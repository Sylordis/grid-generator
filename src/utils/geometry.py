from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
import math
from typing import Callable


from .symbols import OrientationSymbol


@dataclass
class Position:

    x: float
    y: float

    def __add__(self, o):
        npos = self
        if isinstance(o, int) or isinstance(o, float):
            npos = Position(self.x + o, self.y + o)
        if isinstance(o, Position):
            npos = Position(self.x + o.x, self.y + o.y)
        if isinstance(o, tuple) or isinstance(o, list):
            npos = Position(self.x + o[0], self.y + o[1])
        return npos

    def __and__(self, o):
        if callable(o):
            x = o(x)
            y = o(y)
        return self

    def distance(self, p: Position):
        """
        Calculates the distance between this point and another.

        :param p: the other position to calculate the distance to.
        :return: the distance.
        """
        return math.sqrt(math.pow(p.x - self.x, 2)) + math.sqrt(
            math.pow(p.y - self.y, 2)
        )

    def __getitem__(self, items):
        ret = None
        values = [self.x, self.y]
        if isinstance(items, int) or isinstance(items, slice):
            ret = values[items]
        return ret

    def __iadd__(self, o):
        if isinstance(o, int) or isinstance(o, float):
            self.x += o
            self.y += o
        if isinstance(o, Position):
            self.x += o.x
            self.y += o.y
        if isinstance(o, tuple):
            self.x += o[0]
            self.y += o[1]

    def __iter__(self):
        yield self.x
        yield self.y

    def __mul__(self, o):
        npos = self
        if isinstance(o, int) or isinstance(o, float):
            npos = Position(self.x * o, self.y * o)
        else:
            raise ValueError(
                f"Cannot multiply {self.__class__.__name__} with anything other than a number."
            )
        return npos

    def __neg__(self):
        return Position(-self.x, -self.y)

    def __repr__(self):
        return f"({self.x},{self.y})"


class AngleMeasurement(StrEnum):
    DEGREES = "degrees",
    RADIANS = "radians"


class Angle:
    """
    Angles and everything in between.
    """

    def __init__(
        self, angle: float, angle_type: AngleMeasurement = AngleMeasurement.DEGREES
    ):
        "Angle in degrees."
        if angle_type == AngleMeasurement.DEGREES:
            self._angle = angle
        else:
            self._angle = angle * 180 / math.pi
        self._angle = angle % 360

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
    xy: Position, angle: Angle, normaliser: Callable[[float], float] | None = None
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
    if normaliser:
        xn = normaliser(xn)
        yn = normaliser(yn)
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
