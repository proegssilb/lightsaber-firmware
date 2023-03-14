import os
import time
import traceback

import sdcardio
import storage
import board

from contracts import States
import ticks_utils as tu

class Saber:
    """
    The main Saber class. Manages the current state, marshals modules.
    """
    saber_build = None
    config = None
    state = None
    __next_state = None
    modules = None
    frame_time = 10
    anim_time = 50

    def main(self):
        """The top-level method, the root of all execution. Do not call this anywhere except `code.py`."""
        print("")
        mods = [getattr(self.saber_build, n) for n in self.saber_build.__all__]
        self.modules = list(self.build_module_list(*mods))
        self.state = States.DEFAULT
        for (idx, m) in enumerate(self.modules):
            conf_segment_name = type(m).__name__ + str(idx)
            conf_segment = self.saber_build.CONFIG_MANAGER.get_config_segment(conf_segment_name)
            m.setup(conf_segment, self)

        self.saber_build.CONFIG_MANAGER.request_write()

        frame_num = 0
        frame_max = 0xFFFF

        while True:
            sleep_target = tu.ticks_ms() + self.frame_time
            self.__next_state = None
            self.run_loop(self.state, frame_num)
            frame_num = (frame_num + 1) % frame_max

            if self.state == States.ST_IGNITE and frame_num >= self.anim_time:
                self.request_state_change(States.ST_ON)
            if self.state == States.ST_RETRACT and frame_num >= self.anim_time:
                self.request_state_change(States.ST_OFF)

            if self.__next_state is not None:
                self.run_state_change(self.state, self.__next_state)
                self.state = self.__next_state
                frame_num = 0

            while tu.ticks_less(tu.ticks_ms(), sleep_target):
                pass

    def run_state_change(self, old_state, new_state):
        for m in self.modules:
            try:
                m.handle_state_change(self.state, self.__next_state)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print("Exception while changing state in module type:", type(m).__name__)
                traceback.print_exception(e)

    def run_loop(self, state, frame_num):
        for m in self.modules:
            try:
                m.loop(frame_num, state)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print("Exception while looping in module type:", type(m).__name__)
                traceback.print_exception(e)


    def build_module_list(self, *pargs):
        # This is just flatten with a fancy name.
        for item in pargs:
            if type(item) in (list, tuple):
                yield from self.build_module_list(*item)
            else:
                yield item


    def request_state_change(self, new_state):
        """
        Modules use this to signal a new global state for the Saber. The new state will apply after all
        modules have run through the current loop.

        If multiple modules request different state changes, the last module in the list wins. Also,
        your build and/or modules might have a bug.
        """
        self.__next_state = new_state