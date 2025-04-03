import time
t = time.time()

import pickle
from typing import Hashable

import geopandas as gpd
import networkx as nx
import shapely as shp

import netgeo as ng
dt = time.time()
print(f"imports {dt - t}")
t = time.time()
print("Time start")
with open("./data_vault/test_network1.pkl", "rb") as f:
    original_network: nx.Graph = pickle.load(f)

regions: gpd.GeoDataFrame = gpd.read_file("./data_vault/Boston_Neighborhood_Boundaries_Approximated_by_2020_Census_Tracts.shp").get(['neighborho', 'geometry'])
quick_ref: dict[str, shp.Polygon] = dict(zip(regions["neighborho"], regions["geometry"]))


def region_accessor(node: Hashable) -> shp.Geometry:
    neighborhood_name = original_network.nodes[node]["neighborhood"]
    return quick_ref[neighborhood_name]


def point_converter(node: Hashable) -> shp.Point:
    return shp.Point(0, 0)  # Since we are using random points in the region, the output of this function is discarded


dt = time.time()
print(f"Load {dt-t}")
t = dt

new_network = ng.obfuscated_network(
    regions=regions,
    network=original_network,
    region_accessor=region_accessor,
    point_converter=point_converter,
    strategy=ng.rand_point_in_region(max_iter=100)
)
dt = time.time()
print("Thinking complete in", dt-t)
t = time.time()

ng.display(regions, new_network, title="New network using refactored bindings!")
dt = time.time()
print("Displaying complete in", dt-t)
