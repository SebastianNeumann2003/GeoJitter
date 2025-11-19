from dataclasses import dataclass, asdict
from pathlib import Path
import pickle
from typing import Hashable
from datetime import datetime, timedelta
from math import pi, sqrt

import networkx as nx
import numpy as np
import geopandas as gp
import pandas as pd
import shapely as shp

import geojitter as gj

with open("./experiments/data/networks/spatial_graph_brightkite", "rb") as f:
    brightkite: nx.Graph = pickle.load(f)
with open("./experiments/data/networks/spatial_graph_gowalla", "rb") as f:
    gowalla: nx.Graph = pickle.load(f)

all_states = gp.read_file(
    "./data_vault/cb_2023_us_state_20m/cb_2023_us_state_20m.shp").get(['STATEFP', 'NAME', 'geometry'])
all_states.crs = "EPSG:4326"

counties = gp.read_file(
    "./data_vault/cb_2023_us_county_20m/cb_2023_us_county_20m.shp")
counties.crs = "EPSG:4326"

output_path = "./trial_outputs/" + datetime.now().strftime("%d%b%Y - %H%M%S")
Path(output_path).mkdir(parents=True, exist_ok=True)


def point_converter(node: Hashable, data: dict) -> tuple[float, float]:
    return (data['long'], data['lat'])


def dictwise_subtract(left: dict, right: dict) -> dict:
    """
    If a key exists in both dicts, then the resulting dict's value for that key will be left[key] - right[key].
    All other keys are merged into the resulting dict.
    """
    out = right.copy() | left.copy()

    for key, value in right.items():
        if key in left:
            out[key] -= value

    return out


@dataclass
class TrialAnalytics:
    dataset: int
    state: int
    trial_n: int
    overhead_time: int
    radii_time: int
    tile_time: int
    region_time: int


all_trial_states = all_states['NAME'].unique()
iterations_per_state = 1

trial_analytics = list()


def add_weights(G: nx.Graph) -> None:
    for e in G.edges:
        start = e[0]
        end = e[1]

        startx, starty = point_converter(start, G.nodes[start])
        endx, endy = point_converter(end, G.nodes[end])

        G.edges[e]["distance"] = sqrt((endx-startx)**2 + (endy-starty)**2)


def test_states(trial_states: list[str]):
    for i, dataset in enumerate([gowalla, brightkite]):
        for j, trial_state in enumerate(trial_states):
            state_results_dir = output_path + f"/{trial_state}/"
            Path(state_results_dir).mkdir(parents=True, exist_ok=True)

            def region_accessor_tile(node: Hashable) -> shp.Polygon:
                if "region" not in focused_network_tile.nodes(data=True)[node]:
                    return tiled_regions[0]
                else:
                    region_name = focused_network_tile.nodes(data=True)[
                        node]["region"]
                    return tiled_regions[region_name]

            def region_accessor_counties(node: Hashable) -> shp.Polygon:
                data = focused_network_counties.nodes(data=True)[node]

                if "region" not in data:
                    for index, region_entry in counties_regions.iterrows():
                        region = region_entry['geometry']
                        if region.contains(shp.Point(data["long"], data["lat"])):
                            return region

                region_name = focused_network_counties.nodes(data=True)[
                    node]["region"]
                return counties_regions.iloc[region_name].loc['geometry']

            state_subdf = all_states.loc[all_states['NAME'] == trial_state, [
                'STATEFP', 'geometry']]
            fips = state_subdf.iloc[0].iloc[0]
            state_geom = state_subdf.iloc[0].iloc[1]

            by_radii = []
            by_tile = []
            by_region = []

            counties_regions: gp.GeoDataFrame = counties.loc[counties['STATEFP'] == fips]
            avg_area = np.mean(
                [county.area for county in counties_regions['geometry']])
            trial_radius = sqrt(avg_area / (2*pi))
            trial_side_length = sqrt(avg_area)

            for trial in range(iterations_per_state):
                trial_start = datetime.now()

                focused_network_tile: nx.Graph = gj.filter_network_by_region(
                    dataset, state_geom)
                add_weights(focused_network_tile)
                focused_network_counties: nx.Graph = focused_network_tile.copy()
                add_weights(focused_network_counties)

                Path(state_results_dir +
                     "radius/").mkdir(parents=True, exist_ok=True)
                Path(state_results_dir + "tile/").mkdir(parents=True, exist_ok=True)
                Path(state_results_dir +
                     "region/").mkdir(parents=True, exist_ok=True)

                with open(state_results_dir + "radius/original_network.pkl", "wb+") as f:
                    pickle.dump(focused_network_tile, f)
                with open(state_results_dir + "tile/original_network.pkl", "wb+") as f:
                    pickle.dump(focused_network_tile, f)
                with open(state_results_dir + "region/original_network.pkl", "wb+") as f:
                    pickle.dump(focused_network_counties, f)

                tiled_regions: gp.GeoSeries = gj.gen_region_grid_wh(
                    focused_network_tile, trial_side_length, trial_side_length)

                current_time = datetime.now()
                overhead = (current_time - trial_start) / \
                    timedelta(microseconds=1)

                by_radii.append(gj.obfuscated_network(
                    regions=None,
                    network=focused_network_tile,
                    region_accessor=lambda x: x,
                    point_converter=point_converter,
                    strategy=gj.rand_point_by_radius(trial_radius),
                    fail_graceful=False
                ))
                add_weights(by_radii[-1])
                radii_time = (datetime.now() - current_time) / \
                    timedelta(microseconds=1)

                with open(state_results_dir + f"radius/jittered_network_{trial}.pkl", "wb+") as f:
                    pickle.dump(by_radii[-1], f)

                current_time = datetime.now()

                by_tile.append(gj.obfuscated_network(
                    regions=tiled_regions,
                    network=focused_network_tile,
                    region_accessor=region_accessor_tile,
                    point_converter=point_converter,
                    strategy=gj.rand_point_in_region(),
                    fail_graceful=False
                ))
                add_weights(by_tile[-1])
                tile_time = (datetime.now() - current_time) / \
                    timedelta(microseconds=1)

                with open(state_results_dir + f"tile/jittered_network_{trial}.pkl", "wb+") as f:
                    pickle.dump(by_tile[-1], f)

                current_time = datetime.now()

                by_region.append(gj.obfuscated_network(
                    regions=counties_regions,
                    network=focused_network_counties,
                    region_accessor=region_accessor_counties,
                    point_converter=point_converter,
                    strategy=gj.rand_point_in_region(),
                    fail_graceful=True
                ))
                add_weights(by_region[-1])
                region_time = (datetime.now() - current_time) / \
                    timedelta(microseconds=1)

                with open(state_results_dir + f"region/jittered_network_{trial}.pkl", "wb+") as f:
                    pickle.dump(by_region[-1], f)

                trial_analytics.append(asdict(TrialAnalytics(
                    dataset=i,
                    state=j,
                    trial_n=trial,
                    overhead_time=overhead,
                    radii_time=radii_time,
                    tile_time=tile_time,
                    region_time=region_time
                )))

            print(trial_state, "is done!")


test_states(all_trial_states)

print("All complete!")


trial_analytics_df = pd.DataFrame(trial_analytics)
trial_analytics_df.to_pickle(f"{output_path}/trial_analytics.pkl")
