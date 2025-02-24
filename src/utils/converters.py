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
        if "%" in value:
            ret = float(value[:-1]) / 100
        elif "px" in value:
            ret = float(value[:-2])
    elif isinstance(value, int) or isinstance(value, float):
        ret = value
    return ret
