import audiomixer
import audiocore
import asyncio
import supervisor

from adafruit_ble.services import Service
from adafruit_ble.characteristics.float import FloatCharacteristic

from domain.ble import gen_service_id, make_characteristic_id_gen, CharPerms
from domain.observable import Observable
from domain.sabermodule import SaberModule
from domain.config import ConfigSegment
from domain.states import States

try:
    from typing import MutableSequence, Optional

    from io import FileIO
except ImportError:
    pass

SERVICE_ID = 0x309f
mk_char_id = make_characteristic_id_gen(SERVICE_ID)

class BasicSoundConfig(Service, ConfigSegment):
    uuid = gen_service_id(SERVICE_ID)
    hum_volume = FloatCharacteristic(uuid=mk_char_id(0x0001), initial_value=0.9, properties=CharPerms.RWN)
    ignite_volume = FloatCharacteristic(uuid=mk_char_id(0x0002), initial_value=0.9, properties=CharPerms.RWN)
    retract_volume = FloatCharacteristic(uuid=mk_char_id(0x0003), initial_value=0.9, properties=CharPerms.RWN)
    hum_duck_volume = FloatCharacteristic(uuid=mk_char_id(0x0004), initial_value=0.01, properties=CharPerms.RWN)

class BasicSoundLogic(SaberModule):
    mixer: audiomixer.Mixer
    config_type = BasicSoundConfig
    base_anim: Observable[int]
    interrupt_anim: Observable[int]
    wave_files: MutableSequence[Optional[FileIO]]
    interrupt_was_playing: bool = False

    def __init__(self, animation_controller: SaberModule, sample_rate=44100, channel_count=1, bits_per_sample=16):
        self.mixer = audiomixer.Mixer(voice_count = 2, channel_count=channel_count, bits_per_sample=bits_per_sample, sample_rate=sample_rate)
        self.wave_files = list((None, None))
        self.animation_controller = animation_controller
        self.interrupt_was_playing = False

    async def setup(self, config):
        await super(BasicSoundLogic, self).setup(config)
        self.base_anim = self.animation_controller.base_anim
        self.interrupt_anim = self.animation_controller.interrupt_anim
        self.base_anim.watch(self.on_base_anim_change)
        self.interrupt_anim.watch(self.on_interrupt_anim_change)

    async def run(self):
        await super().run()
        while True:
            next_run = supervisor.ticks_ms() + 2

            if self.config.obj_changed():
                # Update the volume in the mixer based on what sound we're playing right now.
                if self.base_anim.value == States.OFF:
                    self.mixer.voice[0].level = 0
                elif self.interrupt_anim.value is not None:
                    self.mixer.voice[0].level = self.config.hum_duck_volume
                else:
                    self.mixer.voice[0].level = self.config.hum_volume
                
                if self.interrupt_anim.value is None:
                    self.mixer.voice[1].level = 0
                elif self.interrupt_anim.value == States.IGNITE:
                    self.mixer.voice[1].level = self.config.ignite_volume
                elif self.interrupt_anim.value == States.RETRACT:
                    self.mixer.voice[1].level = self.config.retract_volume
            
            if self.interrupt_anim.value is not None and self.interrupt_was_playing \
                    and not self.mixer.voice[1].playing:
                # Don't continue firing this event
                self.interrupt_was_playing = False
                # Signal to the animation controller that the animation is done
                self.animation_controller.anim_finished.value = True

            await asyncio.sleep_ms(next_run - supervisor.ticks_ms())

    async def on_base_anim_change(self, new_anim, old_anim):
        if new_anim == States.ON:
            self.play_sample(0, self.config.hum_volume, "/sd/SmthJedi/hum01.wav", True)
        elif new_anim == States.OFF:
            self.stop_voice(0)

    async def on_interrupt_anim_change(self, new_anim, old_anim):
        print("Mixer received interrupt anim change from", old_anim, "to", new_anim )
        if new_anim is None:
            print("Mixer not playing interrupt")
            self.stop_voice(1)
            self.unduck_main()
            self.interrupt_was_playing = False
        elif new_anim is States.IGNITE:
            print("Mixer playing ignite")
            self.duck_main()
            self.play_sample(1, self.config.ignite_volume, "/sd/SmthJedi/out01.wav", False)
            self.interrupt_was_playing = True
        elif new_anim is States.RETRACT:
            print("Mixer playing retract")
            self.duck_main()
            self.play_sample(1, self.config.ignite_volume, "/sd/SmthJedi/in01.wav", False)
            self.interrupt_was_playing = True

    def stop_voice(self, voice_num: int):
        self.mixer.voice[voice_num].level = 0
        self.mixer.voice[voice_num].stop()

    def play_sample(self, voice_num: int, level: float, file_name: str, loop_sound: bool = False):
        self.mixer.voice[voice_num].stop()
        if self.wave_files[voice_num] is not None:
            self.wave_files[voice_num].close()
        
        self.mixer.voice[voice_num].level = level
        wave_data: FileIO = open(file_name, "rb")
        self.wave_files[voice_num] = wave_data
        sample = audiocore.WaveFile(wave_data)
        self.mixer.voice[voice_num].play(sample, loop = loop_sound)

    def duck_main(self):
        print("Ducking main volume")
        self.mixer.voice[0].level = self.config.hum_duck_volume

    def unduck_main(self):
        print("Unducking main volume")
        self.mixer.voice[0].level = self.config.hum_volume

