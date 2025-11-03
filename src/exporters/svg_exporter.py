"""Exporter for SVG format."""

from dataclasses import dataclass
from pathlib import Path
import re
from typing import TypeAlias

from PIL import ImageFont
import svg

from .exporter import Exporter
from ..grid import Grid
from ..shapes import (
    Shape,
    Arrow,
    ArrowHeadShape,
    Circle,
    Diamond,
    Ellipse,
    Hexagon,
    Rectangle,
    Star,
    Text,
    Triangle,
)
from ..utils.converters import apply_all, Converters
from ..utils.geometry import rotate, Angle, Coordinates, Vector
from ..utils.symbols import CharFilter
from ..utils.units import Size
from ..layout_generator import LayoutGenerator


SVGElementCreation: TypeAlias = tuple[dict[str, list[svg.Element]], list[svg.Element]]
"""
Type representing the produced result of creating SVG elements, with a dictionary for definitions,
and a list for created SVG normal elements.
"""


@dataclass
class SVGExporterCfg:
    "Configuration for the exporter itself."

    pass


class SVGExporter(Exporter):
    """
    Exporter to SVG format.
    """

    def __init__(self):
        super().__init__()
        self.exporter_cfg = SVGExporterCfg()
        self._log.debug(self.exporter_cfg)

    def export(self, grid: Grid, output_file: Path):
        self._log.debug("Creating grid image to %s", output_file)
        heightn = len(grid.content)
        widthn = max(len(x) for x in grid.content)
        height_img = heightn * grid.cfg.cell_size + grid.cfg.border_width
        width_img = widthn * grid.cfg.cell_size + grid.cfg.border_width
        self._log.info(
            "Grid size: %dx%d (Image: %dx%d px)", widthn, heightn, width_img, height_img
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
        self._log.debug("Definitions: %s", def_elements.keys())
        elements.insert(0, svg.Defs(elements=[v for k, v in def_elements.items()]))
        canvas = svg.SVG(width=width_img, height=height_img, elements=elements)
        self._log.debug("Creating resulting file")
        with open(output_file, "w", encoding="utf-8") as write_file:
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
        # TODO Create bg shapes
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
        for row, _ in enumerate(grid.content):
            for col, _ in enumerate(grid.content[row]):
                cell_pos = Coordinates(col, row)
                self._log.debug("Generating cell %s", Vector(col, row))
                self._log.debug("Cell: %s", grid.cell(cell_pos))
                cell = grid.cell(cell_pos)
                self._log.debug(
                    "Content=%s", [s.__class__.__name__ for s in cell.content]
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
        shape_id_parts = [
            shape.__class__.__name__.lower(),
            cell_position[0] + 1,
            cell_position[1] + 1,
            shape_index,
        ]
        shape_id = "-".join([str(p) for p in shape_id_parts])
        attr_name = f"create_{shape.__class__.__name__.lower()}"
        self._log.debug("pos=%s, %s: %s", cell_position, attr_name, shape)
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
            self._log.error(
                "No idea how to export shape '%s'", shape.__class__.__name__
            )
        if len(elements) > 0:
            self._log.debug("Shape %s created", shape_id)
        return definitions, elements

    def create_arrow(
        self,
        shape: Arrow,
        grid: Grid,
        cell_pos: Coordinates,
        shape_center: Coordinates | None = None,
        shape_id: str | None = None,
    ) -> SVGElementCreation:
        "Creates an SVG arrow shape."
        svg_params = self._extract_standard_svg_params(shape, grid)
        # TODO Use height
        length_full, *_ = grid.calculate_dimensions(shape, cell=grid.cell(cell_pos))
        self._log.debug("%s", shape)
        stroke_width = Size(grid.cfg.cell_size / 8)  # Judged aesthetically pleasing
        head_size = (
            stroke_width.value * shape.head_size.value
            if shape.head_size and shape.head_size.is_relative()
            else shape.head_size.value
        )
        self._log.debug(
            "Arrow: stroke_width=%s, head_size=%s, shape.head_size=%s",
            stroke_width,
            head_size,
            shape.head_size.value,
        )
        arrow_end = Coordinates(0, -length_full / 2 + head_size)
        arrow_start = Coordinates(0, length_full / 2)
        # Normalise all values
        arrow_start, arrow_end = tuple(
            (shape_center + p).apply(Converters.to_float(2))
            for p in [arrow_start, arrow_end]
        )
        # Rotate
        svg_params["transform"] = self._calculate_rotation_transform(
            self._get_angles(shape, grid, cell_pos), shape_center
        )
        self._log.debug(
            "Arrow: base %d=>%d, length_full=%d, distance=%d, params=%s",
            arrow_start,
            arrow_end,
            length_full,
            arrow_start.distance(arrow_end),
            svg_params,
        )
        # Create SVG definition for head
        head_def_id = f"arrow-head-{self.normalize_id(svg_params["fill"])}-{self.normalize_id(length_full)}-{shape.style}"
        marker = self.create_arrow_head(
            shape, head_def_id, {"fill": svg_params["fill"]}
        )
        defs = {head_def_id: marker}
        # Create SVG element for the arrow
        elts = [
            svg.Path(
                id=shape_id,
                marker_end=f"url(#{head_def_id})",
                stroke_width=stroke_width,  # TODO Make it according to width/height?
                stroke=svg_params["fill"],
                d=f"M {arrow_start[0]},{arrow_start[1]} {arrow_end[0]},{arrow_end[1]}",
                **svg_params,
            )
        ]
        return defs, elts

    def create_arrow_head(
        self, shape: Arrow, head_id: str, cfg_head: dict = None, cfg_marker: dict = None
    ):
        "Creates the head of an SVG arrow shape."
        if cfg_head is None:
            cfg_head = {}
        if cfg_marker is None:
            cfg_marker = {}
        ref_x = 1  # To change to move the head along the path, + is lower
        ref_y = 1.5
        points = []
        if shape.style == ArrowHeadShape.DIAMOND:
            points = [
                Coordinates(1, 3),
                Coordinates(0, 1.5),
                Coordinates(1, 0),
                Coordinates(3, 1.5),
            ]
        elif shape.style == ArrowHeadShape.INDENT:
            points = [
                Coordinates(0, 3),
                Coordinates(1, 1.5),
                Coordinates(0, 0),
                Coordinates(3, 1.5),
            ]
        elif shape.style == ArrowHeadShape.TRIANGLE:
            points = [Coordinates(0.5, 3), Coordinates(0.5, 0), Coordinates(3, 1.5)]
        marker = svg.Marker(
            id=head_id,
            orient="auto",
            markerWidth="3",
            markerHeight="3",
            refX=ref_x,
            refY=ref_y,
            elements=[
                svg.Polygon(
                    points=" ".join([f"{p.x},{p.y}" for p in points]), **cfg_head
                )
            ],
            **cfg_marker,
        )
        return marker

    def create_circle(
        self,
        shape: Circle,
        grid: Grid,
        cell_pos: Coordinates,
        shape_center: Coordinates | None = None,
        shape_id: str | None = None,
    ) -> SVGElementCreation:
        "Creates an SVG circle shape."
        svg_params = self._extract_standard_svg_params(shape, grid)
        width, _ = grid.calculate_dimensions(shape, cell=grid.cell(cell_pos))
        radius = width / 2
        self._log.debug(
            "Circle=(xy=%s, r=%d, params=%s)", shape_center, radius, svg_params
        )
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
        "Creates an SVG diamond shape."
        svg_params = self._extract_standard_svg_params(shape, grid)
        width, height = grid.calculate_dimensions(
            shape,
            cell=grid.cell(cell_pos),
            cell_alt=True,
            default_width=grid.shapes_cfg.base_cell_ratio_2,
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
            "Polygon=(xy=%s, points=%s, params=%s)", shape_center, points, svg_params
        )
        self._log.debug("Points flatmap = %s", discreet_points)
        return {}, [svg.Polygon(id=shape_id, points=discreet_points, **svg_params)]

    def create_ellipse(
        self,
        shape: Ellipse,
        grid: Grid,
        cell_pos: Coordinates,
        shape_center: Coordinates | None = None,
        shape_id: str | None = None,
    ) -> SVGElementCreation:
        "Creates an SVG ellipse shape."
        svg_params = self._extract_standard_svg_params(shape, grid)
        width, height = grid.calculate_dimensions(
            shape,
            cell=grid.cell(cell_pos),
            default_width=grid.shapes_cfg.base_cell_ratio_2,
        )
        rx, ry = width / 2, height / 2
        cx, cy, rx, ry = self.normalize_numbers(shape_center.x, shape_center.y, rx, ry)
        self._log.debug(
            "Ellipse=(xy=%s, rx,ry=%d,%d, params=%s)",
            shape_center,
            width,
            height,
            svg_params,
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
        "Creates an SVG hexagon shape."
        svg_params = self._extract_standard_svg_params(shape, grid)
        width, _ = grid.calculate_dimensions(shape, cell=grid.cell(cell_pos))
        radius = width / 2
        original_point = Vector(radius, 0)
        points = [original_point + shape_center] + [
            shape_center + rotate(original_point, Angle(a)) for a in range(60, 360, 60)
        ]
        discreet_points = self._discreetise(points)
        svg_params["transform"] = self._calculate_rotation_transform(
            self._get_angles(shape, grid, cell_pos), shape_center
        )
        self._log.debug(
            "Hexagon=(cxy=%s, r=%d, points=%s params=%s)",
            shape_center,
            radius,
            points,
            svg_params,
        )
        self._log.debug("Points flatmap = %s", discreet_points)
        return {}, [svg.Polygon(id=shape_id, points=discreet_points, **svg_params)]

    def create_rectangle(
        self,
        shape: Rectangle,
        grid: Grid,
        cell_pos: Coordinates,
        shape_center: Coordinates | None = None,
        shape_id: str | None = None,
    ) -> SVGElementCreation:
        "Creates an SVG rectangle shape."
        svg_params = self._extract_standard_svg_params(shape, grid)
        defaults = {
            "default_width": grid.shapes_cfg.base_cell_ratio,
            "default_height": (
                grid.shapes_cfg.base_cell_ratio
                if shape.is_square
                else grid.shapes_cfg.base_cell_ratio_2
            ),
        }
        width, height = grid.calculate_dimensions(
            shape, cell=grid.cell(cell_pos), cell_alt=not shape.is_square, **defaults
        )
        x, y = shape_center.x - width / 2, shape_center.y - height / 2
        svg_params["transform"] = self._calculate_rotation_transform(
            self._get_angles(shape, grid, cell_pos), shape_center
        )
        # Normalise all values
        x, y, height, width = self.normalize_numbers(x, y, height, width)
        self._log.debug(
            "Rectangle=(xy=%s, height=%d, width=%d, params=%s)",
            (x, y),
            height,
            width,
            svg_params,
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
        "Creates an SVG star shape."
        svg_params = self._extract_standard_svg_params(shape, grid)
        width, height = grid.calculate_dimensions(
            shape,
            cell=grid.cell(cell_pos),
            cell_alt=True,
            default_height=grid.shapes_cfg.base_cell_ratio_2,
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
                "Starring: inner? %s point=%s angle=%d", is_inner, to_rotate, angle
            )
            points.append(shape_center + rotate(to_rotate, Angle(angle)))
            is_inner = not is_inner
            angle += step
        discreet_points = self._discreetise(points)
        svg_params["transform"] = self._calculate_rotation_transform(
            self._get_angles(shape, grid, cell_pos), shape_center
        )
        self._log.debug(
            "Star=(cxy=%s, ro/i=%d/%d, sides=%s, points=%s params=%s)",
            shape_center,
            radius_outer,
            radius_inner,
            shape.sides,
            points,
            svg_params,
        )
        self._log.debug("Points flatmap = %s", discreet_points)
        return {}, [svg.Polygon(id=shape_id, points=discreet_points, **svg_params)]

    def create_text(
        self,
        shape: Text,
        grid: Grid,
        cell_pos: Coordinates,
        shape_center: Coordinates | None = None,
        shape_id: str | None = None,
    ) -> SVGElementCreation:
        "Creates an SVG text shape."
        svg_params = self._extract_standard_svg_params(shape, grid)
        font_size, _ = grid.calculate_dimensions(
            shape,
            cell=grid.cell(cell_pos),
            default_width=grid.shapes_cfg.base_cell_ratio,
        )
        self._log.debug(
            "Text: cell_size=%spx, avail_size=%s, font_size=%s",
            grid.cfg.cell_size,
            grid.calculate_size(grid.shapes_cfg.base_cell_ratio),
            font_size
        )
        font : ImageFont = ImageFont.truetype("arial.ttf", size = font_size)
        # TODO Calculate size
        self._log.debug("Text size: %s => %s", shape.content, font.getbbox(shape.content))
        # (left, top, right, bottom) bounding box
        x, y = self._center_text(shape_center, shape.content, font_size)
        # Normalise all values
        x, y = self.normalize_numbers(x, y)
        self._log.debug(
            "Text=(center=%s xy=(%d,%d), font-size=%s, text=%s |%d|)",
            shape_center,
            x,
            y,
            font_size,
            shape.content,
            len(shape.content)
        )
        return {}, [
            svg.Text(
                id=shape_id,
                text=shape.content,
                x=x,
                y=y,
                font_size=font_size,
                font_family="sans-serif",
                **svg_params,
            ), svg.Circle(
                fill="green",
                cx=shape_center[0],
                cy=shape_center[1],
                r=1,
            )
        ]

    def _center_text(
        self,
        shape_center: Coordinates,
        text: str,
        font_size: float,
    ) -> Coordinates:
        """
        Centers a given text according to its content.

        :param shape_center: original shape's center
        :param text: text to display
        :param font_size: font size
        :return: the corrected coordinates
        """
        # x = shape_center[0] - len(text) * default_font_size / 4
        # y = shape_center[1] + default_font_size / 4
        x = shape_center[0] - 8
        y = shape_center[1] + 3
        has_lows = len(re.compile(CharFilter.LOW_CHARS).findall(text)) > 0
        has_highs = len(re.compile(CharFilter.HIGH_CHARS).findall(text)) > 0
        self._log.debug("center text: xy=(%d,%d) lows=%s highs=%s", x, y, has_lows, has_highs)
        if has_highs and not has_lows:
            y = y + font_size / 8
        elif not has_highs and has_lows:
            y = y - font_size / 8
        # if text.isupper():
        #     x = x - len(text) * font_size / 10
        self._log.debug("adjusted text: xy=(%d,%d)", x, y)
        return (x, y)

    def create_triangle(
        self,
        shape: Triangle,
        grid: Grid,
        cell_pos: Coordinates,
        shape_center: Coordinates | None = None,
        shape_id: str | None = None,
    ) -> SVGElementCreation:
        "Creates an SVG triangle shape."
        svg_params = self._extract_standard_svg_params(shape, grid)
        width, height = grid.calculate_dimensions(shape, cell=grid.cell(cell_pos))
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
            "Triangle=(cxy=%s, height=%d, width=%d, points=%s params=%s)",
            shape_center,
            height,
            width,
            points,
            svg_params,
        )
        return {}, [svg.Polygon(id=shape_id, points=discreet_points, **svg_params)]

    def _calculate_rotation_transform(self, angles, shape_center) -> str | None:
        """
        Calculates the transformation necessary for a rotation.

        :param angles: angles control matrix to apply
        :param shape_center: the coordinates of the center of the shape
        """
        cx, cy = apply_all(Converters.to_float(2), shape_center.x, shape_center.y)
        transform = None
        if angles[0] and angles[0] != angles[1]:
            angle = angles[1] - angles[0]
            transform = f"rotate({angle.degrees} {cx} {cy})"
            self._log.debug("Rotation: %s => %s", angles[1], angles[0])
        return transform

    def _discreetise(self, points: list[Vector]) -> list:
        """
        Normalises the numbers of a list of vectors.
        """
        return self.normalize_numbers(*[c for point in points for c in point.coords])

    def _extract_standard_svg_params(self, shape: Shape, grid: Grid) -> dict:
        """
        Extracts standard SVG parameters from a shape and the grid configuration.

        :param shape: Shape to extract configuration of
        :param grid: Grid to extract default configuration from
        :return: a configuration dictionary
        """
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
        self, shape: Shape, grid: Grid, cell_pos: Coordinates
    ) -> tuple[Angle, Angle]:
        desired_angle: Angle = grid.cell(cell_pos).extract(
            "orientation", shape.orientation, grid.shapes_cfg.starting_angle
        )
        current_angle = grid.shapes_cfg.starting_angle
        return desired_angle, current_angle

    def normalize_id(self, s: str):
        """
        Normalises a shape id by changing anything non alphadecimal into a dash.

        :param s: a string to normalise
        :return: the string normalised
        """
        o = str(s)
        return re.sub("[^a-zA-Z0-9]", "-", o)

    def normalize_numbers(self, *args):
        """
        Normalises all provided argument numbers to a 2-decimal float number.

        :param args: all numbers to normalise
        :return: numbers normalised
        """
        return apply_all(Converters.to_float(2), *args)
