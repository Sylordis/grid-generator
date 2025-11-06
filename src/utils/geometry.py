from __future__ import annotations
from enum import StrEnum
from itertools import zip_longest
import math
from typing import Callable, TypeAlias


class Vector:
    "Vector represents a vector in a variable amount of dimensions."

    def __init__(self, *values, d: int = None):
        """
        Creates new Vector.

        :param values: values of the coordinates of this vector
        :param d: the number of dimensions, creating a vector of d dimensions of 0s, only used if values are None
        """
        if values:
            self.coords = list(values)
        elif d:
            self.coords = [0] * d

    @property
    def x(self):
        "Gets the first vector's component, associated to X axis."
        return self.coords[0]

    @property
    def y(self):
        "Gets the second vector's component, associated to Y axis."
        return self.coords[1]

    @property
    def z(self):
        "Gets the third vector's component, associated to Z."
        return self.coords[2]

    def __add__(self, o):
        npos = self
        if isinstance(o, (int, float)):
            npos = Vector(*[v + o for v in self.coords])
        if isinstance(o, (list, Vector, tuple)):
            npos = Vector(*[a + b for a, b in zip_longest(self.coords, o, fillvalue=0)])
        return npos

    def __and__(self, o):
        npos = self
        if callable(o):
            npos = Vector(*[o(v) for v in self.coords])
        return npos

    def apply(self, converter: Callable[[float], float]) -> Vector:
        """
        Applies a number converter to all Vector of this position.

        :param converter: a converter to apply to both Vector
        :return: a new position where the converter has been applied to both Vector.
        """
        return self.__and__(converter)

    @staticmethod
    def all(value: int | float, length: int = 2) -> Vector:
        """
        Creates a new vector with the same value in all dimensions.

        :param value: value to fill the vector with.
        :param length: dimensions of the vector, default 2.
        """
        if not isinstance(value, (float, int)):
            raise ValueError("Provided value must be a number (int or float)")
        return Vector(*[value] * length)

    def distance(self, p: Vector):
        """
        Calculates the distance between this point and another.

        :param p: the other position to calculate the distance to.
        :return: the distance.
        """
        return math.sqrt(math.pow(p.x - self.x, 2)) + math.sqrt(
            math.pow(p.y - self.y, 2)
        )

    def __eq__(self, o) -> bool:
        if isinstance(o, Vector):
            return all(
                a == b for a, b in zip_longest(self.coords, o.coords, fillvalue=0)
            )
        elif isinstance(o, (list, tuple)):
            return all(a == b for a, b in zip_longest(self.coords, o, fillvalue=0))
        else:
            return False

    def __floordiv__(self, o):
        if isinstance(o, (float, int)):
            return Vector(*[v // o for v in self.coords])
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
        if isinstance(o, (list, Vector, tuple)):
            self.coords = [s + v for s, v in zip_longest(self, o, fillvalue=0)]
        return self

    def __iter__(self):
        yield from self.coords

    def __mul__(self, o):
        if isinstance(o, (float, int)):
            return Vector(*[v * o for v in self.coords])
        else:
            raise ValueError(
                f"Cannot multiply {self.__class__.__name__} with anything other than a number."
            )

    def __neg__(self):
        return Vector(*[-v for v in self.coords])

    def __repr__(self):
        return f"({",".join(map(str, self.coords))})"

    def __sub__(self, o):
        npos = self
        if isinstance(o, (int, float)):
            npos = Vector(*[v - o for v in self.coords])
        if isinstance(o, (list, Vector, tuple)):
            npos = Vector(*[a - b for a, b in zip_longest(self.coords, o, fillvalue=0)])
        return npos

    def __truediv__(self, o):
        if isinstance(o, (float, int)):
            return Vector(*[v / o for v in self.coords])
        else:
            raise ValueError(
                f"Cannot divide {self.__class__.__name__} with anything other than a number."
            )


Coordinates: TypeAlias = Vector
Point: TypeAlias = Vector


class AngleMeasurement(StrEnum):
    "Type of angles."

    DEGREES = "degrees"
    RADIANS = "radians"


class Angle:
    """
    Angles and everything in between.
    """

    def __init__(
        self, angle: float, angle_type: AngleMeasurement = AngleMeasurement.DEGREES
    ):
        "Angle in degrees."
        if isinstance(angle, Angle):
            self._angle = angle._angle
        elif angle_type == AngleMeasurement.DEGREES or not angle_type:
            self._angle = angle % 360
        else:
            self._angle = angle * 180 / math.pi

    def __add__(self, o):
        ret = None
        if isinstance(o, (int, float)):
            ret = Angle(self.degrees + o)
        elif isinstance(o, Angle):
            ret = Angle(self.degrees + o.degrees)
        else:
            raise TypeError("Unsupported operand type for +")
        return ret

    def __eq__(self, o):
        equal = False
        if isinstance(o, Angle):
            equal = self._angle == o._angle
        return equal

    def __neg__(self):
        return Angle(-self._angle)

    def __sub__(self, o):
        return self.__add__(-o)

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


def rotate(xy: Vector, angle: Angle) -> Vector:
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
    return Vector(xn, yn)
