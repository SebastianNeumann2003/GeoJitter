from fiona import Geometry
from networkx import Graph

from type_definitions import Netwielder


def link(geo_fn: str, net_fn: str, sh_index_fn: str = None):
    """
    Accepts GeoJSON/Shapefile name and parses it (using Fiona). Then accepts a filename for a valid NetworkX graph storage file (edge list, adjacency list, etc), which we use NetworkX to read. Optionally takes a .shx file which indexes the shapefile (the geo file must be .shp if a .shx file is provided)
    """
    # Some parsing
    geometry: Geometry = None  # placeholder
    network: Graph = None  # placeholder

    return Netwielder(geometry, network)
