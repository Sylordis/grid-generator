from dataclasses import dataclass, field

from .shapes import Shape
from .utils.color import Color
from .utils.orientation import Orientation


@dataclass
class Cell:
  """
  Programmative representation of a cell.
  """

  bg_color = None
  "Background colour of the cell."
  content: list[Shape] = field(default_factory=list)
  "Content of the cell."
  orientation: Orientation|None = None
  "Global orientation of the content of the cell."


@dataclass
class GridConfig:
  """
  Global configuration of the grid.
  """

  bg_color: Color = Color(1, 1, 1, 0)
  "Color of the background."
  border_color: Color = Color("#000000")
  "Color of the grid border."
  border_width: int = 1
  "Border width (in px)."
  cell_size: int = 15
  "Size of the grid cells (in pixels)."
  shapes_color: Color = Color("#FF0000")
  "Default colour of the objects in the grid."


@dataclass
class Grid:
  """
  Programmative representation of a grid.
  """
  content: list[list[Cell]] = field(default_factory=list)
  "Content of the grid, 2D array of Cells."