import _bleio

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.device_info import DeviceInfoService

from contracts import SaberModule

_bleio.adapter.name = "SABERG0"

class BleConfigService(SaberModule):

    def __init__(self, config_manager, guid_base) -> None:
        super().__init__()
        self.config_manager = config_manager
        self.ble = BLERadio()
        self.device_info = DeviceInfoService(manufacturer="Khyber Squadron", software_revision="0.1.1", model_number="Proto00-Gen0-v0")
        self.advertisement = ProvideServicesAdvertisement(self.device_info)
        self.services = list()


    def setup(self, config, saber):
        super().setup(config, saber)
        self.services = list()
        mods = self.get_modules(saber)
        for (idx, mod) in enumerate(mods):
            if not hasattr(mod, 'uuid'):
                continue
            svc = self.get_service(idx, mod, config, saber)
            self.services.append(svc)
        advertisement = ProvideServicesAdvertisement(self.device_info, *self.services)
        self.ble.start_advertising(advertisement)

    def get_modules(self, saber):
        return saber.modules

    def get_service(self, mod_index: int, mod: SaberModule, config, saber):
        return mod


    def loop(self, frame: int, state):
        pass

    def handle_state_change(self, old_state, new_state):
        pass

    def deep_sleep(self):
        pass

    def sleep_resume(self):
        pass