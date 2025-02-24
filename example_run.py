import networkx

from type_definitions import LocalityObfuscatingNetwork
import netgeo

points_dict = {
    "home1": {"long": 123.456, "lat": -33.456, "region": 0},
    "work1": {"long": 123.789, "lat": -33.789, "region": 1},
    "home2": {"long": 124.456, "lat": -34.456, "region": 0},
    "work2": {"long": 124.789, "lat": -34.789, "region": 1}
}
edge_list = [("home1", "work1"), ("work1", "work2"), ("work2", "home2"), ("home3", "work3")]


def translate_fn(name: str) -> dict[str, float | str]:
    # A user-provided function which gives long-lat-region data when fed a name from edgelist
    return {
        "long": points_dict[name]["long"],
        "lat": points_dict[name]["lat"],
        "region": points_dict[name]["region"]
    }


job_network = networkx.Graph()

for node, attributes in points_dict.items():
    job_network.add_node(node, **attributes)

for start, end in edge_list:
    job_network.add_edge(start, end)

region_filenames = ["alpha_county.shp", "bravo_county.shp", "charlie_county.shp"]
regions = netgeo.load_from_files(region_filenames, translator=translate_fn)  # Loads all into single fiona.Collection

# job_network = netgeo.dereference(keyed_network=job_network, data=points_dict)
# Potential alternative to a contiguous pickled graph.

geo_network = LocalityObfuscatingNetwork(regions=regions, network=job_network)

obfuscated_network = geo_network.obfuscate(geo_network)
new_points = obfuscated_network.dump_points()
