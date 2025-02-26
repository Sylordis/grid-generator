from dataclasses import dataclass
from enum import StrEnum


from .searchable import Searchable


class LayoutDisplayType(StrEnum):
  """
  Display type of the layout, e.g. in which main axis does the layout propagates.
  """
  HORIZONTAL = "horizontal"
  "Layout will be strictly horizontal (along X axis)."
  STACKED = "stacked"
  "All shapes will be stacked upon each other."
  SQUARE = "square"
  "Layout will be going equally between X and Y axis."
  VERTICAL = "vertical"
  "Layout will be strictly vertically (along Y axis)."


class LayoutDirectionHorizontal(StrEnum):
  LEFT_TO_RIGHT = "ltr"
  RIGHT_TO_LEFT = "rtl"


class LayoutDirectionVertical(StrEnum):
  BOTTOM_TO_TOP = "btt"
  TOP_TO_BOTTOM = "ttb"


class HorizontalAlign(StrEnum):
  LEFT = "left"
  CENTER = "center"
  RIGHT = "right"


class VerticalAlign(StrEnum):
  BOTTOM = "bottom"
  CENTER = "center"
  TOP = "top"


@dataclass
class Layout(Searchable):
  align: HorizontalAlign = HorizontalAlign.CENTER
  display_type: LayoutDisplayType = LayoutDisplayType.HORIZONTAL
  hdir: LayoutDirectionHorizontal = LayoutDirectionHorizontal.LEFT_TO_RIGHT
  valign: VerticalAlign = VerticalAlign.CENTER
  vdir: LayoutDirectionVertical = LayoutDirectionVertical.TOP_TO_BOTTOM