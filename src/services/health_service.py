import json
from typing import Dict, Set

from src.constants import HEALTH_CONFIG
from src.models.monitor import Monitor
from src.models.state import State


class HealthService:
    def __init__(self):
        fp = HEALTH_CONFIG
        self._monitors: Dict[str, Monitor] = {}

        with open(fp, "r") as f:
            data = json.load(f)

            if not isinstance(data, dict):
                raise TypeError(f"invalid type in {fp}")

            monitors_cfg = data.get("monitors")
            if isinstance(monitors_cfg, dict):
                for k, v in monitors_cfg.items():
                    if not isinstance(v, dict):
                        raise TypeError("invalid type in monitor config file")
                    self._monitors[k] = Monitor(k, v)

    @property
    def monitors(self) -> Dict[str, Monitor]:
        return self._monitors

    def process(self, cmd: str, value: int) -> Dict[str, Set[State]]:
        if cmd not in self._monitors:
            raise KeyError(f"unknown command {cmd}")
        return self._monitors[cmd].evaluate_all(value)
