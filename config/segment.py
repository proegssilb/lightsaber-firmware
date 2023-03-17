from ticks_utils import ticks_add, ticks_less, ticks_ms
from contracts import SaberModule


class ConfigSegment:
    config_segment = 'example'
    config_manager = None
    config_data = dict()

    def __init__(self, segment_name, manager) -> None:
        self.config_segment = segment_name
        self.config_manager = manager
        self.config_data = dict()

    def __str__(self):
        return str(self.config_data)
    
    def __repr__(self) -> str:
        return repr(self.config_data)

    def set_data(self, segment_data):
        for (k, v) in segment_data.items():
            self.set_config_value(k, v)

    def get_data(self):
        return self.config_data.copy()
    
    def process_config_default(self, prop_name, default_value):
        if default_value is not None and not prop_name in self.config_data.keys():
            self.set_config_value(prop_name, default_value)

    def get_config_value(self, prop_name, default=None):
        """Return the current value for a particular config."""
        rv = self.config_data.get(prop_name, default)
        return rv
    
    def set_config_value(self, prop_name, new_value):
        """Set the current value for a particular config."""
        self.config_data[prop_name] = new_value
        self.config_manager.request_write()