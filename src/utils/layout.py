from dataclasses import dataclass
from enum import StrEnum
import logging
import re
from typing import TypeAlias


from .geometry import Angle, Vector
from .searchable import Searchable
from .symbols import GridSymbol


class PositionShardHorizontal(StrEnum):
    "Horizontal positioning, `None` is Center."
    LEFT = "left"
    RIGHT = "right"


class PositionShardVertical(StrEnum):
    "Vertical positioning, `None` is Center/Middle"
    BOTTOM = "bottom"
    TOP = "top"


PositionShard: TypeAlias = PositionShardHorizontal | PositionShardVertical | None


@dataclass(frozen=True)
class Position:
    valign: PositionShardVertical | None
    halign: PositionShardHorizontal | None
    shortcuts: list[str] | None = None
    relative_coords: Vector | None = None
    _angle: Angle | int | float | None = None

    @property
    def angle(self) -> Angle:
        a = None
        if isinstance(self._angle, (float, int)):
            a = Angle(self._angle)
        elif isinstance(self._angle, Angle):
            a = self._angle
        return a

    @property
    def mnemonics(self):
        mnemos = list(filter(None, [self.valign, self.halign]))
        return "_".join([v.value for v in mnemos])

    def __repr__(self):
        return self.mnemonics


class PositionFactory:

    def __init__(self):
        self._log = logging.getLogger()
        self._positions: list[Position] = [
            Position(PositionShardVertical.BOTTOM, None, ["B"], Vector(0.5, 1), 270),
            Position(
                PositionShardVertical.BOTTOM,
                PositionShardHorizontal.LEFT,
                ["Z"],
                Vector(0, 1),
                225,
            ),
            Position(
                PositionShardVertical.BOTTOM,
                PositionShardHorizontal.RIGHT,
                ["C"],
                Vector(1, 1),
                315,
            ),
            Position(None, PositionShardHorizontal.LEFT, ["L"], Vector(0, 0.5), 180),
            Position(None, PositionShardHorizontal.RIGHT, ["R"], Vector(1, 0.5), 0),
            Position(PositionShardVertical.TOP, None, ["T"], Vector(0.5, 0), 90),
            Position(None, None, ["S"], Vector(0.5, 0.5)),
            Position(
                PositionShardVertical.TOP,
                PositionShardHorizontal.LEFT,
                ["Q"],
                Vector(0, 0),
                135,
            ),
            Position(
                PositionShardVertical.TOP,
                PositionShardHorizontal.RIGHT,
                ["E"],
                Vector(1, 0),
                45,
            ),
        ]

    @property
    def _shard_dict(self) -> dict[str, PositionShard]:
        return {
            v.value: v
            for v in [e for e in PositionShardHorizontal]
            + [e for e in PositionShardVertical]
        }

    def _str_to_shard(self, shard: str) -> PositionShard | None:
        """
        Gets a position shard from the string representation.
        """
        return self._shard_dict.get(shard, None)

    def get_position(self, key: list[str] | tuple[str] | str) -> Position | None:
        """
        Gets a position from the key, which can be:
        - a mnemonic
        - a shortcut
        - position id ("left", "top", etc)

        :param key: search key
        :return: a position matching the key, None otherwise
        """
        pos = None
        candidates = list(
            filter(lambda p: p.mnemonics == key or key in p.shortcuts, self._positions)
        )
        if len(candidates) > 0:
            pos = candidates[0]
        if not pos:
            searched = list(key) if isinstance(key, (str, tuple)) else key
            searched = [self._str_to_shard(s) for s in searched]
            halign = next(
                (p for p in searched if isinstance(p, PositionShardHorizontal)), None
            )
            valign = next(
                (p for p in searched if isinstance(p, PositionShardVertical)), None
            )
            pos = next(
                (
                    p
                    for p in self._positions
                    if p.halign == halign and p.valign == valign
                ),
                None,
            )
        return pos

    def is_layouting(self, o) -> bool:
        return (
            o == None
            or o in self._shard_dict
            or o in [s for pl in self._positions for s in pl.shortcuts]
        )


class LayoutType(StrEnum):
    """
    Display type of the layout, e.g. in which main axis does the layout propagates.
    """

    # Ideas: Arrow, Arc, Triangle, Circle, letter-shaped
    LINE = "line"
    "Layout will be a single line."
    STACK = "stack"
    "All shapes will be stacked upon each other (default)."
    # GRID = "grid"
    # "Layout will be going equally between X and Y axis."


_LAYOUT_SHORTCUTS: dict[str, str] = {
    "horizontal": "line[L,R]",
    "rhorizontal": "line[R,L]",
    "vertical": "line[T,B]",
    "rvertical": "line[B,T]",
}
"Human readable shortcuts for layouts dictionary to functional layout declarations."


@dataclass
class Layout(Searchable):
    display_type: LayoutType = LayoutType.STACK
    start: Position | None = None
    end: Position | None = None

    @staticmethod
    def is_layout(o) -> bool:
        return any([o.startswith(t) for t in LayoutType]) or Layout.is_layout_shortcut(
            o
        )

    @staticmethod
    def is_layout_shortcut(o) -> bool:
        return o in _LAYOUT_SHORTCUTS

    @staticmethod
    def expand_shortcut(o) -> str | None:
        """
        Gets the true value of a shortcut.
        """
        return _LAYOUT_SHORTCUTS[o] if o in _LAYOUT_SHORTCUTS else None
