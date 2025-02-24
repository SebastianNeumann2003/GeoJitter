import pickle

import geopandas as gpd

from type_definitions import LocalityObfuscatingNet

with open("./data_vault/test_network1.pkl", "rb") as f:
    job_network = pickle.load(f)

for e, datadict in job_network.nodes.items():
    print(e, datadict)
print()

regions: gpd.GeoDataFrame = gpd.read_file(".\\data_vault\\Boston_Neighborhood_Boundaries_Approximated_by_2020_Census_Tracts.shp").get(['neighborho', 'geometry'])
print(list(regions.columns))

quick_ref = {}
for name, geom in regions.items():
    quick_ref[name] = geom


def translate_fn(point):
    return job_network.keys()[point].data("neighborhood")


# job_network = netgeo.dereference(keyed_network=job_network, data=points_dict)
# Potential alternative to a contiguous pickled graph.

geo_network = LocalityObfuscatingNet(regions=regions, network=job_network, accessor=lambda point_id: translate_fn(point_id))

obfuscated_network = geo_network.ambiguate_coordinates(10)
