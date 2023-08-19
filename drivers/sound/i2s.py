import audiobusio
import audiomixer

from domain.sabermodule import SaberModule

class I2SSoundOut(SaberModule):
    """ A code-module of a lightsaber.

    A Saber Module manages a particular subsystem of the saber.
    """
    i2s_bus: audiobusio.I2SOut
    mixer = None

    def __init__(self, mixer, bitclock_pin, lrc_pin, data_pin):
        self.mixer = mixer
        self.i2s_bus = audiobusio.I2SOut(bitclock_pin, lrc_pin, data_pin, left_justified=False)

    async def setup(self, config):
        await super(I2SSoundOut, self).setup(config)
        self.i2s_bus.play(self.mixer, loop=True)
    
    async def run(self):
        await super(I2SSoundOut, self).run()

