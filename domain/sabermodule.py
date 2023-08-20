from .config.segment import ConfigSegment

try:
    from typing import Optional, Type, TypeVar, Generic
    CIRCUIT_PYTHON = False

except ImportError:
    CIRCUIT_PYTHON = True

if CIRCUIT_PYTHON:
    class BaseClass(object):
        pass

    ConfigT = object
else:
    ConfigT = TypeVar('T')

    class BaseClass(Generic[ConfigT]):
        pass

class SaberModule(BaseClass): # type: ignore
    """ A code-module of a lightsaber.

    A Saber Module manages a particular subsystem of the saber.
    """
    config: ConfigT # type: ignore
    config_type: Optional[Type[ConfigSegment]]

    async def setup(self, config: ConfigT):
        """ Do any first-power-on setup the subsystem needs to do. Init hardware, pub/sub observables, load data, etc. """
        print("Setting up:", self)
        self.config = config

    async def run(self):
        """ Run your async loop here. """
        # TODO: Put `while true`, frame delay, & exception handling here. Then call loop() in subclass.
        print("Running:", self)
        pass
