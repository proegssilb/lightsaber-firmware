
class Animations:
    """ Enum of all animations supported somewhere in this firmware. """
    # Main blade states
    NONE = 0
    OFF = 1
    ON = 100

    # Transition animations
    IGNITE = 51
    RETRACT = 52

    # Temporary/Interrupt animations
    CLASH = 110

    # Extra Accent LED animations
    SLOW_BREATHE = 501
    PULSE = 502
    