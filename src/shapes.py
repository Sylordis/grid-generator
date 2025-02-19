from abc import ABC
from dataclasses import dataclass
from typing import Any


from .utils.color import Color
from .utils.symbols import OrientationSymbol


@dataclass
class Shape(ABC):
    border_color: Color | None = None
    border_width: int = 0
    fill: Color | None = None
    position: tuple[int, int] | None = None
    height: Any = None
    width: Any = None


@dataclass
class Arrow(Shape):
    orientation: OrientationSymbol | None = None
    width: Any = None


@dataclass
class Circle(Shape):
    pass
