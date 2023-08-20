import asyncio
import json
import supervisor
import time

from domain.ticks_utils import ticks_add, ticks_less, ticks_ms
from domain.sabermodule import SaberModule

class ConfigManager(SaberModule):
    file_name = '/sd/saber_config.json'
    ns_read: int = 0
    ns_write: int = 0
    segments = dict()
    write_interval = 30_000_000 # Number of milliseconds to write a file
    enable_read = False
    enable_write = False

    def __init__(self, file_name = None) -> None:
        super(ConfigManager, self).__init__()
        self.segments = dict()
        if file_name is not None:
            self.file_name = file_name
        self.ns_read = None
        self.ns_write = None
        self.enable_read = False
        self.enable_write = False

    def __read_file(self):
        print("Reading config.")
        self.ns_read = time.monotonic_ns() + self.write_interval
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
        self.ns_write = ticks_add(ticks_ms(), self.write_interval)
        self.enable_write = False

        config_data = {}

        for (key, segment) in self.segments.items():
            config_data[key] = segment.get_data()

        try:
            with open(self.file_name, 'w') as config_file:
                json.dump(config_data, config_file)
        except OSError:
            print("OSError while opening file:", self.file_name)
            raise

    def request_read(self, force=False):
        '''Set a flag to reread the config file at the next save interval'''
        if force or self.ns_read is None or self.ns_read < time.monotonic_ns():
            self.__read_file()
        else:
            self.enable_read = True

    def request_write(self, force=False):
        '''Set a flag to write the config file at the next save interval'''
        if force or self.ns_write is None or self.ns_write < time.monotonic_ns():
            self.__write_file()
        else:
            self.enable_write = True

    async def setup(self, config):
        '''Set up the config provider, including reading data from file.'''
        # Note: `config` will always be nonsense. This has to get called in 
        # order for future modules to have a config object.
        print('Config as of initial setup:', repr(self.segments))
        await super(ConfigManager, self).setup(config)

    async def run(self):
        await super(ConfigManager, self).run()

        while True:
            next_run = supervisor.ticks_ms() + 500

            # TODO: Find a way to refresh the config without disrupting other
            # modules ability to sync changed data.

            # Handle auto-save
            current_time = time.monotonic_ns()

            if self.enable_read and self.ns_read < current_time:
                self.__read_file()
            if self.enable_write and self.ns_write < current_time:
                self.__write_file()

            await asyncio.sleep_ms(next_run - supervisor.ticks_ms())


    def read_data(self):
        # TODO: Can we use `request_read` instead?
        self.__read_file()
        print('Config as of initial read:', repr(self.segments))

    def get_config_segment(self, sabermod: SaberModule, mod_index: int):
        if not hasattr(sabermod, 'config_type') or sabermod.config_type is None:
            return None
        rv_type = sabermod.config_type
        rv = rv_type()
        segment_name = type(sabermod).__name__ + str(mod_index)
        self.segments[segment_name] = rv
        rv.setup_tracking(self.request_write)
        return rv