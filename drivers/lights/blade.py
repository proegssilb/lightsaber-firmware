from domain.observable import Observable
import pwmio

from adafruit_ble.services import Service
from adafruit_ble.characteristics.int import Uint16Characteristic

from domain.ble import gen_service_id, make_characteristic_id_gen, CharPerms
from domain.sabermodule import SaberModule

# The gen1 board has a 25% duty cycle limit due to a lack of current-regulating resistors.
MAX_BRIGHTNESS = 65535 >> 2
MIN_BRIGHTNESS = 0
SERVICE_ID = 0x7103
mk_char_id = make_characteristic_id_gen(SERVICE_ID)

class AnalogLedController(SaberModule):

    __pwm_out: pwmio.PWMOut
    __led_value_observable: Observable[int]

    def __init__(self, pin, led_brightness: Observable[int], pwm_frequency=4000):
        super(AnalogLedController, self).__init__()
        self.__pwm_out = pwmio.PWMOut(pin, frequency=pwm_frequency)
        self.__led_value_observable = led_brightness


    async def setup(self, config):
        await super(AnalogLedController, self).setup(config)
        self.__led_value_observable.watch(self.on_led_change)

    async def run(self):
        await super(AnalogLedController, self).run()

    async def on_led_change(self, new_value, old_value):
        self.__pwm_out.duty_cycle = max(min(new_value, MAX_BRIGHTNESS), MIN_BRIGHTNESS)
