import pwmio

from contracts import SaberModule, States
from saber import Saber

MAX_BRIGHTNESS = 65535
MIN_BRIGHTNESS = 0

class AnalogLedController(SaberModule):
    pwm_out = None
    anim_time = 50 # TODO: Adjust this for variable frame rate
    brightness_per_step = 1

    # TODO: Constrain these to range
    max_brightness = property(*SaberModule.build_config_prop_args('MAX_BRIGHTNESS'))
    min_brightness = property(*SaberModule.build_config_prop_args('MIN_BRIGHTNESS'))
    config_brightness = property(*SaberModule.build_config_prop_args('CURRENT_BRIGHTNESS'))

    def __init__(self, pin, max_brightness=65535):
        super(AnalogLedController, self).__init__()
        self.pwm_out = pwmio.PWMOut(pin)

    def setup(self, config, saber: Saber):
        super(AnalogLedController, self).setup(config, saber)

        self.config.process_config_default('MAX_BRIGHTNESS', MAX_BRIGHTNESS)
        self.config.process_config_default('MIN_BRIGHTNESS', MIN_BRIGHTNESS)
        self.config.process_config_default('CURRENT_BRIGHTNESS', MAX_BRIGHTNESS)

        # TODO: Lazy compute this.
        self.brightness_per_step = (self.max_brightness - self.min_brightness) // self.anim_time


    def handle_state_change(self, old_state, new_state):
        if new_state == States.ST_ON:
            self.pwm_out.duty_cycle = self.config_brightness
        elif new_state == States.ST_OFF:
            self.pwm_out.duty_cycle = self.min_brightness
        elif new_state == States.ST_IGNITE:
            self.pwm_out.duty_cycle = self.min_brightness
        elif new_state == States.ST_RETRACT:
            self.pwm_out.duty_cycle = self.config_brightness

    def loop(self, frame: int, state):
        if state == States.ST_IGNITE:
            self.pwm_out.duty_cycle = min(self.pwm_out.duty_cycle + self.brightness_per_step, self.config_brightness)
        elif state == States.ST_RETRACT:
            self.pwm_out.duty_cycle = max(self.pwm_out.duty_cycle - self.brightness_per_step, 0)