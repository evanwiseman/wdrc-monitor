from dataclasses import dataclass, field
from typing import Dict

from PyQt6.QtCore import QObject

from src.models.state import State


@dataclass
class WdlmEntry:
    name: str
    state: State = field(default=State.UNKNOWN)


class Wdlms(QObject):
    def __init__(self, name: str, color: str, dock: str):
        super().__init__()
        self._name = name
        self._color = color
        self._dock = dock
        self._entries: Dict[str, WdlmEntry] = {}

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
    def entries(self) -> Dict[str, WdlmEntry]:
        return self._entries

    def process(self, value: str):
        row_index = 0

        for char in reversed(value):
            self._entries[f"wdlm_{row_index}"] = WdlmEntry(
                f"WDLM {(row_index // 2) + 1} {'A-D' if row_index % 2 == 0 else 'E-H'}",
                State.TALKING if char == "1" else State.NOT_TALKING,
            )

            row_index += 1
