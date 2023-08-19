
from adafruit_ble.characteristics import Characteristic, ComplexCharacteristic

try:
    from typing import Callable
except:
    pass

class ConfigSegment:
    __tracked_attrs: tuple = tuple()
    __write_hook: Callable[[], None]

    def setup_tracking(self, write_hook: Callable[[], None]) -> None:
        tracked_attrs = []
        for attr_name in dir(self.__class__):
            if attr_name.startswith("__"):
                continue
            value = getattr(self.__class__, attr_name)
            if not isinstance(value, Characteristic) and not isinstance(value, ComplexCharacteristic):
                continue

            tracked_attrs.append(attr_name)
            setattr(self, '_old_val_' + attr_name, getattr(self, attr_name))
        self.__tracked_attrs = tuple(tracked_attrs)
        self.__write_hook = write_hook
    
    def obj_changed(self) -> bool:
        return len(self.changed_attrs()) > 0

    def changed_attrs(self) -> list[str]:
        changed_attrs = []
        for attr_name in self.__tracked_attrs:
            if self.attr_changed(attr_name):
                changed_attrs.append(attr_name)
        if len(changed_attrs) > 0:
            print("Changed attributes:", repr(changed_attrs))
        return changed_attrs
    
    def attr_changed(self, attr_name: str) -> bool:
        old_val = getattr(self, '_old_val_' + attr_name)
        current_val = getattr(self, attr_name)
        setattr(self, '_old_val_' + attr_name, current_val)
        if old_val != current_val:
            self.__write_hook()
        return old_val != current_val
    
    def get_data(self):
        return {attr_name: getattr(self, attr_name) for attr_name in self.__tracked_attrs}

    def set_data(self, segment_data):
        for config_key, config_val in segment_data.items():
            if not hasattr(self, config_key):
                continue
            setattr(self, config_key, config_val)
