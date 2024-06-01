from threading import Lock


class Atom[T]:
    """Thread-safe value"""

    _value: T
    _lock: Lock = Lock()

    def __init__(self, value: T) -> None:
        self.set(value)

    def get(self) -> T:
        with self._lock:
            return self._value

    def set(self, value: T) -> None:
        with self._lock:
            self._value = value
