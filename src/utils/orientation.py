from dataclasses import dataclass
from enum import Enum


from .symbols import OrientationSymbol


@dataclass
class Orientation:

    shortcut:OrientationSymbol
    rotation:int


ORIENTATIONS: list[Orientation] = [
    Orientation(OrientationSymbol.BOTTOM, 90),
    Orientation(OrientationSymbol.DIAG_BOTTOM_LEFT, 135),
    Orientation(OrientationSymbol.DIAG_BOTTOM_RIGHT, 45),
    Orientation(OrientationSymbol.DIAG_TOP_LEFT, 225),
    Orientation(OrientationSymbol.DIAG_TOP_RIGHT, 315),
    Orientation(OrientationSymbol.LEFT, 180),
    Orientation(OrientationSymbol.RIGHT, 0),
    Orientation(OrientationSymbol.TOP, 270),
]
