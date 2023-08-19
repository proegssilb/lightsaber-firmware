import os

import board
import microcontroller as mcu
import sdcardio
import storage
import busio

from domain.sabermodule import SaberModule

class SdStorage(SaberModule):
    """ Makes SD Card available for use as a storage medium. """
    spi: busio.SPI
    cs: mcu.Pin

    def __init__(self, spi_bus: busio.SPI, cs_pin: mcu.Pin):
        self.spi = spi_bus
        self.cs = cs_pin

    async def setup(self, config):
        await super(SdStorage, self).setup(config)
        sd = sdcardio.SDCard(self.spi, self.cs)
        vfs = storage.VfsFat(sd) # type: ignore (You need circuitpython_typing to get this right)
        print("Read-only before mounting:", vfs.readonly)
        storage.mount(vfs, '/sd', readonly=False)
        print("Read-only after mounting:", vfs.readonly)
