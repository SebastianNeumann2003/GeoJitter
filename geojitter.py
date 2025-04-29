import random
from math import pi, cos, sin, sqrt
from typing import Callable
from itertools import pairwise

from networkx import Graph, draw
from geopandas import GeoDataFrame, GeoSeries
from shapely import Polygon, MultiPolygon, Point
import matplotlib.pyplot as plt
import contextily as ctx
import scipy.stats as stat
import numpy as np
import triangle as tri


def obfuscated_network(
        regions: GeoDataFrame,
        network: Graph,
        region_accessor: Callable | None,
        point_converter: Callable,
        strategy: Callable,
        fail_graceful: bool = True
) -> Graph:
    """
    Creates a new network based on given information with the points obfuscated.
    Inputs:
    - regions (geopandas.GeoDataFrame): The collection of regions of interest to the network.
    - network (networkx.Graph): The graph containing all the metadata of the points and how they are connected to one another.
    - region_accessor (Callable): This is a function which, when provided a node on the provided network, return the name of the region that point is contained in. In order for this function to work properly, the returned region names must match the GeoDataFrame provided in the "regions" argument.
    - point_converter (Callable): This is a function which, when provided a node in the provided network, returns a shapely.Point for use in the obfuscation process.
    - strategy (Callable): This is a function which, when provided a shapely.Point and shapely.Polygon (or shapely.MultiPolygon) returns an obfuscated shapely.Point. Alternatively, if the function fails, it should return None.
    - fail_graceful (bool): Default True. If this option is enabled, a failure from the strategy function will remove that node from the network, and the program will continue. These failures will be reported in the log file. If fail_graceful is false, any error raised by the strategy function will halt the program.
    Outputs:
    - new_graph (networkx.Graph): The new graph, with all the original data preserved, but with each node being assigned new latitude and longitude coordinates.
    """
    nodes = {}
    for point, data in network.nodes(data=True):
        nodes[point] = data.copy()
        old_point = point_converter(point, data)

        region = region_accessor(point)

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

    new_graph = Graph()
    for node, data in nodes.items():
        new_graph.add_node(node, **data)

    new_graph.add_edges_from(network.edges(data=True))
    return new_graph


def gen_region_grid_rc(network: Graph, rows: int, cols: int, buffer: float = 0.1, modify_network=True) -> GeoSeries:
    """
    Using points from a network, creates a bounding box surrounding all the points and divides the box into grid squares
    Inputs:
    - network: The graph containing the points. Each node in the graph must have "lat" and "long" properties for geolocation
    - rows: The number of rows in the final collection of regions
    - cols: The number of columns in the final collection of regions
    - buffer (optional): Any extra space to be added around the points, as a percentage above one. Defaults to 0.1, or 10% buffer. No buffer is represented as 0
    - modify_network (optional): If true, modifies the original network so each node on the graph knows which region it is in, using the "region" field. Defaults to true
    Outputs:
    A GeoSeries containing each region's Polygon
    """
    nodes = {node: (data["long"], data["lat"]) for node, data in network.nodes(data=True)}
    min_long = min([x[0] for x in nodes.values()])
    max_long = max([x[0] for x in nodes.values()])
    min_lat = min([x[1] for x in nodes.values()])
    max_lat = max([x[1] for x in nodes.values()])

    lat_buff = buffer*(max_lat - min_lat)
    long_buff = buffer*(max_long - min_long)
    # print("Latitudes", min_lat - lat_buff, max_lat + lat_buff)
    # print("Longitudes", min_long - long_buff, max_long + long_buff)

    lat_pairs = list(pairwise(np.linspace(min_lat - lat_buff, max_lat + lat_buff, rows + 1)))
    long_pairs = list(pairwise(np.linspace(min_long - long_buff, max_long + long_buff, cols + 1)))

    out_regions = []
    for nlong, xlong in long_pairs:
        for nlat, xlat in lat_pairs:
            out_regions.append(
                Polygon(shell=[
                    (nlong, nlat), (nlong, xlat), (xlong, xlat), (xlong, nlat), (nlong, nlat)
                ])
            )

            if modify_network:
                points_in_here = [
                    node for node, data in nodes.items()
                    if nlong <= data[0] < xlong and nlat <= data[1] < xlat
                ]
                for point in points_in_here:
                    network.nodes[point]["region"] = len(out_regions) - 1

    return GeoSeries(data=out_regions)


