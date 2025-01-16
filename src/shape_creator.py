import logging
import re
from typing import Any


from .shapes import Shape, Arrow, Circle
from .utils.orientation import Orientation, ORIENTATIONS
from .utils.symbols import GridSymbol, ShapeSymbol, OrientationSymbol


class ShapeCreator:

  def __init__(self):
    """
    Creates a new drawing tool.

    :param dist_dir: destination dir for generating the images
    """
    self._log = logging.getLogger()

  def interpret_and_create_shapes(self, n, shape_id, shape_cfg) -> list[Shape]:
    """
    Interprets the shape based on provided groups.

    :param n: number of times to repeat this shape (default will be 1).
    :param shape_id: quick id of the shape as defined in symbols.
    :param shape_cfg: configuration of the shapes to be created (if any).
    :return: a list of shapes
    """
    shape:Shape|None = None
    if not n:
      n = 1
    if shape_cfg:
      shape_cfg = shape_cfg[1:-1].split(GridSymbol.PARAMS_SEPARATOR)
    self._log.debug(f"shape: x{n}, {shape_id}, {shape_cfg}")
    cfg = self.interpret_cfg(shape_cfg)
    match shape_id:
      case ShapeSymbol.ARROW | "Arrow":
        shape = Arrow(**cfg)
      case ShapeSymbol.CIRCLE | "Circle":
        shape = Circle(**cfg)
      case _:
        self._log.error(f"Unknown shape ID '{shape_id}'.")
    return [shape] * n

  def interpret_cfg(self, shape_cfg_txt: list[str]) -> dict[str,Any]:
    """
    Interprets the text of a configuration.

    :param shape_cfg_txt: configuration text.
    :return: a dictionary of parameters to inject into the shape constructor.
    """
    print([e.value for e in OrientationSymbol])
    cfg:dict[str,Any] = {}
    size_indicator = []
    for param in shape_cfg_txt:
      match = re.match("([a-z-]+)=(.*)", param)
      size_match = re.match("[0-9]+(px|cm|em|%)", param)
      if match:
        cfg[match.group(1).replace('-','_')] = match.group(2)
      elif param in [e.value for e in OrientationSymbol]:
        cfg["orientation"] = [e for e in ORIENTATIONS if e.shortcut == param][0]
      elif size_match:
        size_indicator.append(param)
      else:
        self._log.debug(param)
    # TODO
    if len(size_indicator) > 0:
      pass
    self._log.debug(cfg)
    return self.convert_cfg_values(cfg)

  def convert_cfg_values(self, old_cfg) -> dict[str,Any]:
    """
    Replaces certain dictionary entries that are programmatically correct.

    :param old_cfg: 
    :return: a dictionary of parameters to inject into the shape constructor.
    """
    cfg:dict[str,Any] = old_cfg
    # TODO replace properties that has to be replaced
    return cfg

