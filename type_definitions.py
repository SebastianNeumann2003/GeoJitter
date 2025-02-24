import random
import math
from itertools import pairwise
from typing import Callable
import pickle

import networkx as nx

__all__ = {
    "GeoDistance",
    "LocalityObfuscatingNet"
}


# Unnecessary, see geopy package, which does this but better
class GeoDistance:
    """
    A data structure which handles all the unit conversions for varying distances. Internally, all are stored in meters and converted on the way out.
    """

    def __init__(self, quantity: float, units: str):
        self.original_quantity = quantity
        self.original_units = units

        match units:
            case "km":
                self._meters = 1000 * quantity
            case _:
                self._meters = 0
        # TODO: Make more of these

    def meters(self):
        return self._meters

    def feet(self):
        return self._meters * 3.28084

    def kilometers(self):
        return self._meters / 1000

    def degrees_lat(self):
        return self._meters / 110574  # Approximate

    def degrees_long(self, starting_long):
        return self._meters / (111320 * math.cos(starting_long / 90 * math.pi))


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
        long = random.random(self.left_long, self.right_long)
        lat = random.random(self.bottom_lat, self.top_lat)
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
            self.generate_coords()

    def generate_coords(self):
        for point in self.graph.nodes:
            region = self.regions[self.accessor(point)]

            bounding_box = BoundingBox(region.coordinates)
            new_point = bounding_box.get_random_point()
            while not self.point_in_polygon(*new_point, region):
                new_point = bounding_box.get_random_point()

    def point_in_polygon(self, long: float, lat: float, geometry) -> bool:
        bounding_box = BoundingBox(geometry.coordinates)
        if not bounding_box.point_inside((long, lat)):
            return False

        edges = list(pairwise(geometry.coordinates)).append((geometry.coordinates[-1], geometry.coordinates[0]))
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
