import fiona
import networkx

import random
import math
from itertools import pairwise

__all__ = {
    "GeoDistance",
    "Netwielder"
}


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

    def point_inside(self, point: tuple[float, float]) -> bool:
        return (self.bottom_lat < point[0] < self.top_lat) and (self.left_long < point[1] < self.right_long)


class Netwielder:
    """
    The manager class that wields both the geometry and network files after they are linked. Contains all the functionality that requires both files to be present.
    """

    def __init__(self, shapes: fiona.Collection, network: networkx.Graph, node_info: dict):
        """
        By the time this class gets initialized, the geometry and graph have already been parsed by their respective libraries and turned into a common data structure.
        """
        self.shapes = shapes
        self.graph = network
        self.nodes = node_info

    def point_in_polygon(self, long: float, lat: float, geometry: fiona.Geometry) -> bool:
        assert isinstance(geometry, fiona.Geometry), "Provided geometry variable cannot be interpreted as a Geometry"
        assert geometry.type == "Polygon", "Provided geometry is of valid type, but not a Polygon"

        bounding_box = BoundingBox(geometry.coordinates)
        if not bounding_box.point_inside((long, lat)):
            return False

        edges = list(pairwise(geometry.coordinates)).append((geometry.coordinates[-1], geometry.coordinates[0]))
        relevant_edges = [edge for edge in edges if (min(edge[0][1], edge[1][1]) < lat < max(edge[0][1], edge[1][1])) and (edge[0][0] > long or edge[1][0] > long)]

        return len(relevant_edges) % 2 == 1

    def ambiguate(self, regions: fiona.Collection, point_data, radius: GeoDistance = None, seed=None):
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

        long = point_data["long"]
        lat = point_data["lat"]
        region_id = point_data["region_id"]
        region = None

        for possible_region in regions:
            if possible_region.get("region_id", "") == region_id:
                region = possible_region

        if region is None:
            raise Exception("Invalid region id")

        # Still doing a naive version for now
        deviation = (radius.meters * random.random(), 2 * math.pi * random.random())

        # TODO: Refine to fit globe-earth conspiracy
        new_coordinate = (long + deviation[0] * math.sin(deviation[1]), lat + deviation[0] * math.cos(deviation[1]))

        return new_coordinate
