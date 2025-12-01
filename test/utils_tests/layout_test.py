import pytest

from utils.layout import Position, PositionFactory, PositionShard, PositionShardVertical, PositionShardHorizontal


class TestPosition:

    @pytest.mark.parametrize(
        "position,expected", [
            (Position(None, None), ""),
            (Position(PositionShardVertical.TOP, None), "top"),
            (Position(PositionShardVertical.BOTTOM, None), "bottom"),
            (Position(None, PositionShardHorizontal.LEFT), "left"),
            (Position(None, PositionShardHorizontal.RIGHT), "right"),
            (Position(PositionShardVertical.TOP, PositionShardHorizontal.LEFT), "top_left"),
            (Position(PositionShardVertical.TOP, PositionShardHorizontal.RIGHT), "top_right"),
            (Position(PositionShardVertical.BOTTOM, PositionShardHorizontal.LEFT), "bottom_left"),
            (Position(PositionShardVertical.BOTTOM, PositionShardHorizontal.RIGHT), "bottom_right"),
        ]
    )
    def test_mnemonics(self, position, expected):
        assert position.mnemonics == expected


class TestPositionFactory:
    
    def test_position_factory(self):
        obj = PositionFactory()
        assert obj
        assert len(obj._positions) == 9

    @pytest.mark.parametrize(
        "position,expected", [
            ("left", True),
            ("L", True),
            ("A", True),
            ("right", True),
            ("R", True),
            ("D", True),
            ("top", True),
            ("T", True),
            ("W", True),
            ("bottom", True),
            ("B", True),
            ("X", True),
            ("top_left", True),
            ("Q", True),
            ("top_right", True),
            ("E", True),
            ("bottom_left", True),
            ("Z", True),
            ("bottom_right", True),
            ("C", True),
            ("", True),
            ("M", True),
            ("S", True),
            # For now
            ("bottom right", False),
            ("right_bottom", False),
            ("bottom left", False),
            ("left_bottom", False),
            ("top right", False),
            ("right_top", False),
            ("top left", False),
            ("left_top", False),
        ]
    )
    def test_is_position(self, position, expected):
        assert PositionFactory().is_position(position) == expected

    @pytest.mark.parametrize(
        "position,iexpected", [
            ("left", 3),
            ("L", 3),
            ("A", 3),
            ("right", 5),
            ("R", 5),
            ("D", 5),
            ("top", 6),
            ("T", 6),
            ("W", 6),
            ("bottom", 0),
            ("B", 0),
            ("X", 0),
            ("top_left", 7),
            ("Q", 7),
            ("top_right", 8),
            ("E", 8),
            ("bottom_left", 1),
            ("Z", 1),
            ("bottom_right", 2),
            ("C", 2),
            ("", 4),
            ("M", 4),
            ("S", 4),
        ]
    )
    def test_get_position(self, position, iexpected):
        pf = PositionFactory()
        assert pf.get_position(position) == pf._positions[iexpected]

    def test_get_position(self):
        assert PositionFactory().get_position("hello") == None
