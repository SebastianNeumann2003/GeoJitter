import random
import math
from itertools import pairwise
from typing import Callable
import pickle

import networkx as nx
import shapely

__all__ = {
    "LocalityObfuscatingNet"
}


class BoundingBox:
    def __init__(self, coords: list[list[float]]):
        """
        Accepts a bunch of coordinates and figures out the smallest rectangle that contains all of them
        """
        longs = [coord[0] for coord in coords]
        lats = [coord[1] for coord in coords]

        self.bottom_left = (min(longs), min(lats))
        self.bottom_right = (max(longs), min(lats))
        self.top_left = (min(longs), max(lats))
        self.top_right = (max(longs), max(lats))

        self.left_long = min(longs)
        self.right_long = max(longs)
        self.top_lat = max(lats)
        self.bottom_lat = min(lats)

    def get_random_point(self):
        long = self.left_long + (self.right_long - self.left_long) * random.random()
        lat = self.bottom_lat + (self.top_lat - self.bottom_lat) * random.random()
        return (long, lat)

    def point_inside(self, point: tuple[float, float]) -> bool:
        return (self.bottom_lat < point[0] < self.top_lat) and (self.left_long < point[1] < self.right_long)


class LocalityObfuscatingNet:
    """
    The manager class that holds both the geometry and network files after they are linked. Contains all the functionality that requires both data structures to be present.
    """

    def __init__(self, network: nx.Graph, accessor: Callable, regions: list, graph_has_coords=True):
        """
        By the time this class gets initialized, the geometry and graph have already been parsed by their respective libraries and turned into a common data structure.
        """
        self.graph = network
        self.accessor = accessor
        self.regions = regions

        if not graph_has_coords:
            self.graph = self.generate_coords()

    def extract_coordinates(self, geometry: shapely.Polygon | shapely.MultiPolygon):
        if geometry.geom_type == "Polygon":
            return list(geometry.exterior.coords)  # Single list of coordinates
        elif geometry.geom_type == "MultiPolygon":
            return list([coord for poly in geometry.geoms for coord in poly.exterior.coords])
        return None  # Handle other cases if needed

    def generate_coords(self) -> nx.Graph:
        new_graph = nx.Graph()
        nodes = {}
        for point in self.graph.nodes:
            region = self.regions[self.accessor(point)]

            bounding_box = BoundingBox(self.extract_coordinates(region))

            new_point = bounding_box.get_random_point()
            i = 0
            while not self.point_in_polygon(*new_point, region) and i < 50:
                new_point = bounding_box.get_random_point()
                i += 1

            if i == 50:
                print("Exceeded iterations")

            nodes[point] = new_point

        for node, data in self.graph.nodes(data=True):
            # Get lat/long from dictionary, or set None if missing
            long, lat = nodes.get(node, (None, None))

            # Copy old attributes and add lat/long
            new_graph.add_node(node, **data, lat=lat, long=long)

        # Copy edges from the original graph
        new_graph.add_edges_from(self.graph.edges(data=True))

        return new_graph

    def point_in_polygon(self, long: float, lat: float, geometry) -> bool:
        coords = self.extract_coordinates(geometry)
        edges = list(pairwise(coords))
        edges.append((coords[-1], coords[0]))
        relevant_edges = [edge for edge in edges if (min(edge[0][1], edge[1][1]) < lat < max(edge[0][1], edge[1][1])) and (edge[0][0] > long or edge[1][0] > long)]

        return len(relevant_edges) % 2 == 1

    def _ambiguate(self, point_id: str | int, radius: float = 0, seed=None):
        """
        Accepts a collection of regions, matches point to region, then ambiguates that point to a random spot in the same region
        Also takes a seed for reproducability.
        We will rely on the user to provide the region files, but I think we should provide a utility to allow them to fetch from the GADM (https://gadm.org/download_country.html)
        The radius is an optional value that allows the user to constrain how far they want the points to vary, on top of staying in the region. If specified, the ambiguated point will still be in the region, but it will be no further from the point than the radius specifies
        """
        if seed is not None:
            random.seed(seed)
        if radius is None:
            radius = GeoDistance(100, "km")

        long = self.accessor(point_id)["long"]
        lat = self.accessor(point_id)["lat"]
        region_id = self.accessor(point_id)["region"]
        region = None

        for possible_region in self.regions:
            if possible_region.get("region_id", "") == region_id:
                region = possible_region

        if region is None:
            # TODO: Maybe we can figure it out ourselves
            raise Exception("Invalid region id")

        # Still doing a naive version for now
        deviation = (radius.meters * random.random(), 2 * math.pi * random.random())

        new_coordinate = (long + deviation[0] * math.sin(deviation[1]), lat + deviation[0] * math.cos(deviation[1]))

        return new_coordinate

    def ambiguate_coordinates(self, radius):
        """
        Public-facing method which ambiguates every point provided in the network, while overwriting the original values.
        """
        for point in self.graph.nodes:
            self._ambiguate(point, radius=10)

    def save_to(self, filename: str) -> str:
        """
        Saves a pickled version of this object to the provided file
        """
        with open(filename, "w") as f:
            f.write(pickle.dumps(self))

    def show(self):
        """
        Using geopandas and matplotlib, creates a static image of all the points and regions included in here.
        Reflects the internal state of the LON (i.e. if the obfuscation has not happened yet, the rendering will show
        the true points)
        """
        nodes = list(self.graph.nodes)

        for node in nodes:
            pass

        for region in self.regions:
            pass
