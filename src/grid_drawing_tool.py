from dataclasses import dataclass
import logging
from pathlib import Path
import re


from .cfg_parser import CfgParser
from .exporters import Exporter, SVGExporter
from .grid import Cell, Grid, GridConfig
from .shapes import Shape, Arrow, Circle, Rectangle
from .utils.symbols import GridSymbol, ShapeSymbol


@dataclass
class DrawToolConfig:
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
        """
        self._log = logging.getLogger()
        "Class logger."
        self.cfg = DrawToolConfig()
        "Drawing tool configuration."
        if cfg:
            self._set_cfg(cfg)
        self.grid_cfg = None
        "Overall grid configuration."
        self._cfg_interpretor = CfgParser()

    def _set_cfg(self, cfg):
        """
        Sets the configuration.
        """
        if cfg.dist:
            self.cfg.dist_dir = Path(cfg.dist)
        # "do_export" is a boolean
        if "do_export" in cfg:
            self.cfg.do_export = cfg.do_export

    def draw_all(self, files_str: list[str], cfg: GridConfig = None):
        """
        Tries to draw all provided files.

        :param files_str: list of string paths of files to generate images of
        :param cfg: configuration of the grid
        """
        self._log.debug(f"files: {files_str}")
        files: list[tuple[Path, Path]] = []
        # Check input files and convert
        for file_str in files_str:
            src_file = Path(file_str).resolve()
            if not src_file.exists():
                self._log.warning(f"File '{src_file}' does not exist. Skipping.")
            else:
                dist_file = (
                    self.cfg.dist_dir
                    if self.cfg.dist_dir is not None
                    else src_file.parent
                )
                dist_file = dist_file / f"{src_file.name}"
                dist_file = dist_file.with_suffix(".svg")
                files.append((src_file, dist_file))
        if self.cfg.dist_dir:
            self._log.info(f"Output dir: {self.cfg.dist_dir}")
        # Draw
        for input, output in files:
            grid_config = GridConfig() if cfg is None else cfg
            self.draw_grid(input, output, grid_config)

    def draw_grid(self, input_file: Path, output_file: Path, cfg: GridConfig):
        """
        Draws a grid from a file.

        :param input_file: input text file
        :param output_file: output image file
        :param cfg: grid configuration
        """
        self._log.debug(f"{input_file.resolve()} => {output_file.resolve()}")
        self._log.info(f"Input: {input_file.name}")
        grid = self.parse_grid_file(input_file)
        grid.cfg = cfg
        self._log.debug(self.cfg)
        if self.cfg.do_export:
            exporter: Exporter = SVGExporter()
            exporter.export(grid, output_file)
            self._log.info(f"Output generated: {output_file.name}")
        else:
            self._log.info("Export was cancelled (--no-export).")

    def parse_grid_file(self, input_file: Path) -> Grid:
        """
        Creates an object representation of the grid provided in a file.

        :param input_file: file to read
        :return: a grid object
        """
        with open(input_file, newline="") as grid_file:
            grid: Grid = Grid()
            for line in grid_file:
                line_txt = line.rstrip()
                cells_str = [
                    cell.strip() for cell in line_txt.split(GridSymbol.CELL_SEPARATOR)
                ]
                self._log.debug(f"Line: {cells_str}")
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
        self._log.debug(f"Parsing cell: '{cell_text}'")
        if len(cell_text) > 0:
            cell_text_processed = cell_text
            # Matching config
            pattern_cfg = r"^(\{[^}]+\})"
            match_cfg = re.match(pattern_cfg, cell_text)
            if match_cfg:
                cell_cfg = match_cfg.group(0)
                cell_text_processed = cell_text[len(cell_cfg) :]
                self._log.debug(f"Config matches: {cell_cfg}, {len(cell_cfg)}")
                if cell_cfg:
                    cell_cfg = cell_cfg[1:-1].split(GridSymbol.PARAMS_SEPARATOR)
                    cell.update(self._cfg_interpretor.interpret(cell_cfg))
            # Matching shapes
            self._log.debug(f"Matching shapes: {cell_text_processed}")
            pattern = r"((\d*)([A-Z][a-z]*)(\{([^}]+)\})?)"
            matches = re.findall(pattern, cell_text_processed)
            self._log.debug(f"Matching: {matches}")
            for group in matches:
                self._log.debug(f"Group: {group}")
                shapes = self.interpret_and_create_shapes(group[2], group[4], group[1])
                self._log.debug(f"shapes created: {len(shapes)}")
                cell.content.extend(shapes)
        return cell

    def interpret_and_create_shapes(self, shape_id, shape_cfg, n=1) -> list[Shape]:
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
            shape_cfg = list(filter(None, shape_cfg.split(GridSymbol.PARAMS_SEPARATOR)))
        cfg = self._cfg_interpretor.interpret(shape_cfg)
        self._log.debug(f"shape: x{ni}, {shape_id}, {shape_cfg}, {cfg}")
        match shape_id:
            case ShapeSymbol.ARROW | "Arrow":
                shape = Arrow(**cfg)
            case ShapeSymbol.CIRCLE | "Circle":
                shape = Circle(**cfg)
            case ShapeSymbol.RECTANGLE | "Rectangle":
                shape = Rectangle(**cfg)
            case ShapeSymbol.SQUARE | "Square":
                if "width" in cfg:
                    cfg["height"] = cfg["width"]
                shape = Rectangle(**cfg)
            case _:
                self._log.error(f"Unknown shape ID '{shape_id}'")
        if shape:
            ret = [shape] * ni
        return ret