def gen_region_grid_wh(network: Graph, width: float, height: float, buffer: float = 0.1, modify_network=True) -> GeoSeries:
    """
    Using points from a network, creates a bounding box surrounding all the points and divides the box into grid squares
    Inputs:
    - network: The graph containing the points. Each node in the graph must have "lat" and "long" properties for geolocation
    - width: The width of each tile
    - height: The height of each tile
    - buffer (optional): Any extra space to be added around the points, as a percentage above one. Defaults to 0.1, or 10% buffer. No buffer is represented as 0
    - modify_network (optional): If true, modifies the original network so each node on the graph knows which region it is in, using the "region" field. Defaults to true
    Outputs:
    A GeoSeries containing each region's Polygon
    """
    nodes = {node: (data["long"], data["lat"]) for node, data in network.nodes(data=True)}
    min_long = min([x[0] for x in nodes.values()])
    max_long = max([x[0] for x in nodes.values()])
    min_lat = min([x[1] for x in nodes.values()])
    max_lat = max([x[1] for x in nodes.values()])

    lat_buff = buffer*(max_lat - min_lat)
    long_buff = buffer*(max_long - min_long)
    print("Latitudes", min_lat - lat_buff, max_lat + lat_buff)
    print("Longitudes", min_long - long_buff, max_long + long_buff)

    lat_pairs = list(pairwise(np.arange(min_lat - lat_buff, max_lat + lat_buff, height)))
    long_pairs = list(pairwise(np.arange(min_long, max_long, width)))

    out_regions = []
    for nlong, xlong in long_pairs:
        for nlat, xlat in lat_pairs:
            out_regions.append(
                Polygon(shell=[
                    (nlong, nlat), (nlong, xlat), (xlong, xlat), (xlong, nlat), (nlong, nlat)
                ])
            )

            if modify_network:
                points_in_here = [
                    node for node, data in nodes.items()
                    if nlong <= data[0] < xlong and nlat <= data[1] < xlat
                ]
                for point in points_in_here:
                    network.nodes[point]["region"] = len(out_regions) - 1

    return GeoSeries(data=out_regions)


def filter_network_by_region(network: Graph, raw_region: Polygon | MultiPolygon) -> Graph:
    if raw_region.geom_type == "MultiPolygon":
        regions = [polygon for polygon in raw_region.geoms]
    else:
        regions = [raw_region]

    new_network = Graph()
    for region in regions:
        for node, data in network.nodes(data=True):
            if region.contains(Point(data["long"], data["lat"])):
                new_network.add_node(node)
                for key, value in data.items():
                    new_network.nodes[node][key] = value

        for u, v, data in network.edges(data=True):
            if u in new_network.nodes and v in new_network.nodes:
                new_network.add_edge(u, v)
                for key, value in data.items():
                    new_network.edges[u, v][key] = value

    orphans = list()
    for node in new_network.nodes:
        if len(list(new_network.neighbors(node))) == 0:
            orphans.append(node)

    new_network.remove_nodes_from(orphans)

    return new_network


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
    def _rand_point_in_triangle(triangle):
        a, b, c = triangle
        r1 = random.random()
        r2 = random.random()
        sqrt_r1 = sqrt(r1)
        u = 1 - sqrt_r1
        v = sqrt_r1 * (1 - r2)
        w = sqrt_r1 * r2
        return Point(u*a + v*b + w*c)

    def _triangle_area(a, b, c):
        return 0.5 * np.abs(np.cross(b - a, c - a))

    def point_gen(point: Point, region: Polygon | MultiPolygon) -> Point:
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
            candidate_point = Point(cpx, cpy)

            if focused_region.contains(candidate_point):
                return candidate_point

        # If the loop proceeds past this point, we use the slower solution that is guaranteed to converge

        print("Iterations exceeded. Proceeding to triangulation algorithm")
        coords = np.array(focused_region.exterior.coords)
        segments = [(i, (i+1) % len(coords)) for i in range(len(coords))]

        triangulated = tri.triangulate({"vertices": coords, "segments": segments}, 'q')

        try:
            tris = [triangulated['vertices'][triangle] for triangle in triangulated['triangles']]
        except Exception as e:
            print(triangulated)
            exit(1)
        areas = [_triangle_area(*triangle) for triangle in tris]
        area_sum = sum(areas)
        weights = [a / area_sum for a in areas]

        chosen_tri = random.choices(tris, weights=weights, k=1)[0]
        return _rand_point_in_triangle(chosen_tri)

    return point_gen


