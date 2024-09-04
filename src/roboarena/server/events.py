# from abc import ABC, abstractmethod
from collections.abc import Iterable

from roboarena.shared.types import EventName

# class EventTarget[T](ABC):
#     @abstractmethod
#     def dispatch(self, type: EventName, value: T) -> None: ...

#     def mapped[U](self, f: Callable[[U], T]) -> "EventTarget[U]":
#         return MappedEventTarget(self, f)


# class MappedEventTarget[T, O](EventTarget[T]):
#     orig: EventTarget[O]
#     f: Callable[[T], O]

#     def __init__(self, orig: EventTarget[O], f: Callable[[T], O]) -> None:
#         super().__init__()
#         self.orig = orig
#         self.f = f

#     def dispatch(self, type: EventName, value: T) -> None:
#         self.orig.dispatch(type, self.f(value))


class EventBuffer[T]:  # (EventTarget[T])
    """Prevents resending of same events by collecting only the last one."""

    events: dict[EventName, T] = {}

    def dispatch(self, type: EventName, value: T) -> None:
        self.events[type] = value

    def collect(self) -> Iterable[T]:
        events = self.events.values()
        self.events = {}
        return events
