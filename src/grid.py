from dataclasses import dataclass, field
from typing import Any

from .shapes import Shape
from .utils.color import Color
from .utils.geometry import Angle
from .utils.searchable import Searchable


@dataclass
class Cell(Searchable):
    """
    Programmative representation of a cell.
    """

    bg_color = None
    "Background colour of the cell."
    content: list[Shape] = field(default_factory=list, repr=False)
    "Content of the cell."
    orientation: Angle | None = None
    "Global orientation of the content of the cell."


@dataclass
class GridConfig(Searchable):
    """
    Global configuration of the grid.
    """

    bg_color: Color = Color(1, 1, 1, 0)
    "Color of the background."
    border_color: Color = Color("#000000")
    "Color of the grid border."
    border_width: int = 1
    "Border width (in px)."
    cell_size: int = 16
    "Size of the grid cells (in pixels)."
    shapes_fill: Color = Color("#FF0000")
    "Default colour of the objects in the grid."


@dataclass
class Grid:
    """
    Programmative representation of a grid.
    """

    content: list[list[Cell]] = field(default_factory=list)
    "Content of the grid, 2D array of Cells."
    cfg: GridConfig | None = None
    "Configuration of the grid."

    def __post_init__(self):
        if self.cfg is None:
            self.cfg = GridConfig()

    def cell(self, col: int, row: int) -> Cell:
        return self.content[row][col]
