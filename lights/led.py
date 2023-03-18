import pwmio

from adafruit_ble.services import Service
from adafruit_ble.characteristics.int import Uint16Characteristic

from ble_utils import gen_service_id, make_characteristic_id_gen, CharPerms
from config import ConfigSegment
from contracts import SaberModule, States
from saber import Saber


MAX_BRIGHTNESS = 65535
MIN_BRIGHTNESS = 0
SERVICE_ID = 0x7103
mk_char_id = make_characteristic_id_gen(SERVICE_ID)

class AnalogLedConfig(Service, ConfigSegment):
    uuid = gen_service_id(SERVICE_ID)
    max_brightness = Uint16Characteristic(uuid=mk_char_id(0x0001), initial_value=MAX_BRIGHTNESS, properties=CharPerms.RWN)
    min_brightness = Uint16Characteristic(uuid=mk_char_id(0x0002), initial_value=MIN_BRIGHTNESS, properties=CharPerms.RWN)
    brightness = Uint16Characteristic(uuid=mk_char_id(0x0003), initial_value=MAX_BRIGHTNESS, properties=CharPerms.RWN)

class AnalogLedController(SaberModule):
    config_type = AnalogLedConfig

    pwm_out = None
    anim_time = 50 # TODO: Adjust this for variable frame rate
    brightness_per_step = 1

    def __init__(self, pin):
        super(AnalogLedController, self).__init__()
        self.pwm_out = pwmio.PWMOut(pin)

    def setup(self, config, saber: Saber):
        super(AnalogLedController, self).setup(config, saber)

        # TODO: Lazy compute this.
        self.brightness_per_step = (self.config.max_brightness - self.config.min_brightness) // self.anim_time


    def handle_state_change(self, old_state, new_state):
        if new_state == States.ST_ON:
            self.pwm_out.duty_cycle = self.config.brightness
        elif new_state == States.ST_OFF:
            self.pwm_out.duty_cycle = self.config.min_brightness
        elif new_state == States.ST_IGNITE:
            self.pwm_out.duty_cycle = self.config.min_brightness
        elif new_state == States.ST_RETRACT:
            self.pwm_out.duty_cycle = self.config.brightness

    def loop(self, frame: int, state):
        if state == States.ST_IGNITE:
            self.pwm_out.duty_cycle = min(self.pwm_out.duty_cycle + self.brightness_per_step, self.config.brightness)
        elif state == States.ST_RETRACT:
            self.pwm_out.duty_cycle = max(self.pwm_out.duty_cycle - self.brightness_per_step, self.config.min_brightness)
        elif self.config.obj_changed():
            if state == States.ST_ON:
                self.pwm_out.duty_cycle = self.config.brightness
            else:
                self.pwm_out.duty_cycle = self.config.min_brightness
