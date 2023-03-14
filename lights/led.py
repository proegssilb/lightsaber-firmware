import pwmio

from contracts import SaberModule, States
from saber import Saber

class AnalogLedController(SaberModule):
    pwm_out = None
    max_brightness = 65535
    min_brightness = 0
    anim_time = 50 # TODO: Adjust this for variable frame rate
    brightness_per_step = (max_brightness - min_brightness) // anim_time

    def __init__(self, pin, max_brightness=65535):
        super(AnalogLedController, self).__init__()
        self.pwm_out = pwmio.PWMOut(pin)
        self.max_brightness = max_brightness

    def setup(self, config, saber: Saber):
        super(AnalogLedController, self).setup(config, saber)

    def handle_state_change(self, old_state, new_state):
        if new_state == States.ST_ON:
            self.pwm_out.duty_cycle = self.max_brightness
        elif new_state == States.ST_OFF:
            self.pwm_out.duty_cycle = 0
        elif new_state == States.ST_IGNITE:
            self.pwm_out.duty_cycle = 0
        elif new_state == States.ST_RETRACT:
            self.pwm_out.duty_cycle = self.max_brightness

    def loop(self, frame: int, state):
        if state == States.ST_IGNITE:
            self.pwm_out.duty_cycle = min(self.pwm_out.duty_cycle + self.brightness_per_step, self.max_brightness)
        elif state == States.ST_RETRACT:
            self.pwm_out.duty_cycle = max(self.pwm_out.duty_cycle - self.brightness_per_step, 0)