import json
from typing import Dict, Set

from PyQt6.QtCore import QObject

from src.constants import HEALTH_CONFIG
from src.models.heartbeat import Heartbeat
from src.models.monitor import Monitor
from src.models.state import State
from src.models.wdlms import Wdlms


class HealthService(QObject):
    def __init__(self):
        super().__init__()
        self._monitors: Dict[str, Monitor] = {}
        self._heartbeats: Dict[str, Heartbeat] = {}
        self._version: int = 0

        self._load_config()

    def _load_config(self):
        """Load and parse health configuration from JSON file."""
        with open(HEALTH_CONFIG, "r") as f:
            data = json.load(f)

        self._validate_config_structure(data)
        self._version = data["version"]
        self._load_monitors(data["monitors"])
        self._load_heartbeats(data["heartbeats"])
        self._load_wdlms(data["wdlms"])

    def _validate_config_structure(self, cfg: dict) -> None:
        """Validate the basic structure of the configuration."""
        if not isinstance(cfg, dict):
            raise TypeError(f"{__name__}: config must be a dict, got {type(cfg)}")

        if "version" not in cfg or not isinstance(cfg["version"], int):
            raise TypeError(f"{__name__}: 'version' must be an int")

        if "monitors" not in cfg or not isinstance(cfg["monitors"], dict):
            raise TypeError(f"{__name__}: 'monitors' must be a dict")

        if "heartbeats" not in cfg or not isinstance(cfg["heartbeats"], dict):
            raise TypeError(f"{__name__}: 'heartbeats' must be a dict")

        if "wdlms" not in cfg or not isinstance(cfg["wdlms"], dict):
            raise TypeError(f"{__name__}: 'wdlms' msut be a dict")

    def _load_monitors(self, monitors_cfg: dict) -> None:
        """Load monitor configurations."""
        for key, cfg in monitors_cfg.items():
            if not isinstance(cfg, dict):
                raise TypeError(
                    f"{__name__}: monitor '{key}' must be a dict, got {type(cfg)}"
                )

            name = cfg["name"]
            if not isinstance(name, str):
                name = key

            self._monitors[key] = Monitor(name, cfg)

    def _load_heartbeats(self, heartbeats_cfg: dict) -> None:
        """Load heartbeat configurations."""
        for key, cfg in heartbeats_cfg.items():
            if not isinstance(cfg, dict):
                raise TypeError(
                    f"{__name__}: heartbeat '{key}' must be a dict, got {type(cfg)}"
                )

            name = cfg["name"]
            if not isinstance(name, str):
                name = key

            retry_limit = cfg["retry_limit"]
            if not isinstance(retry_limit, int):
                raise TypeError(
                    f"{__name__}: retries_max must be an int, got {type(retry_limit)}"
                )

            time_limit = cfg["time_limit"]
            if not isinstance(time_limit, int):
                raise TypeError(
                    f"{__name__}: time_max must be an int, got {type(time_limit)}"
                )

            heartbeat = Heartbeat(name, retry_limit, time_limit)
            self._heartbeats[key] = heartbeat

    def _load_wdlms(self, wdlms_cfg: dict):
        name = wdlms_cfg.get("name")
        if not isinstance(name, str):
            name = "WDLMs Status"

        color = wdlms_cfg.get("color")
        if not isinstance(color, str):
            color = "white"

        dock = wdlms_cfg.get("dock")
        if not isinstance(color, str):
            dock = "left"

        self._wdlms = Wdlms(name, color, dock)

    @property
    def version(self) -> int:
        """Get the configuration version."""
        return self._version

    @property
    def monitors(self) -> Dict[str, Monitor]:
        """Get all configured monitors."""
        return self._monitors

    @property
    def heartbeats(self) -> Dict[str, Heartbeat]:
        """Get all configured heartbeats."""
        return self._heartbeats

    @property
    def wdlms(self) -> Wdlms:
        return self._wdlms

    def process_message(self, msg: Dict):
        cmd = msg["cmd"]
        if not isinstance(cmd, str):
            raise TypeError(f"unable to parse command, must be str, got {type(cmd)}")

        # look for cmd as key in all monitors
        if cmd in self._monitors:
            # if invalid int try parsing as string
            value = msg["value"]
            if not isinstance(value, int):
                try:
                    value = int(value, 0)
                except Exception:
                    raise TypeError(
                        f"unable to parse value, must be int, got {type(value)}"
                    )
            self._process_monitor(cmd, value)

        # look for cmd as key in all heartbeats
        if cmd in self._heartbeats:
            # if invalid int try parsing as string
            value = msg["value"]
            if not isinstance(value, int):
                try:
                    value = int(value, 0)
                except Exception:
                    raise TypeError(
                        f"unable to parse value, must be int, got {type(value)}"
                    )
            self._process_heartbeat(cmd, value)

        # check if cmd is wdlm
        if cmd.lower() == "wdlm":
            # must be parsed as string to get seat data
            value = msg["value"]
            if not isinstance(value, str):
                raise TypeError(f"unable to parse value, must be str, go {type(value)}")
            self._process_wdlms(value)

    def _process_monitor(self, monitor_id: str, value: int) -> Dict[str, Set[State]]:
        """Process a monitor command with the given value."""
        if monitor_id not in self._monitors:
            raise KeyError(f"unknown monitor id: '{monitor_id}'")
        return self._monitors[monitor_id].process(value)

    def _process_heartbeat(self, heartbeat_id: str, value: int) -> None:
        """Process a heartbeat signal."""
        if heartbeat_id not in self._heartbeats:
            raise KeyError(f"Unknown heartbeat id: '{heartbeat_id}'")
        self._heartbeats[heartbeat_id].process(value)

    def _process_wdlms(self, value: str) -> None:
        self.wdlms.process(value)