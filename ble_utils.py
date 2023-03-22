from binascii import unhexlify
import _bleio

from adafruit_ble.uuid import VendorUUID

class CharPerms:
    R = _bleio.Characteristic.READ
    RW = _bleio.Characteristic.READ | _bleio.Characteristic.WRITE
    RWN = _bleio.Characteristic.READ | _bleio.Characteristic.WRITE | _bleio.Characteristic.NOTIFY
    RN = _bleio.Characteristic.READ | _bleio.Characteristic.NOTIFY

BASE_UUID = bytearray(reversed(unhexlify('7d0a00007699494eb638deadbeef0000')))

def gen_service_id(id_in):
    assert 0 <= id_in <= 0xFFFF
    uuid = bytearray(BASE_UUID)
    uuid[13] = (id_in & 0xFF00) >> 8
    uuid[12] = id_in & 0x00FF
    return VendorUUID(uuid)

def gen_char_id(service_id, characteristic_id):
    # Service IDs are inclusive, but a characteristic ID of 0 would return the same ID as the service itself.
    # Probably nothing wrong with that, but I don't allow it here.
    assert 0 <= service_id <= 0xFFFF
    assert 0 < characteristic_id <= 0xFFFF
    uuid = bytearray(BASE_UUID)
    uuid[13] = (service_id & 0xFF00) >> 8
    uuid[12] = service_id & 0x00FF
    uuid[1] = (characteristic_id & 0xFF00) >> 8
    uuid[0] = characteristic_id & 0x00FF
    return VendorUUID(uuid)

def make_characteristic_id_gen(service_id):
    return lambda cid: gen_char_id(service_id, cid)