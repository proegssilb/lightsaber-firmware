
def anim_progress(anim_start_ns, anim_len_ns, current_time_ns):
    """
    Return a float between 0 and 1 representing the current animation progress.

    >>> anim_progress(15, 400, 12)
    0.0
    >>> anim_progress(100, 200, 200)
    0.5
    >>> anim_progress(15, 40, 500)
    1.0
    """
    prog_rv: float = (current_time_ns - anim_start_ns) / anim_len_ns
    return max(0.0, min(1.0, prog_rv))

if __name__ == "__main__":
    import doctest
    doctest.testmod()