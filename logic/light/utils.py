

def interpolate(a_val, b_val, progress: float):
    """
    Perform a Linear Interpolation between A and B.
    
    A and B must support arithmetic with floats.
    """
    return (b_val - a_val) * progress + a_val