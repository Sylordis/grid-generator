from abc import ABC
from colour import Color
from dataclasses import dataclass
from typing import Any


from .utils.geometry import Angle


@dataclass
class Shape(ABC):
    border_color: Color | None = None
    border_width: int = 0
    fill: Color | None = None
    height: Any = None
    # opacity: float | None = None TODO
    orientation: Angle | None = None
    # stroke_opacity: float | None = None TODO
    width: Any = None


@dataclass
class Arrow(Shape):
    head: Any = "150%"


@dataclass
class Circle(Shape):
    """
    Circle shape.

    Properties
    ---
    Width is the radius.
    """

    pass


@dataclass
class Diamond(Shape):
    pass


@dataclass
class Ellipse(Shape):
    """ "
    Ellipse shape.

    Properties
    ---
    :param width: X radius.
    :param height: Y radius.
    """

    pass


class Hexagon(Shape):
    """
    Properties
    ---
    :param width: radius
    """

    pass


@dataclass
class Rectangle(Shape):
    border_radius: int = 0
    _is_square: bool = False


@dataclass
class Star(Shape):
    """
    Properties
    ---
    :param height: internal radius
    :param width: external radius
    """

    sides: int = 5
    "Number of sides (vertices) of the star. Default is 5."


@dataclass
class Triangle(Shape):
    pass
