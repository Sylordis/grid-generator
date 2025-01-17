from __future__ import annotations
from typing import Any


INT_BASE = 255
COLORS: dict[str,Any] = {
    "black": "#000000",
    "blue": "#0000FF",
    "green": "#00FF00",
    "red": "#FF0000",
    "transparent": [0, 0, 0, 0],
    "white": "#FFFFFF",
}

class Color:

    def __init__(self, value_or_red:str|float|int=None, green:float|int = 0.0, blue:float|int = 0.0, opacity:float|int = 1.0):
        self.opacity = opacity
        if all([isinstance(x, float) and 0.0 <= x <= 1.0 for x in [value_or_red, green, blue, opacity]]):
            self.red, self.green, self.blue, self.opacity = value_or_red, green, blue, opacity
        elif all([isinstance(x, int) and 0 <= x <= 255 for x in [value_or_red, green, blue, opacity]]):
            self.red, self.green, self.blue, self.opacity = value_or_red / INT_BASE, green / INT_BASE, blue / INT_BASE, opacity / INT_BASE
        elif isinstance(value_or_red, str):
            assert value_or_red is not None
            string = value_or_red.lower()
            if string[0] == "#":
                string = string[1:]
            r,g,b = int(string[0:2], 16) / INT_BASE, int(string[2:4], 16) / INT_BASE, int(string[4:6], 16) / INT_BASE
            self.red, self.green, self.blue = r,g,b
        else:
            raise ValueError(f"Unknown declaration type {type(value_or_red)}")

    def __iter__(self):
        yield self.red
        yield self.green
        yield self.blue
        yield self.opacity

    @staticmethod
    def from_name(name:str) -> Color:
        return Color(COLORS.get(name, None))

    def web(self) -> str:
        return "#{:02x}{:02x}{:02x}".format(int(self.red * INT_BASE), int(self.green * INT_BASE), int(self.blue * INT_BASE))

    def __str__(self) -> str:
        return self.web()