def rand_point_by_radius(
    radius: float,
    distribution=stat.uniform
) -> Callable:
    """
    Based on a starting point, returns a random point within the provided radius of the starting point.
    Inputs:
    - starting_point (shapely.Point): The anchor point around which the random point will be generated
    - radius (float): The maximum allowable distance from the start point that a point could be generated
    - distribution (scipy.stats.rv_generic): The distribution function (defaults to a uniform distribution) used to generate the new point.
    Outputs:
    - shapely.Point with the new coordinate, within the specified radius from the starting point
    """
    def point_gen(point, region):
        r = radius * sqrt(distribution.rvs(loc=0, scale=1))
        theta = distribution.rvs(loc=0, scale=2 * pi)

        return Point(point[0] + r*cos(theta), point[1] + r*sin(theta))

    return point_gen


def k_nearest_neighbors(
    k: int,
    network: Graph
) -> Callable:
    if k < 1:
        raise ValueError("Can't do k-nearest neighbors with less than 1 point")

    def point_gen(point: tuple[float, float], region):
        coord = Point(point[0], point[1])

        distances = list()
        needs_sort = False

        for a, data in network.nodes(data=True):
            if len(distances) < k:
                distances.append(coord.distance(Point(data["long"], data["lat"])))
                needs_sort = True
            else:
                if needs_sort:
                    distances.sort()

                new_distance = coord.distance(Point(data["long"], data["lat"]))
                if new_distance < distances[k - 1]:
                    replace_index = 0
                    while new_distance > distances[replace_index]:
                        replace_index += 1

                    distances[replace_index] = new_distance

        # By this point, we have a radius for the k-nearest neighbors
        return rand_point_by_radius(distances[k - 1])(point, None)

    return point_gen


def display(regions: GeoDataFrame, network: Graph, title: str = None, ax=None) -> None:
    """
    Overlays a collection of regions and a network over a world map, then displays the plot.
    Inputs:
    - regions (geopandas.GeoDataFrame): The collection of regions to be shown on the overlay
    - network (networkx.Graph): The graph that will be displayed on top of the region plot
    - title (str): If provided, the title of the plot that will be displayed above the image.
    Outpus: None
    Side Effects: A pop-up window will open with the completed plot displayed. Code execution will continue while the pop-up window is open, but the program will not exit until all pop-up windows are closed.
    """
    pos={node: (data['long'], data['lat']) for node, data in network.nodes(data=True)}

    if ax is None:
        fig, ax=plt.subplots(figsize=(10, 10))

    regions.plot(ax=ax, color="lightgray", edgecolor="black", alpha=0.5)
    draw(network, pos, ax=ax, node_size=500 / len(network.nodes), edge_color="blue", node_color="red", with_labels=False)
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs=regions.crs)

    plt.title(title)
    plt.show()


def wasserstein(old_network: Graph, new_networks: list[Graph], ax=None) -> float:
    old_edge_distances=[]
    for u, v in old_network.edges:
        upos=(old_network.nodes[u]["long"], old_network.nodes[u]["lat"])
        vpos=(old_network.nodes[v]["long"], old_network.nodes[v]["lat"])

        old_edge_distances.append(sqrt((upos[0] - vpos[0])**2 + (upos[1]-vpos[1])**2))
    old_span=max(old_edge_distances) - min(old_edge_distances)
    old_edge_distances=[(x - min(old_edge_distances)) / old_span for x in old_edge_distances]

    sorted_old=np.sort(old_edge_distances)
    cdf1=np.arange(1, len(sorted_old) + 1) / len(sorted_old)

    new_cdfs=[]
    for new_network in new_networks:
        new_edge_distances=[]
        for u, v in new_network.edges:
            upos=(new_network.nodes[u]["long"], new_network.nodes[u]["lat"])
            vpos=(new_network.nodes[v]["long"], new_network.nodes[v]["lat"])

            new_edge_distances.append(sqrt((upos[0] - vpos[0])**2 + (upos[1]-vpos[1])**2))
        new_span=max(new_edge_distances) - min(new_edge_distances)
        new_edge_distances=[(x - min(new_edge_distances)) / new_span for x in new_edge_distances]

        sorted_new=np.sort(new_edge_distances)

        new_cdfs.append(np.arange(1, len(sorted_new) + 1) / len(sorted_new))

    avg_new_cdf=np.mean(np.array(new_cdfs), axis=0)
    if ax is not None:
        ax.step(sorted_old, cdf1)
        ax.step(sorted_new, avg_new_cdf)

    return stat.wasserstein_distance(old_edge_distances, new_edge_distances)


