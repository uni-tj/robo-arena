from collections.abc import Iterator, Sequence
from copy import deepcopy
from dataclasses import dataclass
from typing import NoReturn, overload

# import keyboard
from attr import define, field

from roboarena.server.level_generation.tileset import tiles, tileset
from roboarena.server.level_generation.wfc import (
    WFC,
    CollapsedAllEvent,
    CollapsedOneEvent,
    PropagatedOneEvent,
    TilePosition,
    print_wfc,
)
from roboarena.shared.util import Color, spiral_space


class StateError(Exception):
    pass


@dataclass(frozen=True)
class PropagatedOneStep:
    wfc: WFC
    ev: PropagatedOneEvent


@dataclass(frozen=True)
class CollapsedOneStep:
    wfc: WFC
    ev: CollapsedOneEvent
    steps: Sequence[PropagatedOneStep]


@dataclass(frozen=True)
class CollapsedAllStep:
    wfc: WFC
    ev: CollapsedAllEvent
    steps: Sequence[CollapsedOneStep]


@define
class WFCStepper:
    collapsed_all_steps: list[CollapsedAllStep] = field(init=False, factory=list)
    spiral: Iterator[TilePosition] = field(
        init=False, factory=lambda: iter(spiral_space())
    )
    wfc: WFC
    tiles: dict[int, str | None]

    @overload
    def get_state(
        self,
        collapsed_all_step: int,
        collapsed_one_step: None,
        propagated_one_step: None,
    ) -> CollapsedAllStep: ...

    @overload
    def get_state(
        self,
        collapsed_all_step: int,
        collapsed_one_step: int,
        propagated_one_step: None,
    ) -> tuple[CollapsedAllStep, CollapsedOneStep]: ...

    @overload
    def get_state(
        self,
        collapsed_all_step: int,
        collapsed_one_step: int,
        propagated_one_step: int,
    ) -> tuple[CollapsedAllStep, CollapsedOneStep, PropagatedOneStep]: ...

    def get_state(
        self,
        collapsed_all_step: int,
        collapsed_one_step: int | None,
        propagated_one_step: int | None,
    ):
        while collapsed_all_step >= len(self.collapsed_all_steps):
            propagated_one_steps: list[PropagatedOneStep] = list()
            collapsed_one_steps: list[CollapsedOneStep] = list()

            def handle_progated_one(e: PropagatedOneEvent):
                propagated_one_steps.append(  # noqa: B023
                    PropagatedOneStep(deepcopy(self.wfc), e)
                )

            def handle_collapsed_one(e: CollapsedOneEvent):
                nonlocal propagated_one_steps
                collapsed_one_steps.append(  # noqa: B023
                    CollapsedOneStep(deepcopy(self.wfc), e, propagated_one_steps)
                )
                propagated_one_steps = list()

            def handle_collapsed_all(e: CollapsedAllEvent):
                nonlocal collapsed_one_steps
                self.collapsed_all_steps.append(
                    CollapsedAllStep(deepcopy(self.wfc), e, collapsed_one_steps)
                )
                collapsed_one_steps = list()

            wfc.events.add_listener(PropagatedOneEvent, handle_progated_one)
            wfc.events.add_listener(CollapsedOneEvent, handle_collapsed_one)
            wfc.events.add_listener(CollapsedAllEvent, handle_collapsed_all)
            wfc.collapse([next(self.spiral)])
            wfc.events.remove_listener(handle_progated_one)
            wfc.events.remove_listener(handle_collapsed_one)
            wfc.events.remove_listener(handle_collapsed_all)

        try:
            c_all = self.collapsed_all_steps[collapsed_all_step]
            if collapsed_one_step is None:
                return c_all
            c_one = c_all.steps[collapsed_one_step]
            if propagated_one_step is None:
                return c_all, c_one
            p_one = c_one.steps[propagated_one_step]
            return c_all, c_one, p_one
        except IndexError:
            raise StateError

    def print_state(
        self, state: PropagatedOneStep | CollapsedOneStep | CollapsedAllStep
    ) -> None:
        c_colors = {p: Color.CYAN_BG for p in state.wfc._collapsed}  # type: ignore
        match state:
            case PropagatedOneStep():
                print_wfc(
                    state.wfc, self.tiles, c_colors | {state.ev.position: Color.RED_BG}
                )
            case CollapsedOneStep():
                print_wfc(
                    state.wfc, self.tiles, c_colors | {state.ev.position: Color.RED_BG}
                )
            case CollapsedAllStep():
                print_wfc(
                    state.wfc,
                    self.tiles,
                    c_colors | {p: Color.BLUE_BG for p in state.ev.positions},
                )

    def interactive(self) -> NoReturn:
        c_all: int = 0
        c_one: int | None = None
        p_one: int | None = None
        step: int = 1

        while True:
            backup = c_all, c_one, p_one
            try:
                print(f"q/e: c_all -/+, a/d: c_one -/+, y/c: p_one -/+, step: {step}")
                # evt = keyboard.read_event()
                # print(evt)
                # if evt.event_type != keyboard.KEY_DOWN:
                #     continue
                # match evt.name:
                match input():
                    case "-":
                        step = max(step // 10, 1)
                    case "+":
                        step = step * 10
                    case "q":
                        c_all -= step
                        c_one = None
                        p_one = None
                        state = self.get_state(c_all, c_one, p_one)
                        self.print_state(state)
                        print(f"c_all: {c_all+1}")
                    case "e":
                        c_all += step
                        c_one = None
                        p_one = None
                        state = self.get_state(c_all, c_one, p_one)
                        self.print_state(state)
                        print(f"c_all: {c_all+1}")
                    case "a":
                        if c_one is None:
                            c_one = step
                        c_one -= step
                        p_one = None
                        state = self.get_state(c_all, c_one, p_one)
                        self.print_state(state[1])
                        print(
                            f"c_all: {c_all+1}, c_one: {c_one+1}/{len(state[0].steps)},"
                        )
                    case "d":
                        if c_one is None:
                            c_one = -step
                        c_one += step
                        p_one = None
                        state = self.get_state(c_all, c_one, p_one)
                        self.print_state(state[1])
                        print(
                            f"c_all: {c_all+1}, c_one: {c_one+1}/{len(state[0].steps)}"
                        )
                    case "y":
                        if c_one is None:
                            raise StateError()
                        if p_one is None:
                            p_one = +step
                        p_one -= step
                        state = self.get_state(c_all, c_one, p_one)
                        self.print_state(state[2])
                        print(
                            f"c_all: {c_all+1}, c_one: {c_one+1}/{len(state[0].steps)}, p_one: {p_one+1}/{len(state[1].steps)}"  # noqa: B950
                        )
                    case "c":
                        if c_one is None:
                            raise StateError()
                        if p_one is None:
                            p_one = -step
                        p_one += step
                        state = self.get_state(c_all, c_one, p_one)
                        self.print_state(state[2])
                        print(
                            f"c_all: {c_all+1}, c_one: {c_one+1}/{len(state[0].steps)}, p_one: {p_one+1}/{len(state[1].steps)}"  # noqa: B950
                        )
                    case _:
                        pass
            except StateError:
                print("state unaivable")
                c_all, c_one, p_one = backup


if __name__ == "__main__":
    wfc = WFC(tileset.to_wfc())
    tiles = {i + 1: tiles.inv.get(t) for i, t in enumerate(tileset.tiles)}
    WFCStepper(wfc, tiles).interactive()
