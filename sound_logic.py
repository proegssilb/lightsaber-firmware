import audiomixer
import audiocore

from adafruit_ble.services import Service
from adafruit_ble.characteristics.float import FloatCharacteristic

from ble_utils import gen_service_id, make_characteristic_id_gen, CharPerms
from contracts import SaberModule, States
from config import ConfigSegment


SERVICE_ID = 0x309f
mk_char_id = make_characteristic_id_gen(SERVICE_ID)

class BasicSoundConfig(Service, ConfigSegment):
    uuid = gen_service_id(SERVICE_ID)
    hum_volume = FloatCharacteristic(uuid=mk_char_id(0x0001), initial_value=0.9, properties=CharPerms.RWN)
    ignite_volume = FloatCharacteristic(uuid=mk_char_id(0x0002), initial_value=0.9, properties=CharPerms.RWN)
    retract_volume = FloatCharacteristic(uuid=mk_char_id(0x0003), initial_value=0.9, properties=CharPerms.RWN)

class BasicSoundLogic(SaberModule):
    mixer: audiomixer.Mixer = None
    config_type = BasicSoundConfig

    def __init__(self, sample_rate=44100, channel_count=1, bits_per_sample=16):
        self.mixer = audiomixer.Mixer(voice_count = 2, channel_count=channel_count, bits_per_sample=bits_per_sample, sample_rate=sample_rate)
        self.wave_file = None

    def setup(self, config, saber):
        super(BasicSoundLogic, self).setup(config, saber)

    def change_sound_font(self, new_font):
        pass

    def play_sample(self, level, file_name, loop_sound=False):
        for v in self.mixer.voice:
                v.stop()
        if self.wave_file is not None:
            self.wave_file.close()

        print("Sound stopped, playing new sound:", file_name)
        self.mixer.voice[0].level = level
        self.wave_file = open(file_name, "rb")
        sample = audiocore.WaveFile(self.wave_file)
        self.mixer.voice[0].play(sample, loop = loop_sound)

    def handle_state_change(self, old_state, new_state):
        # Start playing a sound based on the current state
        if new_state == States.ST_IGNITE:
            self.play_sample(self.config.ignite_volume, "/sd/SmthJedi/out01.wav")
        elif new_state == States.ST_ON:
            self.play_sample(self.config.hum_volume, "/sd/SmthJedi/hum01.wav", loop_sound=True)
        elif new_state == States.ST_RETRACT:
            self.play_sample(self.config.retract_volume, "/sd/SmthJedi/in01.wav")
    
    def loop(self, frame: int, state):
        if self.config.obj_changed():
            # Update the volume in the mixer based on what sound we're playing right now.
            if state == States.ST_IGNITE:
                self.mixer.voice[0].level = self.config.ignite_volume
            elif state == States.ST_ON:
                print("New level:", self.config.hum_volume)
                self.mixer.voice[0].level = self.config.hum_volume
            elif state == States.ST_RETRACT:
                self.mixer.voice[0].level = self.config.retract_volume
