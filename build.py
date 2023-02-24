
"""
This file lets you build out your saber. Edit it as you like, but make sure the required constants
are present for the rest of the program to reference.
"""

# This line stops the rest of the program from seeing things in this module that aren't part of the spec.
__all__ = ('LED_MODULE', 'SOUND_OUT', 'SOUND_LOGIC', 'CONTROLS', 'OTHER_MODULES')

# There's going to be a number of imports. Keep scrolling for the spot where you configure stuff.
import board

from button import OnOffButton
from lights.led import AnalogLedController
from sound_logic import BasicSoundLogic
from fsplug.sdcard import SdStorage
from sound.i2s import I2SSoundOut
from contracts import SaberModule


LED_MODULE = AnalogLedController(board.D11)

SOUND_LOGIC = BasicSoundLogic()

SOUND_OUT = I2SSoundOut(SOUND_LOGIC.mixer, board.A0, board.A1, board.A2)

CONTROLS = (OnOffButton(), SaberModule())

OTHER_MODULES = (SdStorage(board.SPI(), board.A5), SaberModule())