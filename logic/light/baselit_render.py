import asyncio
import supervisor
import time

from adafruit_ble.services import Service
from adafruit_ble.characteristics.int import Uint16Characteristic

from domain.ble import gen_service_id, make_characteristic_id_gen, CharPerms
from domain.observable import Observable
from domain.sabermodule import ConfigT, SaberModule
from domain.config import ConfigSegment
from domain.animations import Animations
from domain.range import interpolate
from logic.time import anim_progress

try:
    from typing import MutableSequence, Optional
except ImportError:
    pass

SERVICE_ID = 0x309d
mk_char_id = make_characteristic_id_gen(SERVICE_ID)

class BaselitLedRendererConfig(Service, ConfigSegment):
    uuid = gen_service_id(SERVICE_ID)
    max_brightness = Uint16Characteristic(uuid=mk_char_id(0x0001), properties=CharPerms.RWN, max_value=65535, initial_value=16000)

class BaselitRenderer(SaberModule):
    config_type = BaselitLedRendererConfig

    animation_controller: SaberModule
    anim_start: int = 0
    anim_time = 1_000_000_000 # TODO: Adjust this for variable frame rate

    led_brightness: Observable[int] = Observable()
    active_anim: Observable[int]

    def __init__(self, animation_controller: SaberModule):
        self.animation_controller = animation_controller
        self.active_anim = animation_controller.active_anim
        self.led_brightness.value = 0
        self.anim_start = 0
        

    async def setup(self, config: BaselitLedRendererConfig):
        await super().setup(config)
        self.animation_controller.active_anim.watch(self.on_anim_change)
    
    async def run(self):
        await super().run()
        while True:
            next_run = supervisor.ticks_ms() + 4
            
            if self.config.obj_changed():
                pass

            if self.active_anim.value == Animations.ON:
                self.led_brightness.value = self.config.max_brightness
            elif self.active_anim.value == Animations.OFF:
                self.led_brightness.value = 0
            elif self.active_anim.value == Animations.IGNITE:
                frame = anim_progress(self.anim_start, self.anim_time, time.monotonic_ns())
                led_val = int(interpolate(0, self.config.max_brightness, frame))
                print("Animating blade. Frame:", frame, "LED Val:", led_val)
                self.led_brightness.value = led_val
            elif self.active_anim.value == Animations.RETRACT:
                frame = anim_progress(self.anim_start, self.anim_time, time.monotonic_ns())
                led_val = int(interpolate(self.config.max_brightness, 0, frame))
                print("Animating blade. Frame:", frame, "LED Val:", led_val)
                self.led_brightness.value = led_val

            await asyncio.sleep_ms(next_run - supervisor.ticks_ms())

    async def on_anim_change(self, new_anim, old_anim):
        print("LED animation changed from", old_anim, "to", new_anim)
        self.anim_start = time.monotonic_ns()
        # TODO: Force LED to a brightness suitable for the start of the animation
        # (likely full-on/full-off?)