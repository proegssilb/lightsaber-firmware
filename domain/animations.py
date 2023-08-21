from math import fmod
from domain.range import interpolate

from domain.time import ns, us, ms, TTime, anim_timeline_progress

try:
    from typing import Optional, Tuple
except ImportError:
    pass

class Color:
    red: float = 0.0
    green: float = 0.0
    blue: float = 0.0
    chroma: float = 0.0
    value: float = 0.0
    lightness: float = 0.0

    __min: float = 0.0
    __max: float = 0.0
    __hue: Optional[float] = None

    def __init__(self, R: float, G: float, B: float):
        # assert 0 <= R <= 1, f"Red component value {R} out of range."
        # assert 0 <= G <= 1, f"Green component value {G} out of range."
        # assert 0 <= B <= 1, f"Blue component value {B} out of range."
        self.red = R
        self.green = G
        self.blue = B
        self.__min = min(R, G, B)
        self.__max = max(R, G, B)
        self.chroma = self.__max - self.__min
        self.value = self.__max
        self.lightness = (self.__max + self.__min) / 2
        self.__hue = None

    @property
    def hue(self):
        if self.__hue is not None:
            return self.__hue
        elif self.chroma == 0:
            self.__hue = 0
            return 0
        elif self.value == self.red:
            self.__hue = fmod((self.green - self.blue) / self.chroma, 6)
            return self.__hue
        elif self.value == self.green:
            self.__hue = (self.blue - self.red) / self.chroma + 2
        elif self.value == self.blue:
            self.__hue = (self.red - self.green) / self.chroma + 4

    # TODO: HSV, HSL, and the two definitions of saturation

    def to_led(self) -> float:
        """ Return a single float suitable for a single base-lit LED."""
        # TODO: Validate this
        return self.lightness

    def to_rgbw(self) -> Tuple[float, float, float, float]:
        """
        Return values suitable for driving a pixel containing red/green/blue/white components.
        """
        # TODO: Look up a better definition
        w = self.__min
        return (self.red - w, self.green - w, self.blue - w, w)
    
    def __add__(self, other) -> "Color":
        return self.__math(other, lambda x, y: x + y)
    
    __radd__ = __add__

    def __sub__(self, other) -> "Color":
        return self.__math(other, lambda x, y: x - y)
    
    def __rsub__(self, other) -> "Color":
        return self.__math(other, lambda x, y: y - x)
    
    def __mul__(self, other) -> "Color":
        if isinstance(other, Color):
            raise ValueError("Yes, you do need to figure out what this even means.")
        return self.__math(other, lambda x, y: x * y)
    
    __rmul__ = __mul__

    def __truediv__(self, other):
        return self.__partialmath(other, lambda x, y: x / y)
    
    def __rtruediv__(self, other):
        return self.__partialmath(other, lambda x, y: y / x)
    
    def __floordiv__(self, other):
        return self.__partialmath(other, lambda x, y: x // y)
    
    def __rfloordiv__(self, other):
        return self.__partialmath(other, lambda x, y: y // x)
    
    def __mod__(self, other):
        return self.__partialmath(other, lambda x, y: x % y)
    
    def __rmod__(self, other):
        return self.__partialmath(other, lambda x, y: x % y)

    def __math(self, other, op) -> "Color":
        if isinstance(other, Color):
            return Color(op(self.red, other.red), op(self.green, other.green), op(self.blue, other.blue))
        elif isinstance(other, (int, float)):
            return Color(op(self.red, other), op(self.green, other), op(self.blue, other))
        else:
            return NotImplemented
        
    def __partialmath(self, other, op) -> "Color":
        if isinstance(other, Color):
            raise ValueError("Yes, you do need to figure out what this even means.")
        elif isinstance(other, (int, float)):
            return Color(op(self.red, other), op(self.green, other), op(self.blue, other))
        else:
            return NotImplemented

class Animation:

    def render_loop(self, time_from_start: TTime) -> Color:
        raise ValueError("Animation is a base class, do not call.")
    
    def render_once(self, time_from_start: TTime) -> Tuple[Color, bool]:
        raise ValueError("Animation is a base class, do not call.")
    
class Steady(Animation):
    """ Constant color value. """
    value: Color = Color(0.0, 0.0, 0.0)

    def __init__(self, color: Color) -> None:
        super().__init__()
        self.value = color

    def render_loop(self, time_from_start: TTime) -> Color:
        return self.value
    
    def render_once(self, time_from_start: TTime) -> Tuple[Color, bool]:
        return (self.value, True)
    
class Breathe(Animation):
    """
    An animation that transitions from off to on and back to off.

    You can skip any phase by passing a length of 0.
    """

    on_color: Color = Color(0, 0, 0)
    off_color: Color = Color(0, 0, 0) # Constant value for optimization
    off_time: TTime = ms(500)
    fade_in_time: TTime = ms(500)
    on_time: TTime = ms(500)
    fade_out_time: TTime = ms(500)
    total_time: TTime = ms(2000)

    def __init__(self, color, off_time=ms(500), fade_in_time=ms(500), 
                 on_time=ms(500), fade_out_time=ms(500)) -> None:
        super().__init__()
        self.on_color = color
        self.off_time = off_time
        self.fade_in_time = fade_in_time
        self.on_time = on_time
        self.fade_out_time = fade_out_time
        self.total_time = off_time + fade_in_time + on_time + fade_out_time

    def __render(self, time_from_start: TTime) -> Color:
        phases = (self.off_time, self.fade_in_time, self.on_time, self.fade_out_time)
        (phase, progress) = anim_timeline_progress(time_from_start, *phases)
        if phase == 0:
            return self.off_color
        elif phase == 1:
            return interpolate(self.off_color, self.on_color, progress)
        elif phase == 2:
            return self.on_color
        elif phase == 3:
            return interpolate(self.on_color, self.off_color, progress)

    def render_once(self, time_from_start: TTime) -> Tuple[Color, bool]:
        return (self.__render(time_from_start), time_from_start > self.total_time)
    
    def render_loop(self, time_from_start: TTime) -> Color:
        anim_time = time_from_start % self.total_time
        return self.__render(anim_time)
    
class FadeIn(Breathe):
    """
    Fades in over time, but jumps from on to off without transition.
    """
    def __init__(self, color, off_time=ms(500), fade_in_time=ms(500), on_time=ms(500)) -> None:
        super().__init__(color, off_time, fade_in_time, on_time, 0)

class FadeOut(Breathe):
    """
    Fades out over time, but jumps from on to off without transition.
    """
    def __init__(self, color, off_time=ms(500), on_time=ms(500), fade_out_time=ms(500)) -> None:
        super().__init__(color, off_time, 0, on_time, fade_out_time)

class Blink(Breathe):
    """
    Starts off, then turns on, then turns back off.
    """
    def __init__(self, color, off_time=ms(500), on_time=ms(500), ) -> None:
        super().__init__(color, off_time, 0, on_time, 0)
