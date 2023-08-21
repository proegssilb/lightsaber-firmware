import asyncio
import supervisor
import time

from adafruit_ble.services import Service
from adafruit_ble.characteristics.int import Uint16Characteristic

from domain.animations import Animation
from domain.ble import gen_service_id, make_characteristic_id_gen, CharPerms
from domain.observable import Observable
from domain.sabermodule import ConfigT, SaberModule
from domain.config import ConfigSegment
from domain.states import States, State
from domain.range import interpolate
from domain.time import anim_progress

try:
    from typing import MutableSequence, Optional, Dict
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
    anim_map: Dict[State, Animation] = dict()
    active_anim: Optional[Animation] = None

    led_brightness: Observable[int] = Observable()

    def __init__(self, animation_controller: SaberModule, anim_map: Dict[State, Animation]):
        self.animation_controller = animation_controller
        self.led_brightness.value = 0
        self.anim_start = 0
        self.anim_map = anim_map
        self.active_anim = None

    async def setup(self, config: BaselitLedRendererConfig):
        await super().setup(config)
        self.animation_controller.active_anim.watch(self.on_state_change)
    
    async def run(self):
        await super().run()
        while True:
            next_run = supervisor.ticks_ms() + 4
            
            if self.config.obj_changed():
                pass


            if self.active_anim is not None:
                led_color = self.active_anim.render_loop(time.monotonic_ns() - self.anim_start)
                self.led_brightness.value = int( 65000 * led_color.lightness)

            await asyncio.sleep_ms(next_run - supervisor.ticks_ms())

    async def on_state_change(self, new_state, old_state):
        print("Saber state changed from", old_state, "to", new_state)
        self.active_anim = self.anim_map[new_state]
        print("Switching to animation:", self.active_anim)
        self.anim_start = time.monotonic_ns()
        # TODO: Force LED to a brightness suitable for the start of the animation
        # (likely full-on/full-off?)