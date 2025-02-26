from dataclasses import dataclass, field


from .shapes import Shape
from .utils.color import Color
from .utils.geometry import Angle, Position
from .utils.layout import Layout
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
    layout: Layout | None = None
    "Layout of the cell."
    orientation: Angle | None = None
    "Global orientation of the content of the cell."

    def __post_init__(self):
        if not self.layout:
            self.layout = Layout()


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
    grid_over_components:bool = True
    "Whether the grid is displayed on top of the components (True, default) or under (False)."
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

    def cell(self, col_or_pos: int|Position, row: int = -1) -> Cell | None:
        """
        Gets a cell of the grid. As in arrays, numerotation starts at 0.

        :param col_or_pos: either the column number or an (x,y) coordinate.
        :param row: row number, not used if col_or_pos is a Position.
        :return: the corresponding cell or None if the type of the first parameter is neither int nor Position.
        """
        if isinstance(col_or_pos, int):
            return self.content[row][col_or_pos]
        elif isinstance(col_or_pos, Position):
            return self.content[col_or_pos[1]][col_or_pos[0]]
        else:
            return None
