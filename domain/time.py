
import time

try:
    from typing import Optional, Tuple
except ImportError:
    pass


def time2():
    reps = 10_000
    i = 1
    start = time.monotonic_ns()
    while i <= reps:
        i += 1
    stop = time.monotonic_ns()
    a = (stop - start) / reps

    i = 2**100 + 1
    step = 2**70
    stop = i + reps * step + 1
    start = time.monotonic_ns()
    while i <= stop:
        i += step
    stop = time.monotonic_ns()
    b = (stop - start) / reps

    i = 1.0
    step = 1.0
    stop = i + reps * step + 0.1
    start = time.monotonic_ns()
    while i <= stop:
        i += step
    stop = time.monotonic_ns()
    c = (stop - start) / reps

    print({'int': a, 'longint': b, 'float': c})

time2()

TTime = int

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

def anim_timeline_progress(time_from_start: TTime, *phase_lengths) -> Tuple[int, float]:
    """
    Return which phase the animation should be in, and how far through that phase we are.

    Accepts the current overall time spent in the current animation, and a list of phase 
    lengths. These "phase lengths" can also be thought of as the time between keyframes.

    Useful for interpolating between keyframes.

    >>> anim_timeline_progress(0, 500, 400, 300)
    (0, 0.0)
    >>> anim_timeline_progress(250, 500, 400, 300)
    (0, 0.5)
    >>> anim_timeline_progress(500, 500, 400, 300)
    (0, 1.0)
    >>> anim_timeline_progress(501, 500, 400, 300)
    (1, 0.0025)
    >>> anim_timeline_progress(600, 500, 400, 300)
    (1, 0.25)
    >>> anim_timeline_progress(900, 500, 400, 300)
    (1, 1.0)
    >>> anim_timeline_progress(1200, 500, 400, 300)
    (2, 1.0)
    >>> anim_timeline_progress(9001, 500, 400, 300)
    (2, 1.0)
    >>> anim_timeline_progress(250, 500, 0, 300)
    (0, 0.5)
    >>> anim_timeline_progress(650, 500, 0, 300)
    (2, 0.5)
    >>> anim_timeline_progress(500, 500, 0, 400)
    (0, 1.0)
    >>> anim_timeline_progress(501, 500, 0, 400)
    (2, 0.0025)
    """
    current_offset = TTime(0)
    for (idx, phase_len) in enumerate(phase_lengths):
        if current_offset <= time_from_start <= current_offset + phase_len:
            return (idx, (time_from_start - current_offset) / phase_len)
        else:
            current_offset += phase_len
    return (len(phase_lengths) - 1, 1.0)

def ns(x: int) -> TTime:
    """ Returns the argument as a time constant, converted from nanoseconds. """
    return x

def us(x: int) -> TTime:
    """ Returns the argument as a time constant, converted from nanoseconds. """
    return x * 1000

def ms(x: int) -> TTime:
    return x * 1_000_000

if __name__ == "__main__":
    import doctest
    doctest.testmod()