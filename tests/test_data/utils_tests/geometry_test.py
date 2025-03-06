import math
import pytest

from utils.geometry import Angle, AngleMeasurement, Position, rotate


class TestPosition:

    def test_iter(self):
        pos = Position(1, 2)
        x, y = pos
        assert x == 1
        assert y == 2

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (Position(0, 0), Position(0, 0), Position(0, 0)),
            (Position(0, 0), Position(1, 2), Position(1, 2)),
            (Position(3, 4), Position(-3, -4), Position(0, 0)),
        ],
    )
    def test_add(self, a, b, expected):
        c = a + b
        assert expected == c

    @pytest.mark.parametrize(
        "position,converter,expected",
        [
            (Position(0, 0), lambda x: x, Position(0, 0)),
            (Position(0, 0), lambda x: x + 1, Position(1, 1)),
            (Position(3.2, 4.56), lambda x: round(x, 0), Position(3, 5)),
        ],
    )
    def test_and(self, position, converter, expected):
        assert position & converter == expected

    @pytest.mark.parametrize(
        "pos,s,expected",
        [
            (Position(0, 0), 0, 0),
            (Position(3213, 4123), 0, 3213),
            (Position(3213, 4123), 1, 4123),
            (Position(192, 123), slice(0, 1), [192]),
            (Position(192, 123), slice(0, 2), [192, 123]),
        ],
    )
    def test_getitem(self, pos, s, expected):
        assert pos[s] == expected

    @pytest.mark.parametrize(
        "pos,expected",
        [
            (Position(0, 0), Position(0, 0)),
            (Position(-1, 0), Position(1, 0)),
            (Position(0, -128), Position(0, 128)),
            (Position(2, 5), Position(-2, -5)),
            (Position(-4, 8), Position(4, -8)),
        ],
    )
    def test_neg(self, pos, expected):
        assert -pos == expected


class TestAngle:

    @pytest.mark.parametrize(
        "degrees,radians",
        [
            (90, math.pi / 2),
            (45, math.pi / 4),
            (0, 0),
            (360, 2 * math.pi),
            (-56, (360 - 56) * math.pi / 180),
        ],
    )
    def test_init(self, degrees, radians):
        angle = Angle(degrees)
        assert angle.degrees == degrees % 360
        assert angle.radians == radians % (2 * math.pi)

    @pytest.mark.parametrize(
        "angle,angle_type,expected",
        [
            (36, None, 36),
            (720, None, 0),
            (math.pi, AngleMeasurement.RADIANS, 180),
            (3 * math.pi / 4, AngleMeasurement.RADIANS, 135),
            (3 * math.pi / 2, AngleMeasurement.RADIANS, 270),
        ],
    )
    def test_eq(self, angle, angle_type, expected):
        assert Angle(angle, angle_type) == Angle(expected)

    @pytest.mark.parametrize("angle,expected", [(36, -36), (720, 0), (0, 0)])
    def test_neg(self, angle, expected):
        assert -Angle(angle) == Angle(expected)

    @pytest.mark.parametrize(
        "angle_a,angle_b,expected",
        [
            (0, 0, 0),
            (56, 0, 56),
            (0, 4, -4),
            (89, 2, 87),
            (720, 2, -2),
            (-28, 24, -52),
            (-564, -564, 0),
        ],
    )
    def test_sub(self, angle_a, angle_b, expected):
        assert Angle(angle_a) - Angle(angle_b) == Angle(expected)


@pytest.mark.parametrize(
    "position, angle, expected",
    [
        (Position(0, 0), 0, Position(0, 0)),
        (Position(1, 0), 90, Position(0, 1)),
        (Position(1, 0), -90, Position(0, -1)),
        (Position(1, 0), 180, Position(-1, 0)),
        (Position(1, 0), -180, Position(-1, 0)),
        (Position(1, 0), 360, Position(1, 0)),
        (Position(1, 0), -360, Position(1, 0)),
        (Position(1, 0), 45, Position(math.sqrt(2) / 2, math.sqrt(2) / 2)),
    ],
)
def test_rotate(position, angle, expected):
    nx, ny = rotate(position, Angle(angle))
    ex, ey = expected
    assert math.isclose(nx, ex, abs_tol=1e-8)
    assert math.isclose(ny, ey, abs_tol=1e-8)