def kolmogorov_smirnov(old_network: Graph, new_networks: list[Graph]) -> float:
    old_edge_distances=[]
    for u, v in old_network.edges:
        upos=(old_network.nodes[u]["long"], old_network.nodes[u]["lat"])
        vpos=(old_network.nodes[v]["long"], old_network.nodes[v]["lat"])

        old_edge_distances.append(sqrt((upos[0] - vpos[0])**2 + (upos[1]-vpos[1])**2))
    old_span=max(old_edge_distances) - min(old_edge_distances)
    old_edge_distances=[(x - min(old_edge_distances)) / old_span for x in old_edge_distances]

    all_new_edge_distances=[]
    for new_network in new_networks:
        new_edge_distances=[]
        for u, v in new_network.edges:
            upos=(new_network.nodes[u]["long"], new_network.nodes[u]["lat"])
            vpos=(new_network.nodes[v]["long"], new_network.nodes[v]["lat"])

            new_edge_distances.append(sqrt((upos[0] - vpos[0])**2 + (upos[1]-vpos[1])**2))
        new_span=max(new_edge_distances) - min(new_edge_distances)
        new_edge_distances=[(x - min(new_edge_distances)) / new_span for x in new_edge_distances]

        all_new_edge_distances.extend(new_edge_distances)

    return stat.kstest(old_edge_distances, all_new_edge_distances).statistic


def absolute_distance(old_network: Graph, new_networks: list[Graph]) -> list[float]:
    old_edge_distances=[]
    for u, v in old_network.edges:
        upos=(old_network.nodes[u]["long"], old_network.nodes[u]["lat"])
        vpos=(old_network.nodes[v]["long"], old_network.nodes[v]["lat"])

        old_edge_distances.append(sqrt((upos[0] - vpos[0])**2 + (upos[1]-vpos[1])**2))

    all_new_edge_distances=[]
    for new_network in new_networks:
        new_edge_distances=[]
        for u, v in new_network.edges:
            upos=(new_network.nodes[u]["long"], new_network.nodes[u]["lat"])
            vpos=(new_network.nodes[v]["long"], new_network.nodes[v]["lat"])

            new_edge_distances.append(sqrt((upos[0] - vpos[0])**2 + (upos[1]-vpos[1])**2))
        all_new_edge_distances.append(new_edge_distances)

    averaged_new_edge_distances = np.mean(all_new_edge_distances, axis=0)

    return [abs(x - y) for x, y in zip(old_edge_distances, averaged_new_edge_distances)]


def normal_signed_distance(old_network: Graph, new_networks: list[Graph]) -> list[float]:
    old_edge_distances=[]
    for u, v in old_network.edges:
        upos=(old_network.nodes[u]["long"], old_network.nodes[u]["lat"])
        vpos=(old_network.nodes[v]["long"], old_network.nodes[v]["lat"])

        old_edge_distances.append(sqrt((upos[0] - vpos[0])**2 + (upos[1]-vpos[1])**2))

    all_new_edge_distances=[]
    for new_network in new_networks:
        new_edge_distances=[]
        for u, v in new_network.edges:
            upos=(new_network.nodes[u]["long"], new_network.nodes[u]["lat"])
            vpos=(new_network.nodes[v]["long"], new_network.nodes[v]["lat"])

            new_edge_distances.append(sqrt((upos[0] - vpos[0])**2 + (upos[1]-vpos[1])**2))
        all_new_edge_distances.append(new_edge_distances)

    averaged_new_edge_distances = np.mean(all_new_edge_distances, axis=0)

    return [x - y for x, y in zip(old_edge_distances, averaged_new_edge_distances)]


if __name__ == "__main__":
    print("Hello, measurable world!")
