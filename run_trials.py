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
    "./data_vault/cb_2023_us_county_500k/cb_2023_us_county_500k.shp")
counties.crs = "EPSG:4326"

output_path = "./trial_outputs/" + "27Nov2025"


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
    knn_time: int


all_trial_states = all_states['NAME'].unique()
iterations_per_state = 50

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
            state_results_dir = output_path + f"{'bk' if i == 1 else 'gw'}/{trial_state}/"
            Path(state_results_dir).mkdir(parents=True, exist_ok=True)

            def region_accessor_tile(node: Hashable) -> shp.Polygon:
                data = focused_network_tile.nodes[node]
                if "region" not in data:
                    return tiled_regions[0]
                else:
                    region_name = focused_network_tile.nodes[node]["region"]
                    return tiled_regions[region_name]

            state_subdf = all_states.loc[all_states['NAME'] == trial_state, [
                'STATEFP', 'geometry']]
            fips = state_subdf.iloc[0].iloc[0]
            state_geom = state_subdf.iloc[0].iloc[1]

            by_radii = []
            by_tile = []
            by_region = []
            by_knn = []

            counties_regions: gp.GeoDataFrame = counties.loc[counties['STATEFP'] == fips]
            avg_area = np.mean(
                [county.area for county in counties_regions['geometry']])
            trial_radius = sqrt(avg_area / (2*pi))
            trial_side_length = sqrt(avg_area)

            # Remove after uncommenting below
            focused_network_radius: nx.Graph = gj.filter_network_by_region(dataset, state_geom)
            add_weights(focused_network_radius)
            focused_network_tile: nx.Graph = focused_network_radius.copy()
            add_weights(focused_network_tile)
            focused_network_region: nx.Graph = focused_network_tile.copy()
            add_weights(focused_network_region)
            focused_network_knn: nx.Graph = focused_network_tile.copy()
            add_weights(focused_network_knn)

            for trial in range(iterations_per_state):
                trial_start = datetime.now()

                Path(state_results_dir + "radius/").mkdir(parents=True, exist_ok=True)
                Path(state_results_dir + "tile/").mkdir(parents=True, exist_ok=True)
                Path(state_results_dir + "region/").mkdir(parents=True, exist_ok=True)
                Path(state_results_dir + "knn/").mkdir(parents=True, exist_ok=True)
                Path(state_results_dir + "analytics/").mkdir(parents=True, exist_ok=True)

                rad_original_path = Path(state_results_dir + "radius/original_network.pkl")
                tile_original_path = Path(state_results_dir + "tile/original_network.pkl")
                region_original_path = Path(state_results_dir + "region/original_network.pkl")
                knn_original_path = Path(state_results_dir + "knn/original_network.pkl")

                if not rad_original_path.is_file():
                    with rad_original_path.open("wb+") as f:
                        pickle.dump(focused_network_tile, f)
                if not tile_original_path.is_file():
                    with tile_original_path.open("wb+") as f:
                        pickle.dump(focused_network_tile, f)
                if not region_original_path.is_file():
                    with region_original_path.open("wb+") as f:
                        pickle.dump(focused_network_region, f)
                if not knn_original_path.is_file():
                    with knn_original_path.open("wb+") as f:
                        pickle.dump(focused_network_knn, f)

                tiled_regions: gp.GeoSeries = gj.gen_region_grid_wh(focused_network_tile, trial_side_length, trial_side_length)

                current_time = datetime.now()
                overhead = (current_time - trial_start) / timedelta(microseconds=1)

                output_file = Path(state_results_dir + f"radius/jittered_network_{trial}.pkl")

                if not output_file.is_file():
                    by_radii.append(gj.obfuscated_network(
                        regions=None,
                        network=focused_network_tile,
                        region_accessor=lambda x: x,
                        point_converter=point_converter,
                        strategy=gj.rand_point_by_radius(trial_radius),
                        fail_graceful=False
                    ))
                    add_weights(by_radii[-1])

                    with output_file.open("wb+") as f:
                        pickle.dump(by_radii[-1], f)

                radii_time = (datetime.now() - current_time) / timedelta(microseconds=1)

                current_time = datetime.now()

                output_file = Path(state_results_dir + f"tile/jittered_network_{trial}.pkl")

                if not output_file.is_file():
                    try:
                        by_tile.append(gj.obfuscated_network(
                            regions=tiled_regions,
                            network=focused_network_tile,
                            region_accessor=region_accessor_tile,
                            point_converter=point_converter,
                            strategy=gj.rand_point_in_region(),
                            fail_graceful=False
                        ))
                        add_weights(by_tile[-1])

                        with output_file.open("wb+") as f:
                            pickle.dump(by_tile[-1], f)
                    except Exception as e:
                        continue

                tile_time = (datetime.now() - current_time) / timedelta(microseconds=1)

                current_time = datetime.now()

                output_file = Path(state_results_dir + f"knn/jittered_network_{trial}.pkl")

                if not output_file.is_file():
                    by_knn.append(gj.obfuscated_network(
                        regions=counties_regions,
                        network=focused_network_knn,
                        region_accessor=lambda x: None,  # Unused
                        point_converter=point_converter,
                        strategy=gj.k_nearest_neighbors(10, focused_network_knn),
                        fail_graceful=False
                    ))
                    add_weights(by_knn[-1])

                    with output_file.open("wb+") as f:
                        pickle.dump(by_knn[-1], f)

                knn_time = (datetime.now() - current_time) / timedelta(microseconds=1)
                current_time = datetime.now()

                def region_accessor_counties(node: Hashable) -> shp.Polygon:
                    data = focused_network_region.nodes[node]

                    if "region" not in data:
                        for index, region_entry in counties_regions.iterrows():
                            region = region_entry['geometry']
                            if region.contains(shp.Point(data["long"], data["lat"])):
                                return region
                        return None

                    region_name = focused_network_region.nodes[node]["region"]
                    return counties_regions.iloc[region_name].loc['geometry']

                output_file = Path(state_results_dir + f"region/jittered_network_{trial}.pkl")

                if not output_file.is_file():
                    by_region.append(gj.obfuscated_network(
                        regions=counties_regions,
                        network=focused_network_region,
                        region_accessor=region_accessor_counties,
                        point_converter=point_converter,
                        strategy=gj.rand_point_in_region(max_iter=1000000),
                        fail_graceful=True
                    ))
                    add_weights(by_region[-1])

                    with output_file.open("wb+") as f:
                        pickle.dump(by_region[-1], f)

                region_time = (datetime.now() - current_time) / timedelta(microseconds=1)

                this_trial_analytics = asdict(TrialAnalytics(
                    dataset=i,
                    state=j,
                    trial_n=trial,
                    overhead_time=overhead,
                    radii_time=radii_time,
                    tile_time=tile_time,
                    region_time=region_time,
                    knn_time=knn_time
                ))
                output_file = Path(state_results_dir + f"analytics/trial_analytics_{trial}.pkl")

                if not output_file.is_file():
                    with output_file.open("wb+") as f:
                        pickle.dump(this_trial_analytics, f)

                trial_analytics.append(this_trial_analytics)

            print(trial_state, "is done")


test_states(all_trial_states)

print("All complete!")


trial_analytics_df = pd.DataFrame(trial_analytics)
trial_analytics_df.to_csv(f"{output_path}/trial_analytics.csv", columns=trial_analytics.columns.tolist())
trial_analytics_df.to_pickle("./just_in_case.pkl")
