from enum import StrEnum


class GridSymbol(StrEnum):
    "Symbols for the grid and generics."
    CELL_SEPARATOR = "|"
    "Delimiter for cells."
    PARAMS_START = "["
    "Start sequence for configuration parameter values."
    PARAMS_END = "]"
    "End sequence for configuration parameter values."
    PARAMS_SEPARATOR = ","
    "Delimiter for parameter values."
    CFG_START = "{"
    "Start sequence for configuration."
    CFG_END = "}"
    "End sequence for configuration."
    UNIVERSAL_SEPARATOR = ";"
    "Universal separator."
    TXT_PATTERN = r"\"[A-Za-z0-9!]+\""
    "Pattern for text shapes."


class ShapeSymbol(StrEnum):
    "Shortcut symbols for shapes."
    ARROW = "A"
    CIRCLE = "C"
    DIAMOND = "D"
    ELLIPSE = "E"
    HEXAGON = "H"
    # LINE = "L"
    # POLYGON = "P"
    RECTANGLE = "R"
    SQUARE = "Sq"
    STAR = "St"
    TRIANGLE = "T"
