import fiona
import json

from networkx import Graph

from type_definitions import Netwielder


def link(geo_fn: str, net_fn: str):
    """
    Accepts GeoJSON/Shapefile name and parses it (using Fiona). Then accepts a filename for a valid NetworkX graph storage file (edge list, adjacency list, etc), which we use NetworkX to read. Optionally takes a .shx file which indexes the shapefile (the geo file must be .shp if a .shx file is provided)
    """
    # Some parsing
    colxn_f = fiona.open(geo_fn)
    colxn = list(colxn_f)
    print(colxn_f.driver)

    colxn_f.close()

    with open(net_fn, "rb") as json_f:
        raw_network = json.load(json_f)

    node_info = raw_network["nodes"]
    network = Graph()
    network.add_edges_from(raw_network["edges"])

    return Netwielder(colxn, network, node_info)


if __name__ == "__main__":
    link("./examples/hudson_valley.geojson", "./examples/points.json")
