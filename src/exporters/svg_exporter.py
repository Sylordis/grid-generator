import logging
from pathlib import Path
import svg

from .exporter import Exporter
from ..shapes import Shape, Circle
from ..grid import Grid, GridConfig


class SVGExporter(Exporter):
  """
  Exporter to SVG format.
  """

  def __init__(self):
    super().__init__()

  def export(self, grid: Grid, cfg: GridConfig, output_file: Path):
    self._log.debug(f"Creating grid image to {output_file}")
    heightn = len(grid.content)
    widthn = len(grid.content[0])
    height_img = heightn * cfg.cell_size + cfg.border_width
    width_img = widthn * cfg.cell_size + cfg.border_width
    self._log.debug(f"Grid size: {widthn}x{heightn} => Image size: {width_img}x{height_img} px")
    def_elements: list[svg.Element] = []
    elements: list[svg.Element] = []
    defs,els = self.create_svg_grid(grid, cfg)
    elements.extend(els)
    def_elements.extend(defs)
    defs,els = self.create_svg_elements_in_grid(grid, cfg)
    elements.extend(els)
    def_elements.extend(defs)
    elements.insert(0, svg.Defs(elements=def_elements))
    canvas = svg.SVG(
      width=width_img,
      height=height_img,
      elements = elements
    )
    self._log.debug("Creating resulting file")
    with open(output_file, "w") as write_file:
      write_file.write(str(canvas))

  def create_svg_grid(self, grid: Grid, cfg: GridConfig) -> tuple[list[svg.Element], list[svg.Element]]:
    """
    Creates the grid base for the svg.

    :param grid: object representation of the grid
    :param cfg: base configuration of the grid
    :return: normal elements, defs elements
    """
    svg_path = svg.Path(fill="none", stroke="black", stroke_width=cfg.border_width, d=[f"M {cfg.cell_size} 0 L 0 0 0 {cfg.cell_size}"])
    svg_pattern = svg.Pattern(id="grid", patternUnits = "userSpaceOnUse", width = cfg.cell_size, height = cfg.cell_size, elements=[svg_path])
    rect = svg.Rect(width="100%", height="100%", fill="url(#grid)")
    return [svg_pattern], [rect]

  def create_svg_elements_in_grid(self, grid: Grid, cfg: GridConfig) -> tuple[list[svg.Element], list[svg.Element]]:
    """
    :param grid: grid to create the svg elements from
    :return: normal elements, defs elements
    """
    def_elements: list[svg.Element] = []
    elements: list[svg.Element] = []
    for col in range(len(grid.content)):
      for row in range(len(grid.content[col])):
        cell_center = (col*cfg.cell_size + cfg.cell_size/2, row*cfg.cell_size + cfg.cell_size/2)
        self._log.debug(cell_center)
        for shape in grid.content[col][row].content:
          self._log.debug(shape)
          elements.append(self.create_element(shape, cfg))
    return def_elements, elements

  def create_element(self, shape: Shape, cfg:GridConfig) -> svg.Element:
    """
    Dispatch the call to create an element from the Shape.
    """
    element = None
    # TODO convert shapes into SVG code https://pypi.org/project/svg.py/
    # TODO calculate the position of the shape according to cell orientation and number of shapes in the cell
    if isinstance(shape, Circle):
      element = self.create_circle(shape, cfg)
    return element

  def create_circle(self, shape: Circle, cfg: GridConfig) -> svg.Circle:
    radius = 0
    if isinstance(shape.width, str):
      if '%' in shape.width:
        radius = cfg.cell_size * float(shape.width[:-1]) / 100 / 2
      elif 'px' in shape.width:
        radius = cfg.cell_size * float(shape.width[:-2]) / 2
    elif isinstance(shape.width, int) or isinstance(shape.width, float):
      radius = shape.width / 2
    self._log.debug(f"Circle=((cx,cy)={shape.position}, r={radius}, fill={shape.fill})")
    return svg.Circle(cx=shape.position[0], cy=shape.position[1], fill=shape.fill, r=radius)