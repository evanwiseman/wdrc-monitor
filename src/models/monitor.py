from typing import Dict, Set

from src.models.entry import Entry
from src.models.state import State


class Monitor:
    def __init__(self, name: str, data: Dict):
        self._name = name
        self._entries: Dict[str, Entry] = {}

        for name, entry_cfg in data.items():
            entry = Entry(name=name)
            self._entries[name] = entry

            if not isinstance(entry_cfg, dict):
                continue

            raw_masks = entry_cfg.get("masks", {})
            if not isinstance(raw_masks, dict):
                continue

            masks = {int(k, 0): State(v) for k, v in raw_masks.items()}
            entry.masks = masks

    def evaluate_all(self, value: int) -> Dict[str, Set[State]]:
        return {name: entry.evaluate(value) for name, entry in self._entries.items()}

    @property
    def name(self) -> str:
        return self._name

    @property
    def entries(self):
        return self._entries
