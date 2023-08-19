import _bleio

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.device_info import DeviceInfoService

from domain.sabermodule import SaberModule

_bleio.adapter.name = "SABERG0"

class BleConfigService(SaberModule):

    def __init__(self, config_manager, guid_base) -> None:
        super().__init__()
        self.config_manager = config_manager
        self.ble = BLERadio()
        self.device_info = DeviceInfoService(manufacturer="Kyber Squadron", software_revision="0.1.1", model_number="Proto00-Gen0-v0")
        self.advertisement = ProvideServicesAdvertisement(self.device_info)

    async def setup(self, config):
        await super().setup(config)
        advertisement = ProvideServicesAdvertisement(self.device_info)
        self.ble.start_advertising(advertisement)

    def get_modules(self, saber):
        return saber.modules

    def get_service(self, mod_index: int, mod: SaberModule, config, saber):
        return mod

    async def run(self):
        await super(BleConfigService, self).run()
