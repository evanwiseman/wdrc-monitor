from typing import Dict, Set

from PyQt6.QtCore import QObject

from src.models.entry import Entry
from src.models.state import State


class Monitor(QObject):
    def __init__(self, key: str, cfg: Dict) -> None:
        super().__init__()

        self._name = key
        self._color: str = ""
        self._dock: str = ""
        self._entries: Dict[str, Entry] = {}

        self._load(cfg)

    def _load(self, cfg: dict) -> None:
        self._validate_config_structure(cfg)
        self._color = cfg["color"]
        self._dock = cfg["dock"]
        self._load_entries(cfg["entries"])

    def _validate_config_structure(self, cfg: dict) -> None:
        if not isinstance(cfg, dict):
            raise TypeError(f"{__name__}: config must be a dict, got {type(cfg)}")

        if "color" not in cfg or not isinstance(cfg["color"], str):
            raise TypeError(f"{__name__}: 'color' must be a str")

        if "dock" not in cfg or not isinstance(cfg["dock"], str):
            raise TypeError(f"{__name__}: 'dock' must be a str")

        if "entries" not in cfg or not isinstance(cfg["entries"], dict):
            raise TypeError(f"{__name__}: 'entries' must be a dict")

    def _load_entries(self, entries_cfg: dict) -> None:
        for key, cfg in entries_cfg.items():
            entry = Entry(key)
            self._entries[key] = entry
            if not isinstance(cfg, dict):
                raise TypeError(
                    f"{__name__}: entry '{key}' must be a dict, got {type(cfg)}"
                )

            raw_masks = cfg["masks"]
            if not isinstance(raw_masks, dict):
                raise TypeError(
                    f"{__name__}: cfg 'masks' must be a dict, got {type(raw_masks)}"
                )
            masks = {int(k, 0): State(v) for k, v in raw_masks.items()}
            entry.masks = masks

    def process(self, value: int) -> Dict[str, Set[State]]:
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
    def entries(self) -> Dict[str, Entry]:
        return self._entries
