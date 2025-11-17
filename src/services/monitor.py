import json
from typing import Dict, Set

from src.models.entry import Entry
from src.models.state import State


class Monitor:
    def __init__(self, data: Dict):
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
    def entries(self):
        return self._entries


class MonitorService:
    def __init__(self, fp: str):
        self._monitors: Dict[str, Monitor] = {}
        with open(fp, "r") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise TypeError(f"invalid type in {fp}")

            for k, v in data.items():
                if not isinstance(v, dict):
                    raise TypeError("invalid type in monitor config file")
                self._monitors[k] = Monitor(v)

    def processCommand(self, command: str, value: int) -> Dict[str, Set[State]]:
        if command not in self._monitors:
            raise KeyError(f"unknown command {command}")
        return self._monitors[command].evaluate_all(value)
