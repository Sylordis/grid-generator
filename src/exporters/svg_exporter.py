import logging
from pathlib import Path
import svg
from typing import TypeAlias, Any

from .exporter import Exporter
from ..grid import Grid, GridConfig, Cell
from ..shapes import Shape, Arrow, Circle
from ..utils.geometry import Angle, Position, ORIENTATIONS, OrientationSymbol, rotate


SVGElementCreation: TypeAlias = tuple[dict[str, list[svg.Element]], list[svg.Element]]


class SVGExporter(Exporter):
    """
    Exporter to SVG format.
    """

    def __init__(self):
        super().__init__()

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
                    defs, elts = self.create_element(shape, grid, Position(col, row), shape_index=shape_index)
                    def_elements.update(defs)
                    elements.extend(elts)
                    shape_index = shape_index + 1
        return def_elements, elements

    def create_element(
        self, shape: Shape, grid: Grid, cell_position: Position, shape_index: int = 1
    ) -> SVGElementCreation:
        """
        Dispatch the call to create an element from the Shape.

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
                shape, grid, cell_position, translation=None, shape_id = shape_id
            )
        elif isinstance(shape, Arrow):
            direction: Angle = self.from_cell_cfg(
                "orientation",
                grid.cell(cell_position[0], cell_position[1]),
                shape.orientation
            )
            definitions, elements = self.create_arrow(
                shape, grid, cell_position, direction=direction, translation=None,
                shape_id = shape_id
            )
        self._log.debug(f"Shape {shape_id} created")
        return definitions, elements

    def create_circle(
        self,
        shape: Circle,
        grid: Grid,
        cell_pos: Position,
        translation: Position | None = None,
        shape_id: str | None = None
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
            svg.Circle(cx=shape_center[0], cy=shape_center[1], fill=shape_color, r=radius)
        ]

    def create_arrow(
        self,
        shape: Arrow,
        grid: Grid,
        cell_pos: Position,
        direction: Angle | None = None,
        translation: Position | None = None,
        shape_id: str | None = None
    ) -> SVGElementCreation:
        eid = "arrow-head"
        shape_color = self.from_cfg("shapes_fill", grid, shape.fill)
        head_path = svg.Path(fill=shape_color, d="M0,0 V4 L2,2 Z")
        marker = svg.Marker(
            id=eid,
            orient="auto",
            markerWidth="3",
            markerHeight="4",
            refX="0.1",
            refY="2",
            elements=[head_path],
        )
        defs = {eid: marker}
        cell_center = self.calculate_cell_center(grid, cell_pos)
        arrow_start, arrow_end = self.create_base_arrow(
            shape, grid, direction
        )
        arrow_start, arrow_end = self.rotate_arrow(arrow_start, arrow_end, shape, grid, direction)
        arrow_start = arrow_start + cell_center
        arrow_end = arrow_end + cell_center
        self._log.debug(f"Arrow: final {arrow_start}=>{arrow_end} ({cell_center}), fill={shape_color}")
        shape_id = '' if shape_id is None else shape_id
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

    def create_base_arrow(
        self, shape: Arrow, grid: Grid, direction: Angle | None = None
    ) -> tuple[Position, Position]:
        shape_width = shape.width if shape.width else 1.0
        base_ratio = 0.9
        head_length = 4
        arrow_length = (grid.cfg.cell_size - head_length) * shape_width * base_ratio
        head_length = head_length * base_ratio
        # Center the arrow on origin first
        arrow_start = Position(0, arrow_length)
        arrow_end = Position(0, 0)
        return arrow_start, arrow_end

    def calculate_cell_center(self, grid: Grid, cell_pos: Position) -> Position:
        pos = [pos * grid.cfg.cell_size + grid.cfg.cell_size / 2 for pos in cell_pos]
        return Position(pos[0], pos[1])

    def calculate_size(self, grid: Grid, value) -> float:
        size = 0
        if isinstance(value, str):
            if "%" in value:
                size = grid.cfg.cell_size * float(value[:-1]) / 100
            elif "px" in value:
                size = grid.cfg.cell_size * float(value[:-2])
        elif isinstance(value, int) or isinstance(value, float):
            size = value
        return size

    @classmethod
    def from_cfg(cls, key: str, grid: Grid, value: Any = None, default: Any = None):
        nvalue = value
        if not value:
            nvalue = grid.cfg.__dict__.get(key, value)
        if not nvalue:
            nvalue = default
        return nvalue

    @classmethod
    def from_cell_cfg(cls, key: str, cell: Cell, value: Any = None):
        nvalue = value
        if not value:
            nvalue = cell.__dict__.get(key, value)
        return nvalue

    def rotate_arrow(self, arrow_start: Position, arrow_end: Position, shape: Shape, grid: Grid, direction: Angle | None = None):
        self._log.debug(
            f"Arrow: before rotation {arrow_start}=>{arrow_end}, distance={arrow_start.distance(arrow_end)}"
        )
        # TODO Rotate
        # if direction and direction != ORIENTATIONS.get(OrientationSymbol.TOP):
        #     # Base orientation is towards the top
        #     angle: Angle = direction - ORIENTATIONS[OrientationSymbol.TOP]
        #     self._log.debug(f"rotation={angle}")
        #     arrow_start = rotate(base_arrow_start, -angle, lambda x: round(x, 2))
        # else:
        arrow_start_rotated = arrow_start
        arrow_end_rotated = arrow_end
        self._log.debug(
            f"Arrow: after rotation {arrow_start}=>{arrow_end}, distance={arrow_start.distance(arrow_end)}"
        )
        return arrow_start_rotated, arrow_end_rotated