# States

class States:
    ST_OFF = 1000
    ST_IGNITE = 1005
    ST_ON = 1010
    ST_RETRACT = 1015
    ST_SLEEP = 1020
    DEFAULT = ST_OFF

# Modularity

class SaberModule:
    """ A code-module of a lightsaber.

    A Saber Module manages a particular subsystem of the saber.
    """
    saber = None
    config = None

    def setup(self, config, saber):
        """ Do any first-power-on setup the subsystem needs to do. """
        self.config = config
        self.saber = saber

    def handle_state_change(self, old_state, new_state):
        """
        Do a tiny amount of work (< 500 us) needed to prep for changing states.

        This is _not_ for animating. Animations should all be dedicated saber states.
        """
        pass

    def loop(self, frame: int, state):
        """"
        Do everything you need to do for the next ~10ms.

        frame: The current frame number in the current state. Can wrap, but you get at least 65k frames.

        state: The current state of the saber.

        Note: This should be kept short. Avoid loops, avoid sleeping. Use a state machine instead.
        """
        pass

    def deep_sleep(self):
        """ Get ready for complete CPU suspension and/or a hard power cut."""
        pass

    def sleep_resume(self):
        """ Resume coming out of a deep sleep. """
        pass

