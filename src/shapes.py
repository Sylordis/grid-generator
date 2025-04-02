from abc import ABC
from colour import Color
from dataclasses import dataclass
from enum import StrEnum


from .utils.geometry import Angle
from .utils.units import Size


@dataclass
class Shape(ABC):
    border_color: Color | None = None
    border_width: int = 0
    fill: Color | None = None
    height: Size | None = None
    # opacity: float | None = None TODO
    orientation: Angle | None = None
    # stroke_opacity: float | None = None TODO
    width: Size | None = None


class ArrowHeadShape(StrEnum):
    DIAMOND = "diamond"
    INDENT = "indent"
    TRIANGLE = "triangle"


@dataclass
class Arrow(Shape):
    head_size: Size | None = Size("200%")
    stroke_width: Size | None = None # Aesthetics: 1/8 of cell size
    style: ArrowHeadShape | None = ArrowHeadShape.TRIANGLE
    # TODO Choose arrow head position: start, end, start+end


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
