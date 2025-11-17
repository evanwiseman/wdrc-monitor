import json
from typing import Dict, Set

from src.models.monitor import Monitor
from src.models.state import State


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
                self._monitors[k] = Monitor(k, v)

    def processCommand(self, command: str, value: int) -> Dict[str, Set[State]]:
        if command not in self._monitors:
            raise KeyError(f"unknown command {command}")
        return self._monitors[command].evaluate_all(value)
