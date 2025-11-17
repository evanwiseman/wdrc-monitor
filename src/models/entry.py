from dataclasses import dataclass, field
from typing import Dict, Set

from src.models.state import State


@dataclass
class Entry:
    name: str
    masks: Dict[int, State] = field(default_factory=dict)

    def evaluate(self, value: int) -> Set[State]:
        active = {state for mask, state in self.masks.items() if value & mask}

        if active:
            return active

        # If nothing matched, OFF is the implied state
        return {State.OFF}
