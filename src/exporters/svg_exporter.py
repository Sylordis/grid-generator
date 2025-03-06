from dataclasses import dataclass, field
from pathlib import Path
import re
import svg
from typing import TypeAlias, Any

from .exporter import Exporter
from ..grid import Grid, GridConfig, Cell
from ..shapes import Shape, Arrow, Circle
from ..utils.converters import str_to_number, Converters
from ..utils.geometry import Angle, Coordinates, rotate
from ..utils.layout import Position


SVGElementCreation: TypeAlias = tuple[dict[str, list[svg.Element]], list[svg.Element]]
"""
Type representing the produced result of creating SVG elements, with a dictionary for definitions,
and a list for created SVG normal elements.
"""


@dataclass(frozen=True)
class SVGCircleCfg:
    "Basic configuration for SVG Circle elements."
    pass


@dataclass(frozen=True)
class SVGArrowCfg:
    "Basic configuration for SVG Arrow (Path + head) elements."

    head_length: float = 3
    "Head length."


@dataclass(frozen=True)
class SVGExporterCfg:
    "Configuration for the exporter itself."

    arrows: SVGArrowCfg | None = field(default=SVGArrowCfg())
    "Arrows configuration."
    circles: SVGCircleCfg | None = field(default=SVGCircleCfg())
    "Circles configuration."
    shape_base_cell_ratio: Any = "80%"
    "Base ratio for a shape width according to cell size."
    starting_angle = Angle(0)
    "Starting angle for all shapes."


