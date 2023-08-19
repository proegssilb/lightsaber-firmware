def clamp_to_range(min_val, max_val, input):
    """
    Clamp given input to the inclusive range given by min_val and max_val.

    >>> clamp_to_range(1, 10, 1)
    1
    >>> clamp_to_range(1, 10, 0)
    1
    >>> clamp_to_range(1.0, 10.0, 0)
    1.0
    >>> clamp_to_range(1.0, 10.0, 5)
    5
    >>> clamp_to_range(1, 10, 11.0)
    10
    """
    if input < min_val:
        return min_val
    elif input > max_val:
        return max_val
    else:
        return input


def interpolate(a_val, b_val, progress: float):
    """
    Perform a Linear Interpolation between A and B.

    A and B must support arithmetic with floats.

    >>> interpolate(0, 100, 0.0)
    0.0
    >>> interpolate(0, 100, 0.5)
    50.0
    >>> interpolate(0, 100, 1.0)
    100.0
    >>> interpolate(0, 100, 1.1)
    100.0
    >>> interpolate(0, 100, -0.1)
    0.0
    >>> interpolate(100, 0, 0.75)
    25.0
    """
    progress = clamp_to_range(0.0, 1.0, progress)
    return (b_val - a_val) * progress + a_val

if __name__ == "__main__":
    import doctest
    doctest.testmod()


