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
  "All shapes will be stacked upon each other (default)."
  SQUARE = "square"
  "Layout will be going equally between X and Y axis."
  VERTICAL = "vertical"
  "Layout will be strictly vertically (along Y axis)."


class LayoutDirectionHorizontal(StrEnum):
  LEFT_TO_RIGHT = "ltr"
  "Elements will be layout from left to right."
  RIGHT_TO_LEFT = "rtl"
  "Elements will be layout from right to left."


class LayoutDirectionVertical(StrEnum):
  BOTTOM_TO_TOP = "btt"
  "Elements will be layout from bottom to top."
  TOP_TO_BOTTOM = "ttb"
  "Elements will be layout from top to bottom."


@dataclass
class Layout(Searchable):
  display_type: LayoutDisplayType = LayoutDisplayType.STACKED
  hdir: LayoutDirectionHorizontal = LayoutDirectionHorizontal.LEFT_TO_RIGHT
  vdir: LayoutDirectionVertical = LayoutDirectionVertical.TOP_TO_BOTTOM