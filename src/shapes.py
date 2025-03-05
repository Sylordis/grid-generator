from abc import ABC
from colour import Color
from dataclasses import dataclass
from typing import Any


from .utils.symbols import OrientationSymbol


@dataclass
class Shape(ABC):
    border_color: Color | None = None
    border_width: int = 0
    fill: Color | None = None
    height: Any = None
    width: Any = None


@dataclass
class Arrow(Shape):
    border_width: int = 1
    head: Any = "150%"
    orientation: OrientationSymbol | None = None
    width: Any = None


@dataclass
class Circle(Shape):
    pass
