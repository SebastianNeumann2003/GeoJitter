import fiona as fi

from type_definitions import Coordinate, GeoPolygon


def is_point_in_polygon(
    point: Coordinate,
    polygon: GeoPolygon
) -> bool:
    """
    Determines if a point lies within a geographic polygon. For both inputs, the optional
    elevation field (the third entry in a point array) will be ignored.
    Inputs:
        point (Coordinate): The point in question, in lat-long format
        polygon (GeoPolygon):
            The list of vertices defining a geographic polygon, as seen in the "coordinates"
            field of GeoJSON objects. Supports polygons with holes defined by more than
            one point list.
    Outputs:
        Boolean representing if the point is inside (True) or outside (False) the polygon
    Throws:
        TypeError: If either input does not fit the prescribed data format
    """
    if isinstance(polygon[0][0], float):
        # This is a simple polygon (homeomorphic to a disc)
        return False
    elif isinstance(polygon[0][0], list):
        # This is a holey polygon
        return True


def random_point_in_polygon(polygon: GeoPolygon) -> Coordinate:
    """
    Returns a random point within the polygon.
    Inputs:
        polygon (GeoPolygon): The polygon within which a random point will be chosen
    """
    pass
