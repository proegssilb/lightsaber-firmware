
def anim_progress(anim_start_ns, anim_len_ns, current_time_ns):
    """Return a float between 0 and 1 representing the current animation progress."""
    prog_rv: float = (current_time_ns - anim_start_ns) / anim_len_ns
    return max(0.0, min(1.0, prog_rv))