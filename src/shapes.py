from abc import ABC
from colour import Color
from dataclasses import dataclass
from typing import Any


from .utils.layout import Position


@dataclass
class Shape(ABC):
    border_color: Color | None = None
    border_width: int = 0
    fill: Color | None = None
    height: Any = None
    width: Any = None


@dataclass
class OrientableShape(Shape):
    orientation: Position | None = None


@dataclass
class Arrow(OrientableShape):
    head: Any = "150%"


@dataclass
class Circle(Shape):
    pass


@dataclass
class Rectangle(OrientableShape):
    border_radius: int = 0
