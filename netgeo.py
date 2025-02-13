import pickle

import networkx
import fiona

from type_definitions import LocalityObfuscatingNet


def load_regions_from_files(region_files: list[str]) -> list[fiona.Feature]:
    """
    Reads each file provided and convertes them into a single fiona Collection. The files can be ESRI shapefiles or GeoJSON files.
    Inputs:
        region_files (list[str]): The filesnames for each of the regions. The files are opened one at a time, so this list can have a mix of shapefiles and GeoJSON files.
    Outputs:
        A fiona Collection with each region represented as a fiona Geometry internally.
    Raises:
        Any errors fiona has in reading the file are passed up to the caller
    """
    features = list()
    for filename in region_files:
        features.append(list(fiona.open(filename)))
    return features


def load_network_file(network_file: str) -> networkx.Graph:
    """
    Reads a file containing a pickled networkx Graph, unpickles it, and returns the resulting object.
    Inputs:
        network_file (str): The filename of the file containing the pickled graph
    Outputs:
        The unpickled networkx Graph
    Raises:
        If the file is not a pickled networkx Graph, raises a ValueError. Any errors in the unpickling process are also passed up to the caller.
    """
    with open(network_file, "r") as f:
        graph = pickle.loads(f.read())

    if not isinstance(graph, networkx.Graph):
        raise ValueError(f"Object specified in {network_file} could be read, but was not a NetworkX Graph")

    return graph


def load_all(region_files: list[str], network_file: str) -> LocalityObfuscatingNet:
    """
    Combines load_regions_from_files and load_network_file calls and calls the LocalityObfuscatingNet constructor with the resulting files, returning the LON
    Inputs:
        region_files (list[str]): The list of filenames of each region. See load_regions_from_files()
        network_file (str): The filename of the network pickle. See load_network_file()
    Outputs:
        A LocalityObfuscatingNet with the loaded data added via the constructor
    Raises:
        If anything goes wrong during the reading or deserialization process, the error is passed up to the caller.
    """
    regions = load_regions_from_files(region_files)
    network = load_network_file(network_file)

    return LocalityObfuscatingNet(regions=regions, network=network)


if __name__ == "__main__":
    print("Hello, measurable world!")
