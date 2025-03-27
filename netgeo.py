import random
import math
from typing import Callable

import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
import shapely as shp
import contextily as ctx
import scipy.stats as stat


def obfuscated_network(
        regions: gpd.GeoDataFrame,
        network: nx.Graph,
        region_accessor: Callable,
        point_converter: Callable,
        strategy: Callable,
        fail_graceful: bool = True
) -> nx.Graph:
    """
    Creates a new network based on given information with the points obfuscated.
    Inputs:
    - regions (geopandas.GeoDataFrame): The collection of regions of interest to the network.
    - network (networkx.Graph): The graph containing all the metadata of the points and how they are connected to one another.
    - region_accessor (Callable): This is a function which, when provided a node on the provided network, return the name of the region that point is contained in. In order for this function to work properly, the returned region names must match the GeoDataFrame provided in the "regions" argument.
    - point_converter (Callable): This is a function which, when provided a node in the provided network, returns a shapely.Point for use in the obfuscation process.
    - strategy (Callable): This is a function which, when provided a shapely.Point and shapely.Polygon (or shapely.MultiPolygon) returns an obfuscated shapely.Point. Alternatively, if the function fails, it should return None.
    - fail_graceful (bool): Default True. If this option is enabled, the function will continue on if the strategy function fails to return a valid point (i.e. it returns None). However, any exceptoins from within the strategy will not be caught.
    Outputs:
    - new_graph (networkx.Graph): The new graph, with all the original data preserved, but with each node being assigned new latitude and longitude coordinates.
    """
    nodes = {}
    for point, data in network.nodes(data=True):
        nodes[point] = data

        region = region_accessor(point)
        old_point = point_converter(point)

        new_point = strategy(old_point, region)

        if new_point is None:
            if fail_graceful:
                print(f"Unable to obfuscate point {point}. Continuing...")
                nodes[point]["long"] = 0
                nodes[point]["lat"] = 0
            else:
                raise Exception(f"Unable to obfuscate point {point}")
        else:
            nodes[point]["long"] = new_point.x
            nodes[point]["lat"] = new_point.y

    new_graph = nx.Graph()
    for node, data in nodes.items():
        new_graph.add_node(node, **data)

    new_graph.add_edges_from(network.edges(data=True))
    return new_graph


# Will eventually be put in strategies.py
def rand_point_in_region(
        distribution=stat.uniform,
        max_iter: int = 50
) -> Callable:
    """
    Constructs a function which accepts a point and a region, which returns a random point in the region. The provided point is discarded. This is meant to bind into the obfuscate_network function as an available strategy, which is why it needs to be able to accept a point.
    NOTE: This uses a technique known as "Currying" or "Partial Application". If you are unfamiliar, we recommend doing a bit of reading on the topic: https://en.wikipedia.org/wiki/Currying.
    Inputs:
    - distribution (scipy.stats.rv_generic): A probability distribution, which will be used in the returned function to generate a point
    - max_iter (int): Default 50. The number of times the returned function will attempt to find a point in the region provided to it. If it cannot find a point in time, it will return None.
    Outputs:
    - point_gen (Callable[shapely.Point, shapely.Polygon | shapely.MultiPolygon -> shapely.Point]): A function which expects a point and a region, which (when called) outputs a random point in the region.
    """
    def point_gen(point: shp.Point, region: shp.Polygon | shp.MultiPolygon) -> shp.Point:
        if region.geom_type == "MultiPolygon":
            # TODO: It's possible there are better ways to choose the region than this. Will likely modify the behavior of the distribution
            # The first place this comes to mind would be where different sub-polygons have different areas. This would treat them all equally, giving outsized representation to smaller regions
            focused_region = random.choice(region.geoms)
        elif region.geom_type == "Polygon":
            focused_region = region
        else:
            raise TypeError(f"Cannot find a random point in object of type {type(region)}")

        minx, miny, maxx, maxy = focused_region.bounds

        for _ in range(max_iter):
            cpx = distribution.rvs(loc=minx, scale=maxx - minx)
            cpy = distribution.rvs(loc=miny, scale=maxy - miny)
            candidate_point = shp.Point(cpx, cpy)

            if focused_region.contains(candidate_point):
                return candidate_point

        print("Exceeded iterations")
        return None

    return point_gen


def rand_point_by_radius(
    starting_point: shp.Point,
    radius: float,
    distribution=stat.uniform
) -> shp.Point:
    """
    Based on a starting point, returns a random point within the provided radius of the starting point.
    Inputs:
    - starting_point (shapely.Point): The anchor point around which the random point will be generated
    - radius (float): The maximum allowable distance from the start point that a point could be generated
    - distribution (scipy.stats.rv_generic): The distribution function (defaults to a uniform distribution) used to generate the new point.
    Outputs:
    - shapely.Point with the new coordinate, within the specified radius from the starting point
    """
    r = distribution.rvs(loc=0, scale=radius)
    theta = distribution.rvs(loc=0, scale=2 * math.pi)

    return shp.Point(starting_point.x + r*math.cos(theta), starting_point.y + r*math.sin(theta))


def display(regions: gpd.GeoDataFrame, network: nx.Graph, title: str = None) -> None:
    """
    Overlays a collection of regions and a network over a world map, then displays the plot.
    Inputs:
    - regions (geopandas.GeoDataFrame): The collection of regions to be shown on the overlay
    - network (networkx.Graph): The graph that will be displayed on top of the region plot
    - title (str): If provided, the title of the plot that will be displayed above the image.
    Outpus: None
    Side Effects: A pop-up window will open with the completed plot displayed. Code execution will continue while the pop-up window is open, but the program will not exit until all pop-up windows are closed.
    """
    pos = {node: (data['long'], data['lat']) for node, data in network.nodes(data=True)}

    fig, ax = plt.subplots(figsize=(10, 10))

    regions.plot(ax=ax, color="lightgray", edgecolor="black", alpha=0.5)
    nx.draw(network, pos, ax=ax, node_size=50, edge_color="blue", node_color="red", with_labels=True, font_size=8)
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs=regions.crs)

    plt.title(title)
    plt.show()


if __name__ == "__main__":
    print("Hello, measurable world!")
