import time

t = time.time()

import pickle
from typing import Hashable

from networkx import Graph
from geopandas import GeoDataFrame, read_file, GeoSeries
from shapely import Point, Polygon
import matplotlib.pyplot as plt
from contextily import add_basemap, providers

import geojitter as gj

nt = time.time()
print("Imports", nt - t)

t = time.time()

with open("./experiments/data/networks/spatial_graph_brightkite", "rb") as f:
    original_network: Graph = pickle.load(f)

regions: GeoSeries = gj.gen_region_grid(original_network, 10, 10)

quick_ref = dict(enumerate(list(regions)))

fig, ax = plt.subplots(figsize=(10, 10))

add_basemap(ax, source=providers.OpenStreetMap.Mapnik, crs=regions.crs)

nt = time.time()
print("Reading:", nt - t)


def region_accessor(node: Hashable) -> Polygon:
    if "region" not in original_network.nodes(data=True)[node]:
        return quick_ref[0]
    else:
        region_name = original_network.nodes(data=True)[node]["region"]
        return quick_ref[region_name]


def point_converter(node: Hashable) -> Point:
    return Point(0, 0)  # Since we are using random points in the region, the output of this function is discarded


def time_thinking():
    t = time.time()

    new_network = gj.obfuscated_network(
        regions=regions,
        network=original_network,
        region_accessor=region_accessor,
        point_converter=point_converter,
        strategy=gj.rand_point_in_region(max_iter=100)
    )
    x = len(new_network)
    # gj.display(regions, new_network)

    nt = time.time()
    return nt - t


if __name__== "__main__":
    results = []
    for _ in range(1000):
        results.append(time_thinking())

    print("Mean:", sum(results) / len(results))
