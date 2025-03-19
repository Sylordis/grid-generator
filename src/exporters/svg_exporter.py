from dataclasses import dataclass
from pathlib import Path
import re
import svg
from typing import TypeAlias

from .exporter import Exporter
from ..grid import Grid
from ..shapes import (
    Shape,
    OrientableShape,
    Arrow,
    Circle,
    Diamond,
    Ellipse,
    Hexagon,
    Rectangle,
    Star,
    Triangle,
)
from ..utils.converters import apply_all, str_to_number, Converters, Size
from ..utils.geometry import rotate, Angle, Coordinates, Vector
from ..layout_generator import LayoutGenerator


SVGElementCreation: TypeAlias = tuple[dict[str, list[svg.Element]], list[svg.Element]]
"""
Type representing the produced result of creating SVG elements, with a dictionary for definitions,
and a list for created SVG normal elements.
"""


@dataclass
class SVGArrowCfg:
    "Basic configuration for SVG Arrow (Path + head) elements."

    head_length: float = 4
    "Head length."


@dataclass
class SVGExporterCfg:
    "Configuration for the exporter itself."

    arrows: SVGArrowCfg | None = None
    "Arrows configuration."

    def __post_init__(self):
        self.arrows = SVGArrowCfg()


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
        layout_manager = LayoutGenerator()
        for row in range(len(grid.content)):
            for col in range(len(grid.content[row])):
                cell_pos = Coordinates(col, row)
                self._log.debug(f"Generating cell {Vector(col,row)}")
                cell = grid.cell(cell_pos)
                self._log.debug(
                    f"Content={[s.__class__.__name__ for s in cell.content]}"
                )
                layout_pos = layout_manager.generate(grid, cell_pos)
                # Create shapes
                shape_index = 1
                for shape in cell.content:
                    defs, elts = self.create_element(
                        shape,
                        grid,
                        cell_pos,
                        shape_center=next(layout_pos),
                        shape_index=shape_index,
                    )
                    def_elements.update(defs)
                    elements.extend(elts)
                    shape_index = shape_index + 1
        return def_elements, elements

    def create_element(
        self,
        shape: Shape,
        grid: Grid,
        cell_position: Coordinates,
        shape_center: Coordinates = None,
        shape_index: int = 1,
    ) -> SVGElementCreation:
        """
        Dispatch the call to create an svg element from the Shape.

        :param shape: shape to create
        :param grid: grid
        :param cell_position: cell position in the grid
        :param shape_center: center of the shape
        :param shape_index: index of the shape in the parent amount of shapes (for id)
        :return: a tuple for (definitions, elements) required to be created
        """
        definitions: dict[str, list[svg.Element]] = {}
        elements: list[svg.Element] = []
        shape_id = f"{shape.__class__.__name__.lower()}-{cell_position[0]+1}-{cell_position[1]+1}-{shape_index}"
        attr_name = f"create_{shape.__class__.__name__.lower()}"
        self._log.debug(f"pos={cell_position}, {attr_name}: {shape}")
        if hasattr(self, attr_name):
            creator = getattr(self, attr_name)
            definitions, elements = creator(
                shape=shape,
                grid=grid,
                cell_pos=cell_position,
                shape_center=shape_center,
                shape_id=shape_id,
            )
        else:
            self._log.error(f"No idea how to export shape '{shape.__class__.__name__}'")
        if len(elements) > 0:
            self._log.debug(f"Shape {shape_id} created")
        return definitions, elements

    def create_arrow(
        self,
        shape: Arrow,
        grid: Grid,
        cell_pos: Coordinates,
        shape_center: Coordinates | None = None,
        shape_id: str | None = None,
    ) -> SVGElementCreation:
        svg_params = self._extract_standard_svg_params(shape, grid)
        # Create arrow
        length_full, *_ = grid.calculate_dimensions(shape)
        arrow_end = Coordinates(
            0, -length_full / 2 + self.exporter_cfg.arrows.head_length
        )
        arrow_start = Coordinates(0, length_full / 2)
        arrow_start, arrow_end = tuple(
            (shape_center + p).apply(Converters.to_float(2))
            for p in [arrow_start, arrow_end]
        )
        # Rotate
        svg_params["transform"] = self._calculate_rotation_transform(
            self._get_angles(shape, grid, cell_pos), shape_center
        )
        self._log.debug(
            f"Arrow: base {arrow_start}=>{arrow_end}, length_full={length_full}, distance={arrow_start.distance(arrow_end)}, params={svg_params}"
        )
        # Re-center in the middle of the cell
        # Create SVG definition for head
        head_path = svg.Path(fill=svg_params["fill"], d="M0,0 V4 L2,2 Z")
        head_def_id = f"arrow-head-{self.normalize_id(svg_params["fill"])}-{self.normalize_id(length_full)}"
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
                stroke_width="2",  # TODO Make it according to width
                stroke=svg_params["fill"],
                d=f"M {arrow_start[0]},{arrow_start[1]} {arrow_end[0]},{arrow_end[1]}",
                **svg_params,
            )
        ]
        return defs, elts

    def create_circle(
        self,
        shape: Circle,
        grid: Grid,
        cell_pos: Coordinates,
        shape_center: Coordinates | None = None,
        shape_id: str | None = None,
    ) -> SVGElementCreation:
        svg_params = self._extract_standard_svg_params(shape, grid)
        radius = (
            grid.calculate_size(shape.width, base=grid.shapes_cfg.base_cell_ratio) / 2
        )
        self._log.debug(f"Circle=(xy={shape_center}, r={radius}, params={svg_params})")
        return {}, [
            svg.Circle(
                id=shape_id,
                cx=shape_center[0],
                cy=shape_center[1],
                r=radius,
                **svg_params,
            )
        ]

    def create_diamond(
        self,
        shape: Diamond,
        grid: Grid,
        cell_pos: Coordinates,
        shape_center: Coordinates | None = None,
        shape_id: str | None = None,
    ) -> SVGElementCreation:
        svg_params = self._extract_standard_svg_params(shape, grid)
        width, height = grid.calculate_dimensions(
            shape, default_width=grid.shapes_cfg.base_cell_ratio_2
        )
        svg_params["transform"] = self._calculate_rotation_transform(
            self._get_angles(shape, grid, cell_pos), shape_center
        )
        points = [
            shape_center - Vector(0, height / 2),
            shape_center + Vector(width / 2, 0),
            shape_center + Vector(0, height / 2),
            shape_center - Vector(width / 2, 0),
        ]
        discreet_points = self._discreetise(points)
        self._log.debug(
            f"Polygon=(xy={shape_center}, points={points}, params={svg_params})"
        )
        self._log.debug(f"Points flatmap = {discreet_points}")
        return {}, [svg.Polygon(id=shape_id, points=discreet_points, **svg_params)]

    def create_ellipse(
        self,
        shape: Ellipse,
        grid: Grid,
        cell_pos: Coordinates,
        shape_center: Coordinates | None = None,
        shape_id: str | None = None,
    ) -> SVGElementCreation:
        svg_params = self._extract_standard_svg_params(shape, grid)
        width, height = grid.calculate_dimensions(
            shape, default_height=grid.shapes_cfg.base_cell_ratio_2
        )
        rx, ry = width / 2, height / 2
        cx, cy, rx, ry = self.normalize_numbers(shape_center.x, shape_center.y, rx, ry)
        self._log.debug(
            f"Ellipse=(xy={shape_center}, rx,ry={width},{height}, params={svg_params})"
        )
        return {}, [svg.Ellipse(id=shape_id, cx=cx, cy=cy, rx=rx, ry=ry, **svg_params)]

    def create_hexagon(
        self,
        shape: Hexagon,
        grid: Grid,
        cell_pos: Coordinates,
        shape_center: Coordinates | None = None,
        shape_id: str | None = None,
    ) -> SVGElementCreation:
        svg_params = self._extract_standard_svg_params(shape, grid)
        radius = (
            grid.calculate_size(shape.width, base=grid.shapes_cfg.base_cell_ratio) / 2
        )
        original_point = Vector(radius, 0)
        points = [original_point + shape_center] + [
            shape_center + rotate(original_point, Angle(a)) for a in range(60, 360, 60)
        ]
        discreet_points = self._discreetise(points)
        svg_params["transform"] = self._calculate_rotation_transform(
            self._get_angles(shape, grid, cell_pos), shape_center
        )
        self._log.debug(
            f"Hexagon=(cxy={shape_center}, r={radius}, points={points} params={svg_params})"
        )
        self._log.debug(f"Points flatmap = {discreet_points}")
        return {}, [svg.Polygon(id=shape_id, points=discreet_points, **svg_params)]

    def create_rectangle(
        self,
        shape: Rectangle,
        grid: Grid,
        cell_pos: Coordinates,
        shape_center: Coordinates | None = None,
        shape_id: str | None = None,
    ) -> SVGElementCreation:
        svg_params = self._extract_standard_svg_params(shape, grid)
        defaults = {
            "default_width": grid.shapes_cfg.base_cell_ratio,
            "default_height": (
                grid.shapes_cfg.base_cell_ratio
                if shape._is_square
                else grid.shapes_cfg.base_cell_ratio_2
            ),
        }
        width, height = grid.calculate_dimensions(shape, **defaults)
        x, y = shape_center.x - width / 2, shape_center.y - height / 2
        svg_params["transform"] = self._calculate_rotation_transform(
            self._get_angles(shape, grid, cell_pos), shape_center
        )
        # Normalise all values
        x, y, height, width = self.normalize_numbers(x, y, height, width)
        self._log.debug(
            f"Rectangle=(xy={(x,y)}, height={height}, width={width}, params={svg_params})"
        )
        return {}, [
            svg.Rect(
                id=shape_id,
                x=x,
                y=y,
                rx=shape.border_radius,
                height=height,
                width=width,
                **svg_params,
            )
        ]

    def create_star(
        self,
        shape: Star,
        grid: Grid,
        cell_pos: Coordinates,
        shape_center: Coordinates | None = None,
        shape_id: str | None = None,
    ) -> SVGElementCreation:
        svg_params = self._extract_standard_svg_params(shape, grid)
        width, height = grid.calculate_dimensions(
            shape, default_height=grid.shapes_cfg.base_cell_ratio_2
        )
        radius_outer, radius_inner = width / 2, height / 2
        original_outer_point = Vector(0, -radius_outer)
        original_inner_point = Vector(0, -radius_inner)
        points = [shape_center + original_outer_point]
        is_inner = True
        step = 180 / int(shape.sides)
        angle = step
        while angle < 360:
            to_rotate = original_inner_point if is_inner else original_outer_point
            self._log.debug(
                f"Starring: inner? {is_inner} point={to_rotate} angle={angle}"
            )
            points.append(shape_center + rotate(to_rotate, Angle(angle)))
            is_inner = not is_inner
            angle += step
        discreet_points = self._discreetise(points)
        svg_params["transform"] = self._calculate_rotation_transform(
            self._get_angles(shape, grid, cell_pos), shape_center
        )
        self._log.debug(
            f"Star=(cxy={shape_center}, ro/i={radius_outer}/{radius_inner}, sides={shape.sides}, points={points} params={svg_params})"
        )
        self._log.debug(f"Points flatmap = {discreet_points}")
        return {}, [svg.Polygon(id=shape_id, points=discreet_points, **svg_params)]

    def create_triangle(
        self,
        shape: Triangle,
        grid: Grid,
        cell_pos: Coordinates,
        shape_center: Coordinates | None = None,
        shape_id: str | None = None,
    ) -> SVGElementCreation:
        svg_params = self._extract_standard_svg_params(shape, grid)
        width, height = grid.calculate_dimensions(shape)
        x, y = shape_center.x - width / 2, shape_center.y - height / 2
        svg_params["transform"] = self._calculate_rotation_transform(
            self._get_angles(shape, grid, cell_pos), shape_center
        )
        points = [
            shape_center + p
            for p in [
                Vector(0, -height / 2),
                Vector(width / 2, height / 2),
                Vector(-width / 2, height / 2),
            ]
        ]
        discreet_points = self._discreetise(points)
        # Normalise all values
        x, y, height, width = self.normalize_numbers(x, y, height, width)
        self._log.debug(
            f"Triangle=(cxy={shape_center}, height={height}, width={width}, points={points} params={svg_params})"
        )
        return {}, [svg.Polygon(id=shape_id, points=discreet_points, **svg_params)]

    def _calculate_rotation_transform(self, angles, shape_center) -> str | None:
        cx, cy = apply_all(Converters.to_float(2), shape_center.x, shape_center.y)
        transform = None
        if angles[0] and angles[0] != angles[1]:
            angle = angles[1] - angles[0]
            transform = f"rotate({angle.degrees} {cx} {cy})"
            self._log.debug(f"Rotation: {angles[1]} => {angles[0]}")
        return transform

    def _discreetise(self, points: list[Vector]) -> list:
        return self.normalize_numbers(*[c for point in points for c in point.coords])

    def _extract_standard_svg_params(self, shape: Shape, grid: Grid) -> dict:
        params = {}
        for svg_key, shape_key, supplier in [
            ("fill", "fill", lambda s: s.fill),
            ("stroke", "border_color", lambda s: s.border_color),
            ("stroke-width", "border_width", lambda s: s.border_width),
        ]:
            value = grid.shapes_cfg.extract(shape_key, supplier(shape))
            if value:
                params[svg_key] = value
        return params

    def _get_angles(
        self, shape: OrientableShape, grid: Grid, cell_pos: Coordinates
    ) -> tuple[Angle, Angle]:
        desired_angle: Angle = grid.cell(cell_pos).extract(
            "orientation", shape.orientation, grid.shapes_cfg.starting_angle
        )
        current_angle = grid.shapes_cfg.starting_angle
        return desired_angle, current_angle

    def normalize_id(self, s: str):
        o = str(s)
        return re.sub("[^a-zA-Z0-9]", "-", o)

    def normalize_numbers(self, *args):
        return apply_all(Converters.to_float(2), *args)
