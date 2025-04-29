from dataclasses import dataclass, asdict
from pathlib import Path
import pickle
from typing import Hashable
from datetime import datetime, timedelta

import networkx as nx
import numpy as np
import geopandas as gp
import pandas as pd
import shapely as shp
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import FuncFormatter

import geojitter as gj

with open("./experiments/data/networks/spatial_graph_brightkite", "rb") as f:
    brightkite: nx.Graph = pickle.load(f)
with open("./experiments/data/networks/spatial_graph_gowalla", "rb") as f:
    gowalla: nx.Graph = pickle.load(f)

all_states = gp.read_file("./data_vault/cb_2023_us_state_20m/cb_2023_us_state_20m.shp").get(['STATEFP', 'NAME', 'geometry'])
all_states.crs = "EPSG:4326"

counties = gp.read_file("./data_vault/cb_2023_us_county_20m/cb_2023_us_county_20m.shp")
counties.crs = "EPSG:4326"

output_path = "./trial_outputs/" + datetime.now().strftime("%d%b%Y - %H%M%S")
Path(output_path).mkdir(parents=True, exist_ok=True)


def point_converter(node: Hashable, data: dict) -> tuple[float, float]:
    return (data['long'], data['lat'])


@dataclass
class TrialAnalytics:
    dataset: int
    state: int
    trial_n: int
    overhead_time: int
    radii_time: int
    tile_time: int
    region_time: int


@dataclass
class StateAnalytics:
    dataset: int
    state: int

    wass_rad: float
    wass_tile: float
    wass_region: float

    ks_rad: float
    ks_tile: float
    ks_region: float

    quartiles_rad: list[float]
    quartiles_tile: list[float]
    quartiles_region: list[float]


trial_states = all_states['NAME'].unique()
iterations_per_state = 1

trial_analytics = list()
state_analytics = list()

for i, dataset in enumerate([brightkite, gowalla]):
    for j, trial_state in enumerate(trial_states):
        fig = plt.figure()
        gs = GridSpec(2, 3, height_ratios=[1, 1])

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
            trial_start = datetime.now()

            focused_network_tile: nx.Graph = gj.filter_network_by_region(dataset, state_geom)
            focused_network_counties: nx.Graph = focused_network_tile.copy()

            tiled_regions: gp.GeoSeries = gj.gen_region_grid_rc(focused_network_tile, 10, 10)
            counties_regions: gp.GeoDataFrame = counties.loc[counties['STATEFP'] == fips]

            current_time = datetime.now()
            overhead = (current_time - trial_start) / timedelta(microseconds=1)

            by_radii.append(gj.obfuscated_network(
                regions=None,
                network=focused_network_tile,
                region_accessor=lambda x: x,
                point_converter=point_converter,
                strategy=gj.rand_point_by_radius(0.5),
                fail_graceful=False
            ))
            radii_time = (datetime.now() - current_time) / timedelta(microseconds=1)
            current_time = datetime.now()

            by_tile.append(gj.obfuscated_network(
                regions=tiled_regions,
                network=focused_network_tile,
                region_accessor=region_accessor_tile,
                point_converter=point_converter,
                strategy=gj.rand_point_in_region(),
                fail_graceful=False
            ))
            tile_time = (datetime.now() - current_time) / timedelta(microseconds=1)
            current_time = datetime.now()

            by_region.append(gj.obfuscated_network(
                regions=counties_regions,
                network=focused_network_counties,
                region_accessor=region_accessor_counties,
                point_converter=point_converter,
                strategy=gj.rand_point_in_region(),
                fail_graceful=False
            ))
            region_time = (datetime.now() - current_time) / timedelta(microseconds=1)

            trial_analytics.append(asdict(TrialAnalytics(
                dataset=i,
                state=j,
                trial_n=trial,
                overhead_time=overhead,
                radii_time=radii_time,
                tile_time=tile_time,
                region_time=region_time
            )))

        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        ax3 = fig.add_subplot(gs[0, 2])
        ax4 = fig.add_subplot(gs[1, :])

        ax1.set_title("By radius")
        ax2.set_title("By tile")
        ax3.set_title("By county")

        wasserstein_rad = gj.wasserstein(focused_network_tile, by_radii, ax1)
        ks_rad = gj.kolmogorov_smirnov(focused_network_tile, by_radii)

        wasserstein_tile = gj.wasserstein(focused_network_tile, by_tile, ax2)
        ks_tile = gj.kolmogorov_smirnov(focused_network_tile, by_tile)

        wasserstein_region = gj.wasserstein(focused_network_counties, by_region, ax3)
        ks_region = gj.kolmogorov_smirnov(focused_network_counties, by_region)

        ax1.text(0.2, 0.1, f"Wass. Distance = {wasserstein_rad:.4f}\nKS GoF = {ks_rad:.4f}", size='xx-small')
        ax2.text(0.2, 0.1, f"Wass. Distance = {wasserstein_tile:.4f}\nKS GoF = {ks_tile:.4f}", size='xx-small')
        ax3.text(0.2, 0.1, f"Wass. Distance = {wasserstein_region:.4f}\nKS GoF = {ks_region:.4f}", size='xx-small')

        box1 = gj.normal_signed_distance(focused_network_tile, by_radii)
        box2 = gj.normal_signed_distance(focused_network_tile, by_tile)
        box3 = gj.normal_signed_distance(focused_network_counties, by_region)

        state_analytics.append(asdict(StateAnalytics(
            dataset=i,
            state=j,
            wass_rad=wasserstein_rad,
            wass_tile=wasserstein_tile,
            wass_region=wasserstein_region,
            ks_rad=ks_rad,
            ks_tile=ks_tile,
            ks_region=ks_region,
            quartiles_rad=np.percentile(box1, [0, 25, 50, 75, 100], method='midpoint'),
            quartiles_tile=np.percentile(box2, [0, 25, 50, 75, 100], method='midpoint'),
            quartiles_region=np.percentile(box3, [0, 25, 50, 75, 100], method='midpoint')
        )))

        ax4.boxplot([box1, box2, box3])
        ax4.set_title("Percentage change to edge length")
        ax4.set_xticklabels(["Radius", "Tile", "County"])
        ax4.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x*100:.0f}%'))

        if i == 0:  # Brightkite
            fig.suptitle(f"Brightkite Results: {trial_state}")
            plt.tight_layout()
            plt.savefig(f"{output_path}/bk-{trial_state}.png")
        elif i == 1:
            fig.suptitle(f"Gowalla Results: {trial_state}")
            plt.tight_layout()
            plt.savefig(f"{output_path}/gw-{trial_state}.png")
        plt.close()

        print(trial_state, "is done!")

analytics_df = pd.DataFrame(trial_analytics)
analytics_df.to_pickle(f"{output_path}/analytics.pkl")
