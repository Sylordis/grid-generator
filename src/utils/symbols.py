from enum import StrEnum


class GridSymbol(StrEnum):
    "Symbols for the grid and generic"
    CELL_SEPARATOR = "|"
    PARAMS_START = "{"
    PARAMS_END = "}"
    PARAMS_SEPARATOR = ";"


class ShapeSymbol(StrEnum):
    "Symbols for shapes."
    ARROW = "A"
    CIRCLE = "C"
    DIAMOND = "D"
    RECTANGLE = "R"
    SQUARE = "Sq"
    STAR = "St"
    TRIANGLE = "T"
