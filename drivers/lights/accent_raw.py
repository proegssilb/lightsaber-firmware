import board
import digitalio
import supervisor
import pwmio

from adafruit_ble.services import Service
from adafruit_ble.characteristics.int import Uint32Characteristic
import asyncio

from domain.sabermodule import SaberModule
from domain.config import ConfigSegment
from domain.ble import gen_service_id, make_characteristic_id_gen, CharPerms
from domain.observable import Observable
from domain.anim_steps import ConstantBrightness, AnimStep


SERVICE_ID = 0x00b3
mk_char_id = make_characteristic_id_gen(SERVICE_ID)

class RawAccentLedConfig(ConfigSegment, Service):
    uuid = gen_service_id(SERVICE_ID)
    frame_time_ms = Uint32Characteristic(uuid=mk_char_id(0x0001), initial_value=1_000_000//60, properties=CharPerms.RWN)

DEFAULT_ANIM_PHASE = ConstantBrightness(0, 900_000_000)

class RawAccentLed(SaberModule[RawAccentLedConfig]):
    """ 
    Runs an accent LED, as you'd see in a button or crystal chamber. 

    Consumes an Observable of what the animation is supposed to be, and uses PWM
    to drive an LED through the animation.
    """

    config_type = RawAccentLedConfig
    led_pin = None
    led: pwmio.PWMOut
    anim_pattern: Observable[list[AnimStep]]
    anim_phase: AnimStep = DEFAULT_ANIM_PHASE
    time_step: int = 0

    
    def __init__(self, led_pin, anim_pattern: Observable[list[AnimStep]]) -> None:
        super().__init__()
        self.led_pin = led_pin
        self.led = pwmio.PWMOut(led_pin, frequency=4000)
        self.anim_pattern = anim_pattern
        self.time_step: int = 0
        self.anim_phase = self.anim_pattern.value[0] if len(self.anim_pattern.value) > 0 else DEFAULT_ANIM_PHASE

    
    async def setup(self, config: RawAccentLedConfig):
        await super(RawAccentLed, self).setup(config)
        self.anim_pattern.watch(self.on_anim_change)

    async def run(self):

        while True:
            next_run = supervisor.ticks_ms() + self.config.frame_time_ms

            if self.config.obj_changed():
                # ...Do we need to do anything here...?
                pass

            self.led.duty_cycle = self.anim_phase.get_value_at_time(self.time_step)

            self.time_step += self.config.frame_time_ms

            # TODO: Find a better way to do this.
            await asyncio.sleep_ms(next_run - supervisor.ticks_ms())

    async def on_anim_change(self, new_anim: list):
        if len(new_anim) == 0:
            self.anim_phase = DEFAULT_ANIM_PHASE
        else:
            self.anim_phase = new_anim[0]
        self.time_step = 0