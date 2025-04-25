from pathlib import Path
import pickle
from typing import Hashable
from datetime import datetime

import networkx as nx
import geopandas as gp
import shapely as shp
import matplotlib.pyplot as plt

import geojitter as gj

with open("./experiments/data/networks/spatial_graph_brightkite", "rb") as f:
    big_network: nx.Graph = pickle.load(f)

all_states = gp.read_file("./data_vault/cb_2023_us_state_20m/cb_2023_us_state_20m.shp").get(['STATEFP', 'NAME', 'geometry'])
all_states.crs = "EPSG:4326"

counties = gp.read_file("./data_vault/cb_2023_us_county_20m/cb_2023_us_county_20m.shp")
counties.crs = "EPSG:4326"

output_path = "./trial_outputs/" + datetime.now().strftime("%d%b%Y - %H%M%S")
Path(output_path).mkdir(parents=True, exist_ok=True)


def point_converter(node: Hashable, data: dict) -> tuple[float, float]:
    return (data['long'], data['lat'])


trial_states = ['California', 'Texas', 'Florida', 'Missouri', 'Massachusetts', 'Maryland']
iterations_per_state = 25

for trial_state in trial_states:
    fig, ax = plt.subplots(2, 3)

    def region_accessor_tile(node: Hashable) -> shp.Polygon:
        if "region" not in focused_network_tile.nodes(data=True)[node]:
            return tiled_regions[0]
        else:
            region_name = focused_network_tile.nodes(data=True)[node]["region"]
            return tiled_regions[region_name]

    def region_accessor_counties(node: Hashable) -> shp.Polygon:
        data = focused_network_counties.nodes(data=True)[node]

        if "region" not in data:
            for index, region_entry in counties_regions.iterrows():
                region = region_entry['geometry']
                if region.contains(shp.Point(data["long"], data["lat"])):
                    return region

        region_name = focused_network_counties.nodes(data=True)[node]["region"]
        return counties_regions.iloc[region_name].loc['geometry']

    state_subdf = all_states.loc[all_states['NAME'] == trial_state, ['STATEFP', 'geometry']]
    fips = state_subdf.iloc[0].iloc[0]
    state_geom = state_subdf.iloc[0].iloc[1]

    by_radii = []
    by_tile = []
    by_region = []

    for trial in range(iterations_per_state):
        start = datetime.now()
        focused_network_tile: nx.Graph = gj.filter_network_by_region(big_network, state_geom)
        focused_network_counties: nx.Graph = focused_network_tile.copy()

        tiled_regions: gp.GeoSeries = gj.gen_region_grid_rc(focused_network_tile, 10, 10)
        counties_regions: gp.GeoDataFrame = counties.loc[counties['STATEFP'] == fips]

        by_radii.append(gj.obfuscated_network(
            regions=None,
            network=focused_network_tile,
            region_accessor=lambda x: x,
            point_converter=point_converter,
            strategy=gj.rand_point_by_radius(0.5),
            fail_graceful=False
        ))

        by_tile.append(gj.obfuscated_network(
            regions=tiled_regions,
            network=focused_network_tile,
            region_accessor=region_accessor_tile,
            point_converter=point_converter,
            strategy=gj.rand_point_in_region(),
            fail_graceful=False
        ))

        by_region.append(gj.obfuscated_network(
            regions=counties_regions,
            network=focused_network_counties,
            region_accessor=region_accessor_counties,
            point_converter=point_converter,
            strategy=gj.rand_point_in_region(),
            fail_graceful=False
        ))
        end = datetime.now()
        print("Single trial time:", str(end - start))

    ax[0, 0].set_title("By radius")
    ax[0, 1].set_title("By tile")
    ax[0, 2].set_title("By county")

    wasserstein_rad = gj.wasserstein(focused_network_tile, by_radii, ax[0, 0])
    ks_rad = gj.kolmogorov_smirnov(focused_network_tile, by_radii)

    wasserstein_tile = gj.wasserstein(focused_network_tile, by_tile, ax[0, 1])
    ks_tile = gj.kolmogorov_smirnov(focused_network_tile, by_tile)

    wasserstein_region = gj.wasserstein(focused_network_counties, by_region, ax[0, 2])
    ks_region = gj.kolmogorov_smirnov(focused_network_counties, by_region)

    ax[0, 0].text(0.2, 0.1, f"Wass. Distance = {wasserstein_rad:.2f}\nKS GoF = {ks_rad}", size='xx-small')
    ax[0, 1].text(0.2, 0.1, f"Wass. Distance = {wasserstein_tile:.2f}\nKS GoF = {ks_tile}", size='xx-small')
    ax[0, 2].text(0.2, 0.1, f"Wass. Distance = {wasserstein_region:.2f}\nKS GoF = {ks_region}", size='xx-small')

    ax[1, 0].boxplot(gj.normal_signed_distance(focused_network_tile, by_radii))
    ax[1, 1].boxplot(gj.normal_signed_distance(focused_network_tile, by_tile))
    ax[1, 2].boxplot(gj.normal_signed_distance(focused_network_counties, by_region))

    plt.suptitle(f"Results: {trial_state}")
    plt.savefig(f"{output_path}/{trial_state}.png")
    plt.close()

    print(trial_state, "is done!")
