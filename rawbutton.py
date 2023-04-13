import board
import digitalio
import time
import pwmio

from adafruit_ble.services import Service
from adafruit_ble.characteristics.int import Uint16Characteristic, Uint8Characteristic
from adafruit_debouncer import Debouncer



from contracts import SaberModule, States
from config import ConfigSegment
from i2c_utils import I2CDevice
from saber import Saber
from ble_utils import gen_service_id, make_characteristic_id_gen, CharPerms


SERVICE_ID = 0x00b2
mk_char_id = make_characteristic_id_gen(SERVICE_ID)

class RawOnOffButtonConfig(ConfigSegment, Service):
    uuid = gen_service_id(SERVICE_ID)
    brightness = Uint16Characteristic(uuid=mk_char_id(0x0001), initial_value=0xFFFF, properties=CharPerms.RWN)
    brightness_step = Uint8Characteristic(uuid=mk_char_id(0x0002), initial_value=0xFF, properties=CharPerms.RWN)


class ButtonAnimation:
    OFF = 1
    ON = 2
    BREATHE_UP = 3
    BREATHE_DOWN = 4


class RawOnOffButton(SaberModule):
    """Manages an illuminated button via a digital I/O and PWM. Uses said button to turn the saber on and off, doing nothing else."""
    config_type = RawOnOffButtonConfig

    def __init__(self, button_pin, led_pin):
        super(RawOnOffButton, self).__init__()
        self.button_pin = digitalio.DigitalInOut(button_pin)
        self.button_pin.direction = digitalio.Direction.INPUT
        self.button_pin.pull = digitalio.Pull.DOWN
        self.buton = Debouncer(self.button_pin, interval=0.05)
        self.led_pin = led_pin
        self.led = pwmio.PWMOut(led_pin, frequency=4000)
        self.anim_state = ButtonAnimation.BREATHE_UP

    def setup(self, config, saber: Saber):
        super(RawOnOffButton, self).setup(config, saber)

    def set_button_to_off_state(self):
        print("Setting button to off")
        self.anim_state = ButtonAnimation.OFF

    def set_button_to_snooze_state(self):
        print("Setting button to snooze")
        if self.led.duty_cycle > self.config.brightness >> 1:
            self.anim_state = ButtonAnimation.BREATHE_DOWN
        else:
            self.anim_state = ButtonAnimation.BREATHE_UP

    def set_button_to_on_state(self):
        print("Setting button to on")
        self.anim_state = ButtonAnimation.ON

    def handle_state_change(self, old_state, new_state):
        if new_state in (States.ST_IGNITE, States.ST_ON):
            self.set_button_to_on_state()
        else:
            self.set_button_to_snooze_state()

    def loop(self, frame: int, state):
        # BLE update
        if self.config.obj_changed():
            # ...Do we need to do anything here...?
            pass

        # LED Handling
        self.update_led(frame, state)

        # The pushbutton itself
        self.buton.update()
        if not self.buton.rose:
            return
        # We now know the button was clicked. So what's the new state?
        elif state == States.ST_ON:
            self.saber.request_state_change(States.ST_RETRACT)
        elif state == States.ST_OFF:
            self.saber.request_state_change(States.ST_IGNITE)

        print("Raw Button updated pushbutton state")
            
    def update_led(self, frame: int, state):
        current_brightness = self.led.duty_cycle
        if self.anim_state == ButtonAnimation.ON:
            self.led.duty_cycle = self.config.brightness
        elif self.anim_state in (ButtonAnimation.BREATHE_UP, ButtonAnimation.BREATHE_DOWN):
            max_brightness = self.config.brightness
            brightness_step = self.config.brightness_step
            # Flip animation direction if needed
            if current_brightness == 0:
                current_brightness = 0
                self.anim_state = ButtonAnimation.BREATHE_UP
            elif current_brightness >= max_brightness:
                current_brightness = self.config.brightness
                self.anim_state = ButtonAnimation.BREATHE_DOWN

            if self.anim_state == ButtonAnimation.BREATHE_UP:
                self.led.duty_cycle = min(max_brightness, self.led.duty_cycle + brightness_step)
            else:
                self.led.duty_cycle = max(0, self.led.duty_cycle - brightness_step)
            


    def deep_sleep(self):
        self.set_button_to_off_state()
        # I'd also set the button controller to sleep if it had that option.

    def sleep_resume(self):
        pass