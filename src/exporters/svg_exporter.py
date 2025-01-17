import logging
from pathlib import Path
import svg
from typing import TypeAlias, Any

from .exporter import Exporter
from ..shapes import Shape, Arrow, Circle
from ..grid import Grid, GridConfig


Position: TypeAlias = tuple[float,float]
SVGElementCreation: TypeAlias = tuple[dict[str,list[svg.Element]], list[svg.Element]]


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
    self._log.debug(f"Grid size: {widthn}x{heightn} => Image size: {width_img}x{height_img} px")
    def_elements: dict[str,list[svg.Element]] = {}
    elements: list[svg.Element] = []
    for defs,els in [self.create_svg_grid(grid), self.create_svg_elements_in_grid(grid)]:
      elements.extend(els)
      def_elements.update(defs)
    self._log.debug(f"Definitions: {def_elements.keys()}")
    elements.insert(0, svg.Defs(elements=[v for k,v in def_elements.items()]))
    canvas = svg.SVG(
      width=width_img,
      height=height_img,
      elements=elements
    )
    self._log.debug("Creating resulting file")
    with open(output_file, "w") as write_file:
      write_file.write(str(canvas))

  def create_svg_grid(self, grid: Grid) -> SVGElementCreation:
    """
    Creates the grid base for the svg.

    :param grid: object representation of the grid
    :return: normal elements, defs elements
    """
    svg_path = svg.Path(fill="none", stroke="black", stroke_width=grid.cfg.border_width, d=[f"M {grid.cfg.cell_size} 0 L 0 0 0 {grid.cfg.cell_size}"])
    svg_pattern = svg.Pattern(id="grid", patternUnits = "userSpaceOnUse", width = grid.cfg.cell_size, height = grid.cfg.cell_size, elements=[svg_path])
    rect = svg.Rect(width="100%", height="100%", fill="url(#grid)")
    return {"grid": svg_pattern}, [rect]

  def create_svg_elements_in_grid(self, grid: Grid) -> SVGElementCreation:
    """
    Create all svg elements based on the shapes in the provided grid.

    :param grid: grid to create the svg elements from
    :return: normal elements, defs elements
    """
    def_elements: dict[str,list[svg.Element]] = {}
    elements: list[svg.Element] = []
    for row in range(len(grid.content)):
      for col in range(len(grid.content[row])):
        # TODO calculate the position of each shape according to cell orientation and number of shapes in the cell
        for shape in grid.content[row][col].content:
          self._log.debug(shape)
          defs, elts = self.create_element(shape, grid, (col,row))
          def_elements.update(defs)
          elements.extend(elts)
    return def_elements, elements

  def create_element(self, shape: Shape, grid: Grid, position:Position) -> SVGElementCreation:
    """
    Dispatch the call to create an element from the Shape.

    :param shape: shape to create
    :return: the created elements
    """
    definitions: dict[str,list[svg.Element]] = {}
    elements: list[svg.Element] = []
    self._log.debug(f"pos={position}, {shape}")
    # TODO convert shapes into SVG code https://pypi.org/project/svg.py/
    # TODO find a more generic approach to the shape creation
    # Something like self.create_shape(svg.Circle, dictionary of parameters)
    # then create_shape() double checks the actual parameters (what of the definitions then?)
    if isinstance(shape, Circle):
      defs,els = self.create_circle(shape, grid, position)
    elif isinstance(shape, Arrow):
      defs,els = self.create_arrow(shape, grid, position)
    definitions.update(defs)
    elements.extend(els)
    return definitions,elements

  def create_circle(self, shape: Circle, grid: Grid, cell_pos:Position) -> SVGElementCreation:
    cell_center = self.calculate_cell_center(grid, cell_pos)
    shape_color = self.from_cfg("shapes_fill", grid, shape.fill)
    radius = self.calculate_size(grid, shape.width) / 2
    self._log.debug(f"Circle=((cx,cy)={cell_center}, r={radius}, fill={shape_color})")
    return {}, [svg.Circle(cx=cell_center[0], cy=cell_center[1], fill=shape_color, r=radius)]

  def create_arrow(self, shape: Arrow, grid: Grid, cell_pos:Position) -> SVGElementCreation:
    eid = "arrow-head"
    shape_color = self.from_cfg("shapes_fill", grid, shape.fill)
    head_path = svg.Path(fill=shape_color, d="M0,0 V4 L2,2 Z")
    marker = svg.Marker(id=eid, orient="auto", markerWidth='3', markerHeight='4', refX='0.1', refY='2', elements=[head_path])
    defs = {eid: marker}
    cell_center = self.calculate_cell_center(grid, cell_pos)
    # TODO Manage rotation
    arrow_start = (cell_center[0],cell_center[1]+(grid.cfg.cell_size/2-1))
    arrow_end = (cell_center[0],cell_center[1]-(grid.cfg.cell_size/2-5))
    self._log.debug(f"Arrow=((x,y)s={arrow_start}, (x,y)e={arrow_end}, fill={shape_color})")
    elts = [svg.Path(id=f"arrow-{cell_pos[0]}-{cell_pos[1]}", marker_end=f"url(#{eid})", stroke_width='2', fill=shape_color, stroke=shape_color,
                     d=f"M {arrow_start[0]},{arrow_start[1]} {arrow_end[0]},{arrow_end[1]}")]
    return defs, elts

  def calculate_cell_center(self, grid:Grid, cell_pos:Position) -> Position:
    return tuple([pos * grid.cfg.cell_size + grid.cfg.cell_size / 2 for pos in cell_pos])

  def calculate_size(self, grid:Grid, value) -> float:
    size = 0
    if isinstance(value, str):
      if '%' in value:
        size = grid.cfg.cell_size * float(value[:-1]) / 100
      elif 'px' in value:
        size = grid.cfg.cell_size * float(value[:-2])
    elif isinstance(value, int) or isinstance(value, float):
      size = value
    return size

  def from_cfg(self, key:str, grid:Grid, value:Any = None):
    nvalue = value
    if not value:
      nvalue = grid.cfg.__dict__.get(key, value)
    return nvalue
