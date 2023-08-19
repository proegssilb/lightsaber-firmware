
"""
The overall file describing the "build" of the lightsaber. Edit it as you like,
but make sure the required constants are present for the rest of the program to
reference.

This file is meant for skilled technicians. While I try to document the file 
well enough for people to pick up from just this file, there may be important
details only available in the rest of the codebase.
"""

# This line stops the rest of the program from seeing things in this module that aren't part of the spec.
__all__ = ('STORAGE_MODULES', 'CONFIG_MANAGER', 'LED_MODULE', 'SOUND_OUT', 'SOUND_LOGIC', 
           'CONTROLS', 'BUTTON_MODULE', 'LED_LOGIC', 'OTHER_MODULES', 'ANIM_MODULE')

# There's going to be a number of imports. Keep scrolling for the spot where you configure stuff.
import board
from digitalio import Pull

from logic.manager import ConfigManager
from drivers.lights.blade import AnalogLedController
from logic.animation.buttonanimationcontroller import ButtonAnimationController
from logic.light.baselit_render import BaselitRenderer
from logic.sound.basic import BasicSoundLogic
from storage.sdcard import SdStorage
from drivers.sound.i2s import I2SSoundOut
from drivers.ble import BleConfigService
from drivers.buttons.rawbutton import RawButton

# These are "prereqs" in order for other modules to work. Keep this as short as
# is feasible. Have very good engineering reason why something must go here 
# before putting it here.
#
# Nothing before the CONFIG_MANAGER line will have a sane config object. The FS 
# must be working before the config will work, and you need working config to 
# get valid config objects.
STORAGE_MODULES = (SdStorage(board.SPI(), board.A5),)

CONFIG_MANAGER = ConfigManager()

# All the lines after this point are modules of logic. They communicate with 
# each other via "observables", magic data blocks that can be watched for
# changes in value. Each module keeps its observables in a different spot.
# 
# The main way of changing how a lightsaber works is to change the modules 
# below, and how they communicate.
BUTTON_MODULE = RawButton(board.A1, pull_direction=Pull.DOWN)      #  I2cOnOffButton(0x6E)
# TODO: Module for power LED on A2

ANIM_MODULE = ButtonAnimationController(BUTTON_MODULE.button_state)
SOUND_LOGIC = BasicSoundLogic(ANIM_MODULE)
LED_LOGIC = BaselitRenderer(ANIM_MODULE)

LED_MODULE = AnalogLedController(board.A0, LED_LOGIC.led_brightness)

SOUND_OUT = I2SSoundOut(SOUND_LOGIC.mixer, board.D12, board.D11, board.D13)

CONTROLS = () 

OTHER_MODULES = (BleConfigService(CONFIG_MANAGER, '7d0ad01b-7699-494e-b638-c3ec8cdd11d3'),)