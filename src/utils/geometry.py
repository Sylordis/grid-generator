from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from itertools import zip_longest
import math
from typing import Callable


from .symbols import OrientationSymbol


class Position:

    def __init__(self, *values):
        self.coords = list(values)

    @property
    def x(self):
        return self.coords[0]

    @property
    def y(self):
        return self.coords[1]

    @property
    def z(self):
        return self.coords[2]

    def __add__(self, o):
        npos = self
        if isinstance(o, (int, float)):
            npos = Position(*[v + o for v in self.coords])
        if isinstance(o, (list, Position, tuple)):
            npos = Position(*[a + b for a, b in zip_longest(self.coords, o.coords, fillvalue=0)])
        return npos

    def __and__(self, o):
        npos = self
        if callable(o):
            npos = Position(*[o(v) for v in self.coords])
        return npos

    def apply(self, converter: Callable[[float],float]) -> Position:
        """
        Applies a number converter to all coordinates of this position.

        :param converter: a converter to apply to both coordinates
        :return: a new position where the converter has been applied to both coordinates.
        """
        return self.__and__(converter)

    @staticmethod
    def all(value, length=2) -> Position:
        if not isinstance(value, (float, int)):
            raise ValueError("Provided value must be a number (int or float)")
        return Position(*[value] * length)

    def distance(self, p: Position):
        """
        Calculates the distance between this point and another.

        :param p: the other position to calculate the distance to.
        :return: the distance.
        """
        return math.sqrt(math.pow(p.x - self.x, 2)) + math.sqrt(
            math.pow(p.y - self.y, 2)
        )

    def __eq__(self, o) -> bool:
        if isinstance(o, Position):
            return all(a == b for a,b in zip_longest(self.coords, o.coords, fillvalue=0))
        elif isinstance(o, (list, tuple)):
            return all(a == b for a,b in zip_longest(self.coords, o, fillvalue=0))
        else:
            return False

    def __floordiv__(self, o):
        if isinstance(o, (float, int)):
            return Position(*[v // o for v in self.coords])
        else:
            raise ValueError(
                f"Cannot divide {self.__class__.__name__} with anything other than a number."
            )

    def __getitem__(self, items):
        ret = None
        if isinstance(items, int) or isinstance(items, slice):
            ret = self.coords[items]
        return ret

    def __iadd__(self, o):
        if isinstance(o, (float, int)):
            self.coords = [v + o for v in self.coords]
        if isinstance(o, (list, Position, tuple)):
            self.coords = [s + v for s,v in zip_longest(self, o, fillvalue=0)]
        return self

    def __iter__(self):
        yield from self.coords

    def __mul__(self, o):
        if isinstance(o, (float, int)):
            return Position(*[v * o for v in self.coords])
        else:
            raise ValueError(
                f"Cannot multiply {self.__class__.__name__} with anything other than a number."
            )

    def __neg__(self):
        return Position(*[-v for v in self.coords])

    def __repr__(self):
        return f"({",".join(map(str, self.coords))})"

    def __sub__(self, o):
        return self.__add__(-o)

    def __truediv__(self, o):
        if isinstance(o, (float, int)):
            return Position(*[v / o for v in self.coords])
        else:
            raise ValueError(
                f"Cannot divide {self.__class__.__name__} with anything other than a number."
            )


class AngleMeasurement(StrEnum):
    DEGREES = ("degrees",)
    RADIANS = "radians"


class Angle:
    """
    Angles and everything in between.
    """

    def __init__(
        self, angle: float, angle_type: AngleMeasurement = AngleMeasurement.DEGREES
    ):
        "Angle in degrees."
        if angle_type == AngleMeasurement.DEGREES or not angle_type:
            self._angle = angle % 360
        else:
            self._angle = angle * 180 / math.pi

    def __eq__(self, o):
        equal = False
        if isinstance(o, Angle):
            equal = self._angle == o._angle
        return equal

    def __neg__(self):
        return Angle(-self._angle)

    def __sub__(self, o):
        return Angle(self._angle - o._angle)

    def __repr__(self):
        return f"{self.degrees}°"

    @property
    def radians(self):
        "Provides the angle in radians."
        return math.pi * self._angle / 180

    @property
    def degrees(self):
        "Provides the angle in degrees."
        return self._angle

    @property
    def degrees_abs(self):
        "Provides the angle in absolute degrees."
        return abs(self._angle)


def rotate(
    xy: Position, angle: Angle
) -> Position:
    """
    Performs a rotation of the given position compared to the origin.

    :param xy: position to rotate
    :param angle: angle to rotate it with (>0 angles are clockwise, <0 are counter-clockwise)
    :param normaliser: operation to perform after calculation on the calculated result to transform the result
    :return: the rotated position
    """
    x, y = xy
    degrees = angle.degrees / 180
    xn = x * math.cos(degrees * math.pi) - y * math.sin(degrees * math.pi)
    yn = x * math.sin(degrees * math.pi) + y * math.cos(degrees * math.pi)
    return Position(xn, yn)


ORIENTATIONS: dict[str, Angle] = {
    OrientationSymbol.BOTTOM: Angle(90),
    OrientationSymbol.DIAG_BOTTOM_LEFT: Angle(135),
    OrientationSymbol.DIAG_BOTTOM_RIGHT: Angle(45),
    OrientationSymbol.DIAG_TOP_LEFT: Angle(225),
    OrientationSymbol.DIAG_TOP_RIGHT: Angle(315),
    OrientationSymbol.LEFT: Angle(180),
    OrientationSymbol.RIGHT: Angle(0),
    OrientationSymbol.TOP: Angle(270),
}
