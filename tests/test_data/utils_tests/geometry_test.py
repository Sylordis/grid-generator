import math
import pytest

from utils.geometry import Angle, Position, rotate


def test_position_iter():
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
def test_position_add(a, b, expected):
    c = a + b
    assert expected == c


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
def test_position_getitem(pos, s, expected):
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
def test_position_neg(pos, expected):
    assert -pos == expected


@pytest.mark.parametrize(
    "degrees,radians",
    [
        (90, math.pi / 2),
        (45, math.pi / 4),
        (0, 0),
        (360, 2 * math.pi),
        (-56, -56 * math.pi / 180),
    ],
)
def test_angle(degrees, radians):
    angle = Angle(degrees)
    assert angle.degrees == degrees
    assert angle.radians == radians


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
