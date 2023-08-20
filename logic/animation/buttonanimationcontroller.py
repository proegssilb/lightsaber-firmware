from domain.sabermodule import SaberModule
from domain.observable import Observable
from domain.animations import Animations


class ButtonAnimationController(SaberModule):
    """
    An animation controller that only uses button(s) as its inputs.

    Decides which animation is playing when.
    """
    # Inputs
    pow_btn: Observable[bool] = Observable()
    anim_finished: Observable[bool] = Observable()

    # Outputs
    base_anim: Observable[int] = Observable()
    interrupt_anim: Observable[Optional[int]] = Observable()
    active_anim: Observable[int] = Observable()

    def __init__(self, power_button: Observable[bool]) -> None:
        super().__init__()
        self.pow_btn = power_button
        self.base_anim.value = Animations.OFF
        self.interrupt_anim.value = Animations.NONE
        self.anim_finished.value = False
    
    async def setup(self, config):
        await super().setup(config)
        self.pow_btn.watch(self.on_button)
        self.anim_finished.watch(self.on_anim_finished)
    
    async def run(self):
        return await super().run()
    
    async def on_button(self, now_is_pressed, was_pressed):
        # Detect trailing/rising edge - trigger on release of button.
        # TODO: Make this happen on "tap"
        print("Button event received.")
        if was_pressed and not now_is_pressed:
            self.toggle_power()

    async def on_anim_finished(self, is_finished, was_finished):
        print("Anim finished callback called. From", was_finished, "to", is_finished)
        if not was_finished and is_finished:
            self.interrupt_anim.value = None
            self.active_anim.value = self.base_anim.value
    
    def toggle_power(self):
        print("Changing base anim from button event:", self.base_anim.value)
        if self.base_anim.value == Animations.ON:
            print("Button event received, turning power OFF")
            self.anim_finished.value = False
            self.base_anim.value = Animations.OFF
            self.interrupt_anim.value = Animations.RETRACT
            self.active_anim.value = self.interrupt_anim.value
        else:
            print("Button event received, turning power ON")
            self.anim_finished.value = False
            self.base_anim.value = Animations.ON
            self.interrupt_anim.value = Animations.IGNITE
            self.active_anim.value = self.interrupt_anim.value
