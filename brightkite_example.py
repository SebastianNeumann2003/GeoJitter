import time

t = time.time()

import pickle
from typing import Hashable

from networkx import Graph, draw
from geopandas import GeoDataFrame, read_file, GeoSeries, list_layers
from shapely import Point, Polygon
import matplotlib.pyplot as plt
from contextily import add_basemap, providers

import geojitter as gj

nt = time.time()
print("Imports", nt - t)

t = time.time()

fig, ax = plt.subplots()

with open("./experiments/data/networks/spatial_graph_brightkite", "rb") as f:
    original_network: Graph = pickle.load(f)
state = read_file("./data_vault/cb_2018_us_state_20m/cb_2018_us_state_20m.shp")
state.crs = "EPSG:4326"
state = state.loc[32, 'geometry']
ax.plot(*state.exterior.xy)

new_network = gj.filter_network_by_region(original_network, state)

regions: GeoSeries = gj.gen_region_grid_rc(new_network, 10, 10)

quick_ref = dict(enumerate(list(regions)))


def point_converter(node: Hashable, data: dict) -> Point:
    return (data["long"], data["lat"])


nt = time.time()
print("Reading:", nt - t)


def region_accessor(node: Hashable) -> Polygon:
    if "region" not in new_network.nodes(data=True)[node]:
        return quick_ref[0]
    else:
        region_name = new_network.nodes(data=True)[node]["region"]
        return quick_ref[region_name]


def time_thinking():
    t = time.time()

    jittered_network = gj.obfuscated_network(
        regions=regions,
        network=new_network,
        region_accessor=region_accessor,
        point_converter=point_converter,
        strategy=gj.rand_point_in_region(max_iter=100)
    )
    print(gj.wasserstein(new_network, jittered_network))
    display_df = GeoDataFrame(geometry=regions)
    display_df.crs = "EPSG:4326"
    gj.display(display_df, jittered_network, ax=ax)

    nt = time.time()
    return nt - t


if __name__== "__main__":
    # results = []
    # for _ in range(1000):
    #     results.append(time_thinking())
    #
    # print("Mean:", sum(results) / len(results))
    time_thinking()
    plt.show()