class SVGExporter(Exporter):
    """
    Exporter to SVG format.
    """

    def __init__(self):
        super().__init__()
        self.exporter_cfg = SVGExporterCfg()
        self._log.debug(self.exporter_cfg)

    def export(self, grid: Grid, output_file: Path):
        self._log.debug(f"Creating grid image to {output_file}")
        heightn = len(grid.content)
        widthn = max(len(x) for x in grid.content)
        height_img = heightn * grid.cfg.cell_size + grid.cfg.border_width
        width_img = widthn * grid.cfg.cell_size + grid.cfg.border_width
        self._log.info(
            f"Grid size: {widthn}x{heightn} => Image size: {width_img}x{height_img} px"
        )
        def_elements: dict[str, list[svg.Element]] = {}
        elements: list[svg.Element] = []
        for defs, els in [
            self.create_bg_shapes(grid),
            self.create_svg_elements_in_grid(grid),
        ]:
            elements.extend(els)
            def_elements.update(defs)
        # Add SVG element and def for the grid, either after if supposed to be over other shapes or
        # before if under.
        defs, els = self.create_svg_grid(grid)
        def_elements.update(defs)
        if grid.cfg.grid_over_components:
            elements.extend(els)
        else:
            elements = els + elements
        self._log.debug(f"Definitions: {def_elements.keys()}")
        elements.insert(0, svg.Defs(elements=[v for k, v in def_elements.items()]))
        canvas = svg.SVG(width=width_img, height=height_img, elements=elements)
        self._log.debug("Creating resulting file")
        with open(output_file, "w") as write_file:
            write_file.write(str(canvas))

    def create_svg_grid(self, grid: Grid) -> SVGElementCreation:
        """
        Creates the grid base for the svg.

        :param grid: object representation of the grid
        :return: normal elements, defs elements
        """
        svg_path = svg.Path(
            fill="none",
            stroke="black",
            stroke_width=grid.cfg.border_width,
            d=[f"M {grid.cfg.cell_size} 0 L 0 0 0 {grid.cfg.cell_size}"],
        )
        svg_pattern = svg.Pattern(
            id="grid",
            patternUnits="userSpaceOnUse",
            width=grid.cfg.cell_size,
            height=grid.cfg.cell_size,
            elements=[svg_path],
        )
        rect = svg.Rect(width="100%", height="100%", fill="url(#grid)")
        return {"grid": svg_pattern}, [rect]

    def create_bg_shapes(self, grid: Grid) -> SVGElementCreation:
        """
        Creates background shapes, like cell filling.

        :param grid: grid to create the svg elements from
        :return: normal elements, defs elements
        """
        # TODO
        return {}, []

    def create_svg_elements_in_grid(self, grid: Grid) -> SVGElementCreation:
        """
        Create all svg elements based on the shapes in the provided grid.

        :param grid: grid to create the svg elements from
        :return: normal elements, defs elements
        """
        def_elements: dict[str, list[svg.Element]] = {}
        elements: list[svg.Element] = []
        for row in range(len(grid.content)):
            for col in range(len(grid.content[row])):
                shape_index = 1
                # TODO calculate the translation of each shape according to cell orientation and number of shapes in the cell
                # TODO Provide translation from here directly, then just apply it during shape creation
                for shape in grid.content[row][col].content:
                    defs, elts = self.create_element(
                        shape, grid, Coordinates(col, row), shape_index=shape_index
                    )
                    def_elements.update(defs)
                    elements.extend(elts)
                    shape_index = shape_index + 1
        return def_elements, elements

    def create_element(
        self, shape: Shape, grid: Grid, cell_position: Coordinates, shape_index: int = 1
    ) -> SVGElementCreation:
        """
        Dispatch the call to create an svg element from the Shape.

        :param shape: shape to create
        :param grid: grid
        :param position: cell position
        :return: the created elements
        """
        definitions: dict[str, list[svg.Element]] = {}
        elements: list[svg.Element] = []
        self._log.debug(f"pos={cell_position}, {shape}")
        shape_id = f"{shape.__class__.__name__.lower()}-{cell_position[0]+1}-{cell_position[1]+1}-{shape_index}"
        if isinstance(shape, Circle):
            definitions, elements = self.create_circle(
                shape, grid, cell_position, translation=None, shape_id=shape_id
            )
        elif isinstance(shape, Arrow):
            definitions, elements = self.create_arrow(
                shape,
                grid,
                cell_position,
                translation=None,
                shape_id=shape_id,
            )
        self._log.debug(f"Shape {shape_id} created")
        return definitions, elements

    def create_arrow(
        self,
        shape: Arrow,
        grid: Grid,
        cell_pos: Coordinates,
        translation: Coordinates | None = None,
        shape_id: str | None = None,
    ) -> SVGElementCreation:
        shape_fill = grid.shapes_cfg.extract("fill", shape.fill)
        cell_center = grid.calculate_cell_center(cell_pos)
        cell_bounds = [
            cell_center - Coordinates.all(grid.cfg.cell_size / 2),
            cell_center + Coordinates.all(grid.cfg.cell_size / 2),
        ]
        self._log.debug(
            f"Cell: pos={cell_pos} center:{cell_center}, size={grid.cfg.cell_size}, bounds={cell_bounds}"
        )
        # Create arrow
        arrow_length_full = grid.calculate_size(
            shape.width, default=self.exporter_cfg.shape_base_cell_ratio
        )
        self._log.debug(
            f"Arrow_length_full={arrow_length_full}, {shape.width}, base={self.exporter_cfg.shape_base_cell_ratio}"
        )
        # The ends of the arrow are created around (0,0) directly, just need to add cell_center to them after rotation.
        arrow_start = Coordinates(-arrow_length_full / 2, 0)
        arrow_end = Coordinates(
            round(arrow_length_full / 2 - self.exporter_cfg.arrows.head_length, 2), 0
        )
        self._log.debug(
            f"Arrow: base {arrow_start}=>{arrow_end}, length_full={arrow_length_full} (supposed={grid.cfg.cell_size * str_to_number(self.exporter_cfg.shape_base_cell_ratio)}), distance={arrow_start.distance(arrow_end)}"
        )
        # Rotate
        desired_angle: Angle = grid.cell(cell_pos).extract(
            "orientation", shape.orientation, self.exporter_cfg.starting_angle
        )
        current_angle = self.exporter_cfg.starting_angle
        self._log.debug(f"Arrow rotation: {current_angle} => {desired_angle}")
        if desired_angle and desired_angle != self.exporter_cfg.starting_angle:
            angle: Angle = desired_angle - self.exporter_cfg.starting_angle
            arrow_start = rotate(arrow_start, angle)
            arrow_end = rotate(arrow_end, angle)
            self._log.debug(
                f"Arrow rotation: after {arrow_start}=>{arrow_end} distance={arrow_start.distance(arrow_end)}"
            )
        # Re-center in the middle of the cell
        arrow_start = cell_center + arrow_start
        arrow_end = cell_center + arrow_end
        arrow_start = arrow_start.apply(Converters.to_float(2))
        arrow_end = arrow_end.apply(Converters.to_float(2))
        # TODO apply translation if needed
        # https://math.stackexchange.com/questions/2204520/how-do-i-rotate-a-line-segment-in-a-specific-point-on-the-line
        self._log.debug(f"Arrow: final {arrow_start}=>{arrow_end}, fill={shape_fill}")
        # Create SVG definition for head
        head_path = svg.Path(fill=shape_fill, d="M0,0 V4 L2,2 Z")
        head_def_id = f"arrow-head-{self.normalize_id(shape_fill)}-{self.normalize_id(arrow_length_full)}"
        marker = svg.Marker(
            id=head_def_id,
            orient="auto",
            markerWidth=self.exporter_cfg.arrows.head_length,
            markerHeight="4",
            refX="0.1",
            refY="2",
            elements=[head_path],
        )
        defs = {head_def_id: marker}
        # Create SVG element for the arrow
        shape_id = "" if shape_id is None else shape_id
        elts = [
            svg.Path(
                id=shape_id,
                marker_end=f"url(#{head_def_id})",
                stroke_width="2",
                fill=shape_fill,
                stroke=shape_fill,
                d=f"M {arrow_start[0]},{arrow_start[1]} {arrow_end[0]},{arrow_end[1]}",
            )
        ]
        return defs, elts

    def create_circle(
        self,
        shape: Circle,
        grid: Grid,
        cell_pos: Coordinates,
        translation: Coordinates | None = None,
        shape_id: str | None = None,
    ) -> SVGElementCreation:
        shape_center = grid.calculate_cell_center(cell_pos)
        if translation:
            shape_center += translation
        shape_color = grid.shapes_cfg.extract("fill", shape.fill)
        radius = (
            grid.calculate_size(
                shape.width, base=self.exporter_cfg.shape_base_cell_ratio
            )
            / 2
        )
        self._log.debug(f"Circle=(xy={shape_center}, r={radius}, fill={shape_color})")
        return {}, [
            svg.Circle(
                id=shape_id,
                cx=shape_center[0],
                cy=shape_center[1],
                fill=shape_color,
                r=radius,
            )
        ]

    @classmethod
    def normalize_id(cls, s: str):
        o = str(s)
        return re.sub("[^a-zA-Z0-9]", "-", o)
