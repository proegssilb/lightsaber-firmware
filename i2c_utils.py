
from adafruit_bus_device.i2c_device import I2CDevice
import board
import busio

_default_bus = None

def default_bus():
    if _default_bus is None:
        _default_bus = busio.I2C(board.SCL, board.SDA, frequency=1_000_000)
    return _default_bus

class I2CDevice:
    bus = None
    address = None

    def __init__(self, address: int, bus=None):
        self.bus = bus or default_bus()
        self.address = address

    def __enter__(self):
        while not self.bus.try_lock():
            pass
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.bus.unlock()

    def read_register_into(self, reg_addr: int, buffer: bytes):
        try:
            self.bus.writeto(self.address, bytes([reg_addr]))
            self.bus.readfrom_into(self.address, buffer)
        except OSError as e:
            if e.errno in (116, 19):
                # Known issue.
                pass
            else:
                raise

    def write_register(self, reg_addr: int, data: bytes):
        dbuff = bytes([reg_addr]) + data
        try:
            self.bus.writeto(self.address, dbuff)
        except OSError as e:
            if e.errno in (116, 19):
                # Known issue.
                pass
            else:
                raise