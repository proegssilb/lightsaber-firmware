import os

import board
import sdcardio
import storage

from contracts import SaberModule

class SdStorage(SaberModule):
    """ Makes SD Card available for use as a storage medium. """
    spi = None
    cs = None

    def __init__(self, spi_bus, cs_pin):
        self.spi = spi_bus
        self.cs = cs_pin

    def setup(self, config, saber):
        super(SdStorage, self).setup(config, saber)
        sd = sdcardio.SDCard(self.spi, self.cs)
        vfs = storage.VfsFat(sd)
        storage.mount(vfs, '/sd')
