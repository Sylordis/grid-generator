"Main module of the grid-generator for drawing grids."

from dataclasses import dataclass
import logging
from pathlib import Path
import re


from .cfg_parser import CfgParser
from .exporters import Exporter, SVGExporter
from .grid import Cell, Grid, GridConfig
from .shapes import (
    Shape,
    Arrow,
    Circle,
    Diamond,
    Ellipse,
    Hexagon,
    Rectangle,
    Star,
    Text,
    Triangle,
)
from .utils.symbols import GridSymbol, ShapeSymbol


@dataclass
class DrawToolConfig:
    """
    Configuration for the tool.
    """

    dest_dir: Path | None = None
    "Destination directory for created images."
    do_export: bool = True
    "Perform the export if true."
    output_format = "SVG"
    "Color mode for the image."


class GridDrawingTool:
    """
    Main class to draw grids and arrows.
    """

    def __init__(self, cfg=None, grid_cfg=None):
        """
        Creates a new drawing tool.

        :param dist_dir: destination dir for generating the images
        :param grid_cfg: overall grid configuration
        """
        self._log = logging.getLogger()
        "Class logger."
        self.cfg = DrawToolConfig()
        "Drawing tool configuration."
        if cfg:
            self._set_cfg(cfg)
        self.grid_cfg = grid_cfg
        "Overall grid configuration."
        self._cfg_parser = CfgParser()
        "Grid/Cell configuration parser."

    def _set_cfg(self, cfg):
        """
        Sets the configuration.
        """
        if cfg.dest:
            self.cfg.dest_dir = Path(cfg.dest)
        # "do_export" is a boolean
        if "do_export" in cfg:
            self.cfg.do_export = cfg.do_export

    def draw_all(self, files_str: list[str], cfg: GridConfig = None):
        """
        Tries to draw all provided files.

        :param files_str: list of string paths of files to generate images of
        :param cfg: configuration of the grid
        """
        self._log.debug("files: %s", files_str)
        files: list[tuple[Path, Path]] = []
        # Check input files and convert
        for file_str in files_str:
            src_file = Path(file_str).resolve()
            if not src_file.exists():
                self._log.warning("File '%s' does not exist. Skipping.", src_file)
            else:
                dist_file = (
                    self.cfg.dest_dir
                    if self.cfg.dest_dir is not None
                    else src_file.parent
                )
                dist_file = dist_file / f"{src_file.name}"
                dist_file = dist_file.with_suffix(".svg")
                files.append((src_file, dist_file))
        if self.cfg.dest_dir:
            self._log.info("Output dir: %s", self.cfg.dest_dir)
        # Draw
        for input_file, output_file in files:
            grid_config = GridConfig() if cfg is None else cfg
            self.draw_grid(input_file, output_file, grid_config)

    def draw_grid(self, input_file: Path, output_file: Path, cfg: GridConfig):
        """
        Draws a grid from a file.

        :param input_file: input text file
        :param output_file: output image file
        :param cfg: grid configuration
        """
        self._log.debug("%s => %s", input_file.resolve(), output_file.resolve())
        self._log.info("Input: %s", input_file.name)
        grid = self.parse_grid_file(input_file)
        grid.cfg = cfg
        self._log.debug(self.cfg)
        if self.cfg.do_export:
            exporter: Exporter = SVGExporter()
            exporter.export(grid, output_file)
            self._log.info("Output generated: %s", output_file.name)
        else:
            self._log.info("Export was cancelled (--no-export).")

    def parse_grid_file(self, input_file: Path) -> Grid:
        """
        Creates an object representation of the grid provided in a file.

        :param input_file: file to read
        :return: a grid object
        """
        with open(input_file, newline="", encoding="utf-8") as grid_file:
            grid: Grid = Grid()
            for line in grid_file:
                line_txt = line.rstrip()
                cells_str = [
                    cell.strip() for cell in line_txt.split(GridSymbol.CELL_SEPARATOR)
                ]
                self._log.debug("Line: %s", cells_str)
                cells = []
                for cell_str in cells_str:
                    cell = self.parse_cell(cell_str)
                    cells.append(cell)
                grid.content.append(cells)
            return grid

    def parse_cell(self, cell_text: str) -> Cell:
        """
        Parses a cell text to create a Cell and its content.

        :param cell_text: text to parse
        :return: a cell object
        """
        cell = Cell()
        self._log.debug("Parsing cell: '%s'", cell_text)
        if len(cell_text) > 0:
            cell_text_processed = cell_text
            # Matching config
            pattern_cfg = (
                r"^("
                + re.escape(GridSymbol.CFG_START)
                + "[^"
                + GridSymbol.CFG_END
                + "]+"
                + re.escape(GridSymbol.CFG_END)
                + ")"
            )
            match_cfg = re.match(pattern_cfg, cell_text)
            if match_cfg:
                cell_cfg = match_cfg.group(0)
                cell_text_processed = cell_text[len(cell_cfg) :]
                self._log.debug("Config matches: %s, %d", cell_cfg, len(cell_cfg))
                if cell_cfg:
                    cell_cfg = cell_cfg[1:-1].split(GridSymbol.UNIVERSAL_SEPARATOR)
                    cell.update(self._cfg_parser.interpret(cell_cfg))
            # Matching shapes
            self._log.debug("Matching shapes: %s", cell_text_processed)
            pattern = (
                r"((\d*)([A-Z][a-z]*|\"[^\"]+\")("
                + re.escape(GridSymbol.CFG_START)
                + "([^"
                + GridSymbol.CFG_END
                + "]+)"
                + re.escape(GridSymbol.CFG_END)
                + ")?)"
            )
            matches = re.findall(pattern, cell_text_processed)
            self._log.debug("Matching: %s", matches)
            for group in matches:
                self._log.debug("Group: %s", group)
                shapes = self.interpret_and_create_shapes(group[2], group[4], group[1])
                self._log.debug("shapes created: %d", len(shapes))
                cell.content.extend(shapes)
        return cell

    def interpret_and_create_shapes(self, shape_id: str, shape_cfg, n=1) -> list[Shape]:
        """
        Interprets the shape based on provided groups.

        :param shape_id: quick id of the shape as defined in symbols.
        :param shape_cfg: configuration of the shapes to be created (if any).
        :param n: number of times to repeat this shape (default will be 1).
        :return: a list of shapes
        """
        shape: Shape | None = None
        ret = []
        ni = 1
        if n:
            ni = int(n)
        if shape_cfg:
            shape_cfg = list(
                filter(None, shape_cfg.split(GridSymbol.UNIVERSAL_SEPARATOR))
            )
        cfg = self._cfg_parser.interpret(shape_cfg)
        self._log.debug("shape: x%d, %s, %s, %s", ni, shape_id, shape_cfg, cfg)
        match shape_id:
            case ShapeSymbol.ARROW | "Arrow":
                shape = Arrow(**cfg)
            case ShapeSymbol.CIRCLE | "Circle":
                shape = Circle(**cfg)
            case ShapeSymbol.DIAMOND | "Diamond":
                shape = Diamond(**cfg)
            case ShapeSymbol.ELLIPSE | "Ellipsis":
                shape = Ellipse(**cfg)
            case ShapeSymbol.HEXAGON | "Hexagon":
                shape = Hexagon(**cfg)
            case ShapeSymbol.RECTANGLE | "Rectangle":
                shape = Rectangle(**cfg)
            case ShapeSymbol.SQUARE | "Square":
                shape = Rectangle(**cfg)
                shape.is_square = True
            case ShapeSymbol.STAR | "Star":
                shape = Star(**cfg)
            case ShapeSymbol.TRIANGLE | "Triangle":
                shape = Triangle(**cfg)
            case _:
                shape = self.check_for_text_based_shape(shape_id, cfg)
        if shape:
            ret = [shape] * ni
        return ret

    def check_for_text_based_shape(self, shape_id: str, shape_cfg) -> Shape | None:
        """
        Checks if a shape_id is not a text shape declaration.

        :param shape_id: quick id of the shape as defined in symbols.
        :param shape_cfg: configuration of the shapes to be created (if any).
        :return: a shape or None
        """
        shape: Shape | None = None
        pattern = re.compile("^" + GridSymbol.TXT_PATTERN + "$")
        if pattern.match(shape_id):
            shape = Text(**shape_cfg)
            shape.content = shape_id[1:-1]
        else:
            self._log.error("Unknown shape ID '%s'", shape_id)
        return shape
