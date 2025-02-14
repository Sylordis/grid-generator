from dataclasses import dataclass, field
import logging
from pathlib import Path
import svg
from typing import TypeAlias, Any

from .exporter import Exporter
from ..grid import Grid, GridConfig, Cell
from ..shapes import Shape, Arrow, Circle
from ..utils.converters import str_to_number
from ..utils.geometry import Angle, Position, ORIENTATIONS, OrientationSymbol, rotate


SVGElementCreation: TypeAlias = tuple[dict[str, list[svg.Element]], list[svg.Element]]


@dataclass(frozen=True)
class SVGCircleCfg:
    pass


@dataclass(frozen=True)
class SVGArrowCfg:

    head_length: float = 3
    "Head length."


@dataclass(frozen=True)
class SVGExporterCfg:

    arrows: SVGArrowCfg | None = field(default=SVGArrowCfg())
    "Arrows configuration."
    circles: SVGCircleCfg | None = field(default=SVGCircleCfg())
    "Circles configuration."
    shape_base_cell_ratio: Any = '80%'
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
        widthn = len(grid.content[0])
        height_img = heightn * grid.cfg.cell_size + grid.cfg.border_width
        width_img = widthn * grid.cfg.cell_size + grid.cfg.border_width
        self._log.debug(
            f"Grid size: {widthn}x{heightn} => Image size: {width_img}x{height_img} px"
        )
        def_elements: dict[str, list[svg.Element]] = {}
        elements: list[svg.Element] = []
        for defs, els in [
            self.create_svg_grid(grid),
            self.create_svg_elements_in_grid(grid),
        ]:
            elements.extend(els)
            def_elements.update(defs)
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
                # TODO calculate the position of each shape according to cell orientation and number of shapes in the cell
                # TODO Provide translation from here directly, then just apply it during shape creation
                for shape in grid.content[row][col].content:
                    self._log.debug(shape)
                    defs, elts = self.create_element(
                        shape, grid, Position(col, row), shape_index=shape_index
                    )
                    def_elements.update(defs)
                    elements.extend(elts)
                    shape_index = shape_index + 1
        return def_elements, elements

    def create_element(
        self, shape: Shape, grid: Grid, cell_position: Position, shape_index: int = 1
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
            direction: Angle = self.from_cell_cfg(
                "orientation",
                grid.cell(cell_position[0], cell_position[1]),
                shape.orientation,
            )
            definitions, elements = self.create_arrow(
                shape,
                grid,
                cell_position,
                direction=direction,
                translation=None,
                shape_id=shape_id,
            )
        self._log.debug(f"Shape {shape_id} created")
        return definitions, elements

    def create_arrow(
        self,
        shape: Arrow,
        grid: Grid,
        cell_pos: Position,
        direction: Angle | None = None,
        translation: Position | None = None,
        shape_id: str | None = None,
    ) -> SVGElementCreation:
        eid = "arrow-head"
        shape_color = self.from_cfg("shapes_fill", grid, shape.fill)
        head_path = svg.Path(fill=shape_color, d="M0,0 V4 L2,2 Z")
        marker = svg.Marker(
            id=eid,
            orient="auto",
            markerWidth=self.exporter_cfg.arrows.head_length,
            markerHeight="4",
            refX="0.1",
            refY="2",
            elements=[head_path],
        )
        defs = {eid: marker}
        cell_center = self.calculate_cell_center(grid, cell_pos)
        cell_bounds = [cell_center - Position.both(grid.cfg.cell_size/2), cell_center + Position.both(grid.cfg.cell_size/2)]
        self._log.debug(
            f"Cell: pos={cell_pos} center:{cell_center}, size={grid.cfg.cell_size}, bounds={cell_bounds}"
        )
        # Create arrow
        arrow_length_full = self.calculate_size(grid, shape.width)
        # The ends of the arrow are created around (0,0) directly, just need to add cell_center to them after rotation.
        arrow_start = Position(-arrow_length_full/2, 0)
        arrow_end = Position(round(arrow_length_full/2 - self.exporter_cfg.arrows.head_length, 2), 0)
        self._log.debug(
            f"Arrow: base {arrow_start}=>{arrow_end}, length_full={arrow_length_full} (supposed={grid.cfg.cell_size * str_to_number(self.exporter_cfg.shape_base_cell_ratio)}), distance={arrow_start.distance(arrow_end)}"
        )
        # Rotate
        if shape.orientation != self.exporter_cfg.starting_angle:
            angle: Angle = shape.orientation - self.exporter_cfg.starting_angle
            self._log.debug(f"rotation={angle}")
            arrow_start = rotate(arrow_start, angle, lambda x: round(x, 2))
            arrow_end = rotate(arrow_end, angle, lambda x: round(x, 2))
        # else:
        self._log.debug(
            f"Arrow: after rotation {arrow_start}=>{arrow_end} distance={arrow_start.distance(arrow_end)}"
        )
        # Re-center in the middle of the cell
        arrow_start = cell_center + arrow_start
        arrow_end = cell_center + arrow_end
        # TODO apply translation
        # https://math.stackexchange.com/questions/2204520/how-do-i-rotate-a-line-segment-in-a-specific-point-on-the-line
        self._log.debug(
            f"Arrow: final {arrow_start}=>{arrow_end}, fill={shape_color}"
        )
        shape_id = "" if shape_id is None else shape_id
        elts = [
            svg.Path(
                id=f"arrow-{cell_pos[0]}-{cell_pos[1]}",
                marker_end=f"url(#{eid})",
                stroke_width="2",
                fill=shape_color,
                stroke=shape_color,
                d=f"M {arrow_start[0]},{arrow_start[1]} {arrow_end[0]},{arrow_end[1]}",
            )
        ]
        return defs, elts

    def create_circle(
        self,
        shape: Circle,
        grid: Grid,
        cell_pos: Position,
        translation: Position | None = None,
        shape_id: str | None = None,
    ) -> SVGElementCreation:
        shape_center = self.calculate_cell_center(grid, cell_pos)
        if translation:
            shape_center += translation
        shape_color = self.from_cfg("shapes_fill", grid, shape.fill)
        radius = self.calculate_size(grid, shape.width) / 2
        self._log.debug(
            f"Circle=((cx,cy)={shape_center}, r={radius}, fill={shape_color})"
        )
        return {}, [
            svg.Circle(
                cx=shape_center[0], cy=shape_center[1], fill=shape_color, r=radius
            )
        ]

    def calculate_cell_center(self, grid: Grid, cell_pos: Position) -> Position:
        pos = [pos * grid.cfg.cell_size + grid.cfg.cell_size / 2 for pos in cell_pos]
        return Position(pos[0], pos[1])

    def calculate_size(self, grid: Grid, value) -> float:
        size = 0
        if value is None:
            value = self.exporter_cfg.shape_base_cell_ratio
        if isinstance(value, str):
            size = grid.cfg.cell_size * str_to_number(value)
        elif isinstance(value, int) or isinstance(value, float):
            size = value
        return size

    @classmethod
    def from_cfg(cls, key: str, grid: Grid, value: Any = None, default: Any = None):
        """
        Multi-level value getter, the first value found (e.g. not None) in the given list will be returned:
        1. provided value in the arguments.
        2. grid config's dictionary key.
        3. default value.

        :param key: key to get from the grid configuration's dictionary
        :param grid: grid to get the configuration from
        :param value: current value to be returned with priority
        :param default: default value to be returned if all else fails
        :return: the first value which is not None, default value otherwise.
        """
        nvalue = value
        if not value:
            nvalue = grid.cfg.__dict__.get(key, value)
        if not nvalue:
            nvalue = default
        return nvalue

    @classmethod
    def from_cell_cfg(cls, key: str, cell: Cell, value: Any = None):
        """
        Gets the value provided or the given cell configuration's dictionary's value if the former is None.

        :param key: cell's configuration's key to get the value from
        :param cell: cell to get the configuration from
        :param value: current value to be returned with priority 
        :return: the provided value if not None, cell configuration's dictionary's key otherwise
        """
        nvalue = value
        if not value:
            nvalue = cell.__dict__.get(key, value)
        return nvalue
