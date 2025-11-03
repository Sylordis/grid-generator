from typing import Callable, Any


def is_percentile(value) -> bool:
    """
    Takes a value and check if it's a percentile number.
    This method will consider any string with a "%" or any number between 1 and 0 as
    being percentile.

    :param value: a value to check if it is percentile
    :return: True if the value is a string and contains "%" or if it is between 1 and 0,
    false otherwise.
    """
    return (
        isinstance(value, str)
        and "%" in value
        or isinstance(value, (int, float))
        and 0 <= value <= 1
    )


def str_to_number(value) -> float:
    """
    Takes a string measurement and converts it to an actual value.
    For example:
    - `90%` => 0.9
    - `15px` => 15
    - any number to the same number

    :param value: value to convert
    :return: a value or 0 if it cannot be converted
    """
    ret = 0
    if isinstance(value, str):
        if value.endswith("%"):
            ret = float(value[:-1]) / 100
        elif value.endswith("px"):
            ret = float(value[:-2])
        else:
            ret = float(value)
    elif isinstance(value, (float, int)):
        ret = value
    return ret


def apply_all(m: Callable[[], Any], *values) -> tuple:
    """
    Applies a method to all provided values and return all values as a tuple to be unpacked.

    :param m: a method to apply to all values
    :param values: all values to process
    :return: a tuple of all values that have been passed through the method
    """
    return tuple([m(v) for v in values])


class Converters:
    "Simple static methods to create callables to convert data from one type to another."

    @staticmethod
    def to_float(precision: int) -> Callable[[Any], float]:
        "Float converter to reduce to a specific precision."
        return lambda x: round(x, precision)
