from dataclasses import dataclass
import logging
from pathlib import Path
import re


from .exporters import Exporter, SVGExporter
from .grid import Cell, Grid, GridConfig
from .shape_creator import ShapeCreator
from .utils.symbols import GridSymbol


@dataclass
class DrawToolConfig:
  output_format = "SVG"
  "Color mode for the image."
  dest_dir: Path|None = None
  "Destination directory for created images."

class GridDrawingTool:
  """
  Main class to draw grids and arrows.
  """

  def __init__(self, dist_dir: Path|None = None):
    """
    Creates a new drawing tool.

    :param dist_dir: destination dir for generating the images
    """
    self._log = logging.getLogger()
    self.dist_dir: Path|None = dist_dir
    self._shape_creator = ShapeCreator()

  def draw_all(self, files_str: list[str], cfg: GridConfig = None):
    """
    Tries to draw all provided files.

    :param files_str: list of string paths of files to generate images of
    :param cfg: configuration of the grid
    """
    self._log.debug(f"files: {files_str}")
    files: list[tuple[Path,Path]] = []
    # Check input files and convert
    for file_str in files_str:
      src_file = Path(file_str).resolve()
      if not src_file.exists():
        self._log.warning(f"File '{src_file}' does not exist. Skipping.")
      else:
        dist_file = self.dist_dir if self.dist_dir is not None else src_file.parent
        dist_file = dist_file / f"{src_file.name}"
        dist_file = dist_file.with_suffix(".svg")
        files.append((src_file, dist_file))
    # Draw
    for input, output in files:
      grid_config = GridConfig() if cfg is None else cfg
      self.draw_grid(input, output, grid_config)

  def draw_grid(self, input_file: Path, output_file: Path, cfg: GridConfig):
    """
    Draws a grid from a file.

    :param input_file: input text file
    :param output_file: output image file
    """
    self._log.debug(f"{input_file.resolve()} => {output_file.resolve()}")
    grid = self.parse_grid_file(input_file)
    grid.cfg = cfg
    exporter: Exporter = SVGExporter()
    exporter.export(grid, output_file)
    self._log.info(f"{input_file.name} => {output_file.name}")

  def parse_grid_file(self, input_file: Path) -> Grid:
    """
    Creates an object representation of the grid provided in a file.

    :param input_file: file to read
    :return: a grid object
    """
    with open(input_file, newline='') as grid_file:
      grid:Grid = Grid()
      for line in grid_file:
        line_txt = line.rstrip()
        cells_str = [cell.strip() for cell in line_txt.split(GridSymbol.CELL_SEPARATOR)]
        self._log.debug(cells_str)
        cells = []
        for cell_str in cells_str:
          cell = self.parse_cell(cell_str)
          cells.append(cell)
        grid.content.append(cells)
        self._log.debug(cells)
      return grid

  def parse_cell(self, cell_text: str) -> Cell:
    """
    Parses a cell text to create a Cell and its content.

    :param cell_text: text to parse
    :param cfg: configuration of the grid
    :param cell_position: 
    :return: a cell object
    """
    cell = Cell()
    self._log.debug(f"parsing cell: '{cell_text}'")
    if len(cell_text) > 0:
      pattern = r"(\{[^}]+\})?((\d*)([A-Z][A-Za-z]*)(\{[^}]+\})?)?(;(\d*)([A-Z][A-Za-z]*)(\{[^}]+\})?)*"
      match = re.match(pattern, cell_text)
      if match:
        it = iter(match.groups())
        cell_cfg = next(it)
        if cell_cfg:
          cell_cfg = cell_cfg[1:-1].split(GridSymbol.PARAMS_SEPARATOR)
        while (group:=next(it, None)) is not None:
          self._log.debug(f"group:{group}")
          shapes = self._shape_creator.interpret_and_create_shapes(next(it), next(it), next(it))
          cell.content.extend(shapes)
    return cell
