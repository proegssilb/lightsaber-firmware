import asyncio

# There's a lot of hoops involved in getting user-defined generic classes 
# working in CircuitPython. Don't do generics.
CIRCUIT_PYTHON = False

try:
    from typing import TypeVar, Generic, Callable, MutableSequence, Coroutine, Any
    CIRCUIT_PYTHON = False

except (ImportError, NameError):
    CIRCUIT_PYTHON = True


if CIRCUIT_PYTHON:
    class BaseClass(object):
        pass

    T = object
else:
    T = TypeVar('T')

    class BaseClass(Generic[T]):
        pass

class Observable(BaseClass):
    __callbacks: MutableSequence[Callable[[T, T], Coroutine[Any, Any, None]]] = list()
    _value: T

    def __init__(self) -> None:
        super().__init__()
        self.__callbacks = list()
        self._value = None

    def snapshot(self) -> T:
        # TODO: Clone the value, preferably deeply.
        return self.value
    
    def watch(self, callback: Callable[[T, T], Coroutine[Any, Any, None]]):
        if callback is None:
            return
        self.__callbacks.append(callback)

    def unwatch(self, callback: Callable[[T, T], Coroutine[Any, Any, None]]):
        if callback is None:
            return
        self.__callbacks.remove(callback)
    
    def __get(self) -> T:
        return self._value
    
    def __set(self, value: T):
        if value != self._value:
            print("Observable value changed. Old value:", self._value, "New value:", value)
            for f in self.__callbacks:
                # callback(new_value, old_value)
                asyncio.create_task(f(value, self._value))
                pass
        self._value = value

    value = property(__get, __set)
        
