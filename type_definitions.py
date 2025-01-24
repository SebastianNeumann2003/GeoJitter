from functools import reduce

__all__ = {
    "Coordinate",
    "GeoPolygon"
}

type Coordinate = list[float]


class GeoPolygon:
    def __init__(self, points: list[Coordinate] | list[list[Coordinate]]) -> None:
        self.is_complex = isinstance(points[0][0], Coordinate)  # Does this polygon have hole(s)

        # Verify validity
        pass

        self.points = points


def is_valid_coord(coord: Coordinate) -> bool:
    return isinstance(coord, Coordinate) and len(coord) == 2
