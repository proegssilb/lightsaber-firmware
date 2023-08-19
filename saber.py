import asyncio
import traceback

import sdcardio
import storage
import board
import domain.ticks_utils as tu
import build

class Saber:
    """
    The main Saber class. Instantiates everything, and sets it all running.
    """
    saber_build = build
    config = None
    modules = ()

    def main(self):
        """The top-level method, the root of all execution. Do not call this anywhere except `code.py`."""
        print("")
        mods = [getattr(self.saber_build, n) for n in self.saber_build.__all__]
        self.modules = list(self.build_module_list(*mods))
        for (idx, m) in enumerate(self.modules):
            conf_segment = self.saber_build.CONFIG_MANAGER.get_config_segment(m, idx)
            asyncio.run(m.setup(conf_segment))

        self.saber_build.CONFIG_MANAGER.read_data()
        self.saber_build.CONFIG_MANAGER.request_write()

        self.run_loop()
            

    def run_loop(self):
        for m in self.modules:
            asyncio.create_task(m.run())
        asyncio.get_event_loop().run_forever()


    def build_module_list(self, *pargs):
        # This is just flatten with a fancy name.
        for item in pargs:
            if type(item) in (list, tuple):
                yield from self.build_module_list(*item)
            else:
                yield item
