import pickle

import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
import shapely

from type_definitions import LocalityObfuscatingNet

with open("./data_vault/test_network1.pkl", "rb") as f:
    job_network: nx.Graph = pickle.load(f)

regions: gpd.GeoDataFrame = gpd.read_file(".\\data_vault\\Boston_Neighborhood_Boundaries_Approximated_by_2020_Census_Tracts.shp").get(['neighborho', 'geometry'])

quick_ref: dict[str, shapely.Polygon] = dict(zip(regions["neighborho"], regions["geometry"]))
print(type(list(quick_ref.values())[0]))


def point_to_neighborhood(point):
    return job_network.nodes[point]["neighborhood"]


geo_network = LocalityObfuscatingNet(regions=quick_ref, network=job_network, accessor=point_to_neighborhood, graph_has_coords=False)

obfuscated_network = geo_network.graph

pos = {node: (data['long'], data['lat']) for node, data in obfuscated_network.nodes(data=True)}
print(pos)

fig, ax = plt.subplots(figsize=(10, 10))

# Step 3: Plot the regions (GeoDataFrame)
regions.plot(ax=ax, color="lightgray", edgecolor="black", alpha=0.5)  # Neighborhood polygons

# Step 4: Draw the graph on top
nx.draw(obfuscated_network, pos, ax=ax, node_size=50, edge_color="blue", node_color="red", with_labels=True, font_size=8)

# Step 5: Customize and show
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("NetworkX Graph Over Neighborhood Regions")
plt.show()
