from __future__ import annotations
from dataclasses import dataclass
from math import pi, cos, sin


from .symbols import OrientationSymbol


@dataclass
class Orientation:

    shortcut:OrientationSymbol
    _angle_degrees:int
    "Rotation (degrees)"
    _angle_radians: float
    "Rotation (radians) without PI. Use radians()."

    @property
    def radians(self):
        return pi * self._angle_radians

    @property
    def degrees(self):
        return self._angle_degrees
    
    @staticmethod
    def rotate_to(xy: tuple[float,float], direction: Orientation) -> tuple[float,float]:
        x,y = xy
        xn = x * cos(direction.radians) - y * sin(direction.radians)
        yn = x * sin(direction.radians) + y * cos(direction.radians)
        return (xn, yn)


ORIENTATIONS: list[Orientation] = [
    Orientation(OrientationSymbol.BOTTOM, 90, 3/2),
    Orientation(OrientationSymbol.DIAG_BOTTOM_LEFT, 135, 5/4),
    Orientation(OrientationSymbol.DIAG_BOTTOM_RIGHT, 45, 7/4),
    Orientation(OrientationSymbol.DIAG_TOP_LEFT, 225, 3/4),
    Orientation(OrientationSymbol.DIAG_TOP_RIGHT, 315, 1/4),
    Orientation(OrientationSymbol.LEFT, 180, 1.0),
    Orientation(OrientationSymbol.RIGHT, 0, 0.0),
    Orientation(OrientationSymbol.TOP, 270, 1/2),
]
