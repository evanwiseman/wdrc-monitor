from dataclasses import dataclass, field
from typing import Dict, Set

from src.models.state import State


@dataclass
class Entry:
    name: str
    masks: Dict[int, State] = field(default_factory=dict)
    states: Set[State] = field(default_factory=lambda: {State.UNKNOWN})

    def evaluate(self, value: int) -> Set[State]:
        active = {state for mask, state in self.masks.items() if value & mask}

        if not active:
            active = {State.OFF}

        self.states = active
        return active
