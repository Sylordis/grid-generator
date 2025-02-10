from enum import StrEnum


class GridSymbol(StrEnum):
    "Symbols for the grid and generic"
    CELL_SEPARATOR = "|"
    PARAMS_START = "{"
    PARAMS_END = "}"
    PARAMS_SEPARATOR = ","


class ShapeSymbol(StrEnum):
    "Symbols for shapes."
    ARROW = "A"
    CIRCLE = "C"
    DIAMOND = "D"
    RECTANGLE = "R"
    SQUARE = "Sq"
    STAR = "St"
    TRIANGLE = "T"


class OrientationSymbol(StrEnum):
    "Symbols for orientations."
    BOTTOM = "B"
    DIAG_BOTTOM_LEFT = "Z"
    DIAG_BOTTOM_RIGHT = "C"
    DIAG_TOP_LEFT = "Q"
    DIAG_TOP_RIGHT = "E"
    LEFT = "L"
    RIGHT = "R"
    TOP = "T"
