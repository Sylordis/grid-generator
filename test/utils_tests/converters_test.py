import pytest

from utils.converters import is_percentile, str_to_number, Converters


@pytest.mark.parametrize("input", ["5%", 0.9, "100%", "37232%", 0.1, 0])
def test_is_percentile(input):
    assert is_percentile(input)


@pytest.mark.parametrize("input", [5, "abc", 1.1])
def test_is_percentile_not(input):
    assert not is_percentile(input)


@pytest.mark.parametrize(
    "input,expected",
    [
        (0, 0),
        ("0", 0),
        (329123, 329123),
        ("1.483029", 1.483029),
        ("100%", 1),
        ("95%", 0.95),
        ("238px", 238),
    ],
)
def test_str_to_number(input, expected):
    assert str_to_number(input) == expected


class TestConverters:

    @pytest.mark.parametrize(
        "number,precision,expected",
        [
            (0, 0, 0),
            (1.54, 0, 2),
            (1.483029, 2, 1.48),
        ],
    )
    def test_to_float(self, number, precision, expected):
        method = Converters.to_float(precision)
        assert method(number) == expected
