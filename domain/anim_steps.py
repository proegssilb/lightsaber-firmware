

class AnimStep:
    phase_time_ms: int

    def __init__(self, phase_time_ms) -> None:
        self.phase_time_ms = phase_time_ms

    # CircuitPython doesn't support abstract methods, which this is.
    def get_value_at_time(self, time_ms: int) -> int: # type: ignore
        pass

class ConstantBrightness(AnimStep):
    value: int

    def __init__(self, brightness: int, phase_time_ms: int) -> None:
        super().__init__(phase_time_ms)
        self.value = brightness
    
    def get_value_at_time(self, time_ms: int):
        return self.value

class LinearBrightnessFade(AnimStep):
    start_value: int
    stop_value: int
    step: int

    def __init__(self, start_value: int, stop_value: int, step: int, phase_time_ms: int) -> None:
        super().__init__(phase_time_ms)
        self.start_value = start_value
        self.stop_value = stop_value
        self.step = step
    
    def get_value_at_time(self, time_ms: int):
        if time_ms < 10:
            return self.start_value
        if time_ms > self.phase_time_ms - 10:
            return self.stop_value
        return (self.stop_value - self.start_value) * time_ms // self.phase_time_ms + self.start_value
