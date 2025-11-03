from dataclasses import dataclass, field
from enum import StrEnum
import logging
from typing import Any, TypeAlias


from .geometry import Angle, Vector
from .searchable import Searchable
from .units import Size


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
            Position(
                PositionShardVertical.BOTTOM, None, ["B", "X"], Vector(0.5, 1), 180
            ),
            Position(
                PositionShardVertical.BOTTOM,
                PositionShardHorizontal.LEFT,
                ["Z"],
                Vector(0, 1),
                135,
            ),
            Position(
                PositionShardVertical.BOTTOM,
                PositionShardHorizontal.RIGHT,
                ["C"],
                Vector(1, 1),
                225,
            ),
            Position(
                None, PositionShardHorizontal.LEFT, ["L", "A"], Vector(0, 0.5), 90
            ),
            Position(
                None, PositionShardHorizontal.RIGHT, ["R", "F"], Vector(1, 0.5), 270
            ),
            Position(PositionShardVertical.TOP, None, ["T", "W"], Vector(0.5, 0), 0),
            Position(None, None, ["S", "M"], Vector(0.5, 0.5)),
            Position(
                PositionShardVertical.TOP,
                PositionShardHorizontal.LEFT,
                ["Q"],
                Vector(0, 0),
                45,
            ),
            Position(
                PositionShardVertical.TOP,
                PositionShardHorizontal.RIGHT,
                ["E"],
                Vector(1, 0),
                315,
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

    def is_position(self, o) -> bool:
        return o in self._shard_dict or o in [
            s for pl in self._positions for s in pl.shortcuts
        ]


class LayoutType(StrEnum):
    """
    Display type of the layout, e.g. in which main axis does the layout propagates.
    """

    # BOX = "box"
    # "Layout will be going equally between X and Y axis."
    # CHEVRON = "chevron"
    # CIRCLE = "circle"
    # Layout is centred in the cell and divides the shapes all around it on a circle.
    LINE = "line"
    "Layout will be a single line."
    STACK = "stack"
    "All shapes will be stacked upon each other (default)."


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
    keypoints: list[Position] = field(default_factory=list)
    """
    Key points related to the layout, e.g. where it is supposed to pass through in order.
    By definition the first one is considered as the "start" point, the last one is the "end" point.
    """
    height: Size = Size("100%")
    "Set in terms of margin."
    width: Size = Size("100%")
    "Set in terms of margin."

    @property
    def start(self):
        return self.keypoints[0]

    def has_start(self):
        return self.has_keypoints()

    @property
    def end(self):
        return self.keypoints[-1]

    @property
    def has_keypoints(self):
        return len(self.keypoints) > 0

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
