from colour import Color
from dataclasses import dataclass, field


from .shapes import Shape
from .utils.converters import is_percentile, str_to_number
from .utils.geometry import Angle, Coordinates
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

    bg_color: Color | None = None
    "Color of the background."
    border_color: Color | None = None
    "Color of the grid border."
    border_width: int = 1
    "Border width (in px)."
    cell_size: int = 16
    "Size of the grid cells (in pixels)."
    grid_over_components: bool = True
    "Whether the grid is displayed on top of the components (True, default) or under (False)."

    def __post_init__(self):
        if not self.bg_color:
            self.bg_color = Color("#FFFFFF")
        if not self.border_color:
            self.border_color = Color("#000000")


@dataclass
class ShapesConfig(Searchable):
    """
    Global configuration of the shapes.
    """

    border_color: Color | None = None
    "Color of the grid border."
    border_width: int = 1
    "Default border width."
    fill: Color | None = None
    "Default colour of the objects in the grid."

    def __post_init__(self):
        if not self.border_color:
            self.border_color = Color("#FF0000")
        if not self.fill:
            self.fill = Color("#FF0000")


@dataclass
class Grid:
    """
    Programmative representation of a grid.
    """

    content: list[list[Cell]] = field(default_factory=list)
    "Content of the grid, 2D array of Cells."
    cfg: GridConfig | None = None
    "Configuration of the grid."
    shapes_cfg: ShapesConfig | None = None
    "Default configuration of the shapes."

    def __post_init__(self):
        if not self.cfg:
            self.cfg = GridConfig()
        if not self.shapes_cfg:
            self.shapes_cfg = ShapesConfig()

    def cell(self, col_or_pos: int | Coordinates, row: int = -1) -> Cell | None:
        """
        Gets a cell of the grid. As in arrays, numerotation starts at 0.

        :param col_or_pos: either the column number or an (x,y) coordinate.
        :param row: row number, not used if col_or_pos is a Position.
        :return: the corresponding cell or None if the type of the first parameter is neither int nor Position.
        """
        if isinstance(col_or_pos, int):
            return self.content[row][col_or_pos]
        elif isinstance(col_or_pos, Coordinates):
            return self.content[col_or_pos[1]][col_or_pos[0]]
        else:
            return None

    def calculate_cell_center(self, cell_pos: Coordinates) -> Coordinates:
        """
        Calculates the center of a given cell according to its configuration.

        :param cell_pos: position of the cell in the grid
        :return: a position with the exact center of the cell
        """
        pos = [pos * self.cfg.cell_size + self.cfg.cell_size / 2 for pos in cell_pos]
        return Coordinates(pos[0], pos[1])

    def calculate_size(self, *factors, base=None, default=None) -> float:
        """
        Calculates a size based on multiple factors.
        It will first try to multiply all factors together in provided order.
        It will stop as soon as it hits a non-string and non-percentile factor.
        Then if all factors were just percentile number or under 1, it will try to get the cell size
        and multiply the factors product by the cell size.

        :param factors: all factors to multiply together
        :param base: number to use as base for the calculation (default is 1)
        :param default: default size to provide in case there are no factors provided
        :return: a number
        """
        all_percentiles = True
        value = 1
        if base:
            value *= str_to_number(base)
        orig = value
        for f in factors:
            if f:
                value *= str_to_number(f)
                if not is_percentile(f):
                    all_percentiles = False
                    break
        if orig == value and default:
            value = str_to_number(default)
            all_percentiles = is_percentile(default)
        if all_percentiles:
            value *= self.cfg.cell_size
        return float(value)
