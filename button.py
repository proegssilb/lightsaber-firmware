import board
import busio
from i2c_utils import I2CDevice

from contracts import SaberModule, States
from saber import Saber

class OnOffButton(SaberModule):
    default_brightness = 0x40
    clear_state_register = bytes([0x00])

    i2c_address = 0x6F
    button = None
    state_register = 0x03
    clicked_bitmask = 0x02
    led_brightness_register = 0x19
    led_step_count_register = 0x1A
    led_pulse_on_register = 0x1C
    led_pulse_off_register = 0x1E

    def __init__(self, i2c_address=None):
        super(OnOffButton, self).__init__()

        # If the user supplied an address, use it. Else, use our default.
        self.i2c_address = i2c_address or self.i2c_address

    def setup(self, config, saber: Saber):
        super(OnOffButton, self).setup(config, saber)

    def set_button_to_off_state(self):
        with I2CDevice(self.i2c_address) as button:
            button.write_register(self.led_brightness_register, bytes([0x00]))
            button.write_register(self.led_step_count_register, bytes([0x0F]))
            button.write_register(self.led_pulse_on_register, bytes([0x00, 0x00]))
            button.write_register(self.led_pulse_off_register, bytes([0x00, 0xFF]))

    def set_button_to_snooze_state(self):
        with I2CDevice(self.i2c_address) as button:
            button.write_register(self.led_brightness_register, bytes([self.default_brightness]))
            button.write_register(self.led_step_count_register, bytes([0x0F]))
            button.write_register(self.led_pulse_on_register, bytes([0x07, 0xD0]))
            button.write_register(self.led_pulse_off_register, bytes([0x00, 0xFF]))

    def set_button_to_on_state(self):
        with I2CDevice(self.i2c_address) as button:
            button.write_register(self.led_brightness_register, bytes([self.default_brightness]))
            button.write_register(self.led_step_count_register, bytes([0x0F]))
            button.write_register(self.led_pulse_on_register, bytes([0x00, 0x00]))
            button.write_register(self.led_pulse_off_register, bytes([0x00, 0xFF]))

    def handle_state_change(self, old_state, new_state):
        if new_state in (States.ST_IGNITE, States.ST_ON):
            self.set_button_to_on_state()
        else:
            self.set_button_to_snooze_state()

    def loop(self, frame: int, state):
        is_clicked = False
        out_data = bytearray(1)
        with I2CDevice(self.i2c_address) as button:
            button.read_register_into(self.state_register, out_data)
            button.write_register(self.state_register, self.clear_state_register)
        if out_data[0] != 0:
            print("Button data:", out_data[0])
        is_clicked = bool(out_data[0] & 0x02)
        if not is_clicked:
            return
        elif state == States.ST_ON:
            # We already know the button was clicked.
            self.saber.request_state_change(States.ST_RETRACT)
        elif state == States.ST_OFF:
            self.saber.request_state_change(States.ST_IGNITE)

    def deep_sleep(self):
        self.set_button_to_off_state()
        # I'd also set the button controller to sleep if it had that option.

    def sleep_resume(self):
        # Handle register setting when we get the state change message
        pass