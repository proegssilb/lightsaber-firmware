import digitalio
import supervisor

from adafruit_ble.services import Service
from adafruit_ble.characteristics.int import Uint16Characteristic, Uint8Characteristic
from adafruit_debouncer import Debouncer
import asyncio

from domain.sabermodule import SaberModule
from domain.config import ConfigSegment
from domain.ble import gen_service_id, make_characteristic_id_gen, CharPerms
from domain.observable import Observable


SERVICE_ID = 0x00b2
mk_char_id = make_characteristic_id_gen(SERVICE_ID)

class RawButtonConfig(ConfigSegment, Service):
    uuid = gen_service_id(SERVICE_ID)

class RawButton(SaberModule):
    """Manages an illuminated button via a digital I/O and PWM. Uses said button to turn the saber on and off, doing nothing else."""
    config_type = RawButtonConfig
    button_state: Observable[bool]

    def __init__(self, button_pin, pull_direction=digitalio.Pull.DOWN):
        super(RawButton, self).__init__()
        self.__button_pin = digitalio.DigitalInOut(button_pin)
        self.__button_pin.direction = digitalio.Direction.INPUT
        self.__button_pin.pull = pull_direction
        self.__buton = Debouncer(self.__button_pin, interval=0.05)
        self.__invert_logic: bool = (pull_direction == digitalio.Pull.UP)
        self.button_state = Observable()

    async def setup(self, config: RawButtonConfig):
        await super(RawButton, self).setup(config)
        self.button_state.watch(self.on_change)

    async def run(self):
        await super(RawButton, self).run()
        while True:
            next_run = supervisor.ticks_ms() + 5

            # BLE update
            if self.config.obj_changed():
                # ...Do we need to do anything here...?
                pass

            # The pushbutton itself - normalize on pushed = true / released = false
            # (Using a bool is a temporary measure, need a more descriptive event enum)
            self.__buton.update()
            # This next line should actually be logical xor, but both sides are
            # bool, so bitwise technically works.
            self.button_state.value = bool(self.__buton.value ^ self.__invert_logic)
            await asyncio.sleep_ms(next_run - supervisor.ticks_ms())
    
    async def on_change(self, new_value, old_value):
        print("Button state changed:", new_value, ", was:", old_value)
            