
"""
This file lets you build out your saber. Edit it as you like, but make sure the required constants
are present for the rest of the program to reference.
"""

# This line stops the rest of the program from seeing things in this module that aren't part of the spec.
__all__ = ('STORAGE_MODULES', 'CONFIG_MANAGER', 'LED_MODULE', 'SOUND_OUT', 'SOUND_LOGIC', 'CONTROLS', 'OTHER_MODULES')

# There's going to be a number of imports. Keep scrolling for the spot where you configure stuff.
import board

from config import ConfigManager
from button import OnOffButton
from lights.led import AnalogLedController
from sound_logic import BasicSoundLogic
from fsplug.sdcard import SdStorage
from sound.i2s import I2SSoundOut
from ble import BleConfigService

# Neither of these two will have a sane config object. The FS must be working before
# the config will work, and you need working config to get valid config objects.
STORAGE_MODULES = (SdStorage(board.SPI(), board.A5),)

CONFIG_MANAGER = ConfigManager()

# These should all have a sane config object
LED_MODULE = AnalogLedController(board.A0)

SOUND_LOGIC = BasicSoundLogic()

SOUND_OUT = I2SSoundOut(SOUND_LOGIC.mixer, board.D6, board.D9, board.D5)

CONTROLS = (OnOffButton(), OnOffButton(0x6E))

OTHER_MODULES = (BleConfigService(CONFIG_MANAGER, '7d0ad01b-7699-494e-b638-c3ec8cdd11d3'),)