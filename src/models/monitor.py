from dataclasses import dataclass, field
from typing import Dict, Set

from PyQt6.QtCore import QObject

from src.models.state import State


@dataclass
class MonitorEntry:
    name: str
    masks: Dict[int, State] = field(default_factory=dict)
    states: Set[State] = field(default_factory=lambda: {State.UNKNOWN})

    def evaluate(self, value: int) -> Set[State]:
        """Evaluate a value with the masks stored"""
        active = {state for mask, state in self.masks.items() if value & mask}

        # No matches are found
        if not active:
            active = {State.OFF}

        self.states = active
        return active


class Monitor(QObject):
    def __init__(self, key: str, cfg: Dict) -> None:
        super().__init__()

        self._name = key
        self._color: str = ""
        self._dock: str = ""
        self._entries: Dict[str, MonitorEntry] = {}

        self._load(cfg)

    def _load(self, cfg: dict) -> None:
        """Load in values from a config dictionary"""
        self._validate_config_structure(cfg)

        # Load specifiy values
        self._color = cfg.get("color", "white")
        self._dock = cfg.get("dock", "center")
        self._load_entries(cfg.get("entries", {}))

    def _validate_config_structure(self, cfg: dict) -> None:
        """Validate the config dictionary has all necessary parameters"""
        if not isinstance(cfg, dict):
            raise TypeError(f"{__name__}: config must be a dict, got {type(cfg)}")

        if "color" not in cfg or not isinstance(cfg["color"], str):
            raise TypeError(f"{__name__}: 'color' must be a str")

        if "dock" not in cfg or not isinstance(cfg["dock"], str):
            raise TypeError(f"{__name__}: 'dock' must be a str")

        if "entries" not in cfg or not isinstance(cfg["entries"], dict):
            raise TypeError(f"{__name__}: 'entries' must be a dict")

    def _load_entries(self, entries_cfg: dict) -> None:
        """Loads entries from the entries config"""
        for key, cfg in entries_cfg.items():
            # initialize entry
            entry = MonitorEntry(key)
            self._entries[key] = entry

            # validate cfg type
            if not isinstance(cfg, dict):
                raise TypeError(
                    f"{__name__}: entry '{key}' must be a dict, got {type(cfg)}"
                )

            # extract masks
            raw_masks = cfg["masks"]
            if not isinstance(raw_masks, dict):
                raise TypeError(
                    f"{__name__}: cfg 'masks' must be a dict, got {type(raw_masks)}"
                )
            masks = {int(k, 0): State(v) for k, v in raw_masks.items()}
            entry.masks = masks

    def process(self, value: int) -> Dict[str, Set[State]]:
        """evaluate all entries from the value provided, presumes correlation in masks"""
        return {name: entry.evaluate(value) for name, entry in self._entries.items()}

    @property
    def name(self) -> str:
        return self._name

    @property
    def color(self) -> str:
        return self._color

    @property
    def dock(self) -> str:
        return self._dock

    @property
    def entries(self) -> Dict[str, MonitorEntry]:
        return self._entries
