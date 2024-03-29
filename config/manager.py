import json

from ticks_utils import ticks_add, ticks_less, ticks_ms
from contracts import SaberModule
from config.segment import ConfigSegment

class ConfigManager(SaberModule):
    file_name = '/sd/saber_config.json'
    ticks_read = None
    ticks_write = None
    segments = dict()
    write_interval = 30000 # Number of milliseconds to write a file
    enable_read = False
    enable_write = False

    def __init__(self, file_name = None) -> None:
        super(ConfigManager, self).__init__()
        self.segments = dict()
        if file_name is not None:
            self.file_name = file_name
        self.ticks_read = None
        self.ticks_write = None
        self.enable_read = False
        self.enable_write = False

    def __read_file(self):
        print("Reading config.")
        self.ticks_read = ticks_add(ticks_ms(), self.write_interval)
        self.enable_read = False

        try:
            with open(self.file_name, 'r') as config_file:
                try:
                    config_data = json.load(config_file)
                    print("Loaded data:", config_data)
                except ValueError as ve:
                    print(ve)
                    config_data = {}
                if not isinstance(config_data, dict):
                    return
                for (k, v) in config_data.items():
                    if not isinstance(v, dict):
                        print("Config key has invalid data, continuing:", k)
                        continue
                    segment = self.segments.get(k, None)
                    if segment is None:
                        print("Could not find segment for key:", repr(k))
                        continue
                    segment.set_data(v)
                    self.segments[k] = segment
        except OSError as ose:
            if ose.errno == 2:
                # No such file/directory. We'll write the file out soon enough.
                print("Ignoring missing file.")

    def __write_file(self):
        print("Writing config:", self.segments)
        self.ticks_write = ticks_add(ticks_ms(), self.write_interval)
        self.enable_write = False

        config_data = {}

        for (key, segment) in self.segments.items():
            config_data[key] = segment.get_data()

        with open(self.file_name, 'w') as config_file:
            json.dump(config_data, config_file)

    def request_read(self, force=False):
        '''Set a flag to reread the config file at the next save interval'''
        if force or self.ticks_read is None or ticks_less(self.ticks_read, ticks_ms()):
            self.__read_file()
        else:
            self.enable_read = True

    def request_write(self, force=False):
        '''Set a flag to write the config file at the next save interval'''
        if force or self.ticks_write is None or ticks_less(self.ticks_write, ticks_ms()):
            self.__write_file()
        else:
            self.enable_write = True

    def setup(self, config, saber):
        '''Set up the config provider, including reading data from file.'''
        # Note: `config` will always be nonsense. This has to get called in 
        # order for future modules to have a config object.
        print('Config as of initial setup:', repr(self.segments))

    def read_data(self):
        # TODO: Can we use `request_read` instead?
        self.__read_file()
        print('Config as of initial read:', repr(self.segments))
    
    def loop(self, _frame: int, _state):
        # We need this in order to check on "timers"

        if self.enable_read and ticks_less(self.ticks_read, ticks_ms()):
            self.__read_file()
        
        if self.enable_write and ticks_less(self.ticks_write, ticks_ms()):
            self.__write_file()

    def get_config_segment(self, sabermod, mod_index):
        if not hasattr(sabermod, 'config_type'):
            return None
        rv_type = getattr(sabermod, 'config_type')
        rv = rv_type()
        segment_name = type(sabermod).__name__ + str(mod_index)
        self.segments[segment_name] = rv
        rv.setup_tracking(self)
        return rv