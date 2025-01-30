from fiona import Geometry
from fiona.collection import Collection
from networkx import Graph

import random

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

        # some parsing business

        self._meters = None

    def meters(self):
        return self._meters

    def feet(self):
        return self._meters * 3.28084

    def kilometers(self):
        return self._meters / 1000

    # etc


class Netwielder:
    """
    The manager class that wields both the geometry and network files after they are linked. Contains all the functionality that requires both files to be present.
    """

    def __init__(self, geometry: Geometry, network: Graph):
        """
        By the time this class gets initialized, the geometry and graph have already been parsed by their respective libraries and turned into a common data structure.
        """
        self.geo = geometry
        self.graph = network

    def ambiguate(self, regions: Collection, radius=None, seed=None):
        """
        Accepts a collection of regions, figures out which region each point is in, then ambiguates that point to a random spot in the same region, while maintaining the properties of the network.
        Regions ideally should not intersect, but if it so happens that a point falls in two regions, the first is chosen as the parent region of that point.
        Also takes a seed for reproducability.
        We will rely on the user to provide the region files, but I think we should provide a utility to allow them to fetch from the GADM (https://gadm.org/download_country.html)
        The radius is an optional value that allows the user to constrain how far they want the points to vary, on top of staying in the region. If specified, the ambiguated point will still be in the region, but it will be no further from the point than the radius specifies
        """
        if seed is not None:
            random.seed(seed)
        pass
