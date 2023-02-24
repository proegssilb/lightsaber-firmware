import audiobusio
import audiomixer

from contracts import SaberModule

class I2SSoundOut(SaberModule):
    """ A code-module of a lightsaber.

    A Saber Module manages a particular subsystem of the saber.
    """
    i2s_bus = None
    mixer = None

    def __init__(self, mixer, bitclock_pin, lrc_pin, data_pin):
        self.mixer = mixer
        self.i2s_bus = audiobusio.I2SOut(bitclock_pin, lrc_pin, data_pin)

    def setup(self, config, saber):
        super(I2SSoundOut, self).setup(config, saber)
        print("Setting i2s playing")
        self.i2s_bus.play(self.mixer, loop=True)

