from dataclasses import dataclass
from enum import StrEnum
import re
from typing import Callable


class SizeUnitKey(StrEnum):
    "Unit types for sizes."
    PERCENTILE = "%"
    PIXELS = "px"


@dataclass(frozen=True)
class SizeUnit:
    "Unit for size."
    key: SizeUnitKey
    "Key for unit."
    relative: bool
    "Is this unit a relative one, i.e. requires another value to be provided for a final calculation."
    value_supplier: Callable[[float], float]
    "Function to pass a value through to get the actual value represented by this size, leave `None` for identity."


SIZE_UNITS: dict[SizeUnitKey, SizeUnit] = {
    SizeUnitKey.PERCENTILE: SizeUnit(SizeUnitKey.PERCENTILE, True, lambda f: f / 100),
    SizeUnitKey.PIXELS: SizeUnit(SizeUnitKey.PIXELS, False, None),
}


class Size:
    "Denotes of a size."

    def __init__(self, value):
        self._value: float = 0
        self._unit: SizeUnit | None = None
        if unit := next(
            iter(
                [p for _, p in SIZE_UNITS.items() if str(value).endswith(p.key.value)]
            ),
            None,
        ):
            self._unit = unit
            self._value = float(value[: -len(self._unit.key.value)])
        else:
            self._value = float(value)
            self._unit = SIZE_UNITS[SizeUnitKey.PIXELS]

    def is_relative(self):
        "Is this unit a relative one, i.e. requires another value to be provided for a final calculation."
        return self._unit.relative

    @property
    def value(self) -> float:
        "Gets the floating value of this size."
        return self._unit.value_supplier(self._value) if self._unit else self._value

    @property
    def unit(self) -> SizeUnit:
        return self._unit

    def __str__(self):
        return f"{self._value}{self._unit.key.value}"

    def __repr__(self):
        return f"{self._value}{self._unit.key.value}"

    @staticmethod
    def pattern():
        "Gets a pattern for sizes."
        return r"(\d+%? *x *\d+%?)|(\d+%? *x)|(x *\d+%?)|(\d+%?)"

    @staticmethod
    def is_size(o) -> re.Match[str] | None:
        """ "
        Checks if the provided object matches the size pattern.
        """
        return re.match(Size.pattern(), o)
