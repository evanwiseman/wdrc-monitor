from typing import Dict, Set

from src.models.entry import Entry
from src.models.state import State


class Monitor:
    def __init__(self, key: str, data: Dict):
        self._name = key

        # Create entries for the montior
        self.color: str = data.get("color", "white")
        self.dock: str = data.get("dock", "center")
        self._entries: Dict[str, Entry] = {}
        entries_cfg = data.get("entries")
        if isinstance(entries_cfg, dict):
            for name, entry_cfg in entries_cfg.items():
                entry = Entry(name)
                self.entries[name] = entry
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
