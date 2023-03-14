import audiomixer
import audiocore

from contracts import SaberModule, States

class Effects:
    HUM = 0
    IGNITE = 1
    RETRACT = 2

class BasicSoundLogic(SaberModule):
    master_volume = property(*SaberModule.build_config_prop_args('MASTER_VOLUME'))

    """ Which audiomixer.Mixer instance should be used for playing sounds. Should support 2+ voices."""
    mixer = None

    volumes = {
        Effects.HUM: .9,
        Effects.IGNITE: .9,
        Effects.RETRACT: .9,
        }

    def __init__(self, sample_rate=44100, channel_count=1, bits_per_sample=16):
        self.mixer = audiomixer.Mixer(voice_count = 2, channel_count=channel_count, bits_per_sample=bits_per_sample, sample_rate=sample_rate)
        self.wave_file = None

    def setup(self, config, saber):
        super(BasicSoundLogic, self).setup(config, saber)
        self.config.process_config_default('MASTER_VOLUME', 0.9)

    def change_sound_font(self, new_font):
        pass

    def play_sample(self, level, file_name):
        for v in self.mixer.voice:
                v.stop()
        if self.wave_file is not None:
            self.wave_file.close()

        self.mixer.voice[0].level = level
        self.wave_file = open(file_name, "rb")
        sample = audiocore.WaveFile(self.wave_file)
        self.mixer.voice[0].play(sample, loop = True)

    def handle_state_change(self, old_state, new_state):
        if new_state == States.ST_OFF:
            print("Stopping sound")
            for v in self.mixer.voice:
                v.stop()
        elif new_state == States.ST_IGNITE:
            self.play_sample(self.volumes[Effects.HUM], "/sd/TeensySF/out01.wav")
        elif new_state == States.ST_ON:
            self.play_sample(self.volumes[Effects.HUM], "/sd/TeensySF/hum01.wav")
        elif new_state == States.ST_OFF:
            self.play_sample(self.volumes[Effects.HUM], "/sd/TeensySF/in01.wav")