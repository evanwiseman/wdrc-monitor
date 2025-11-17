from typing import Dict, Optional, Set

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.models.monitor import Monitor
from src.models.state import State
from src.ui.widgets.entry_widget import EntryWidget


class MonitorWidget(QWidget):
    def __init__(
        self,
        monitor: "Monitor",
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.monitor = monitor

        self._main_layout = QVBoxLayout()
        self._main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._main_layout.addWidget(QLabel(monitor.name))

        self._entry_layout = QVBoxLayout()
        self._entry_lookup: Dict[str, EntryWidget] = {}

        for name, entry in sorted(monitor.entries.items()):
            entry_widget = EntryWidget(entry)
            self._entry_layout.addWidget(entry_widget)
            self._entry_lookup[name] = entry_widget

        self._main_layout.addLayout(self._entry_layout)

        self.setLayout(self._main_layout)

    def update_all(self, states_dict: Dict[str, Set[State]]):
        for name, states in states_dict:
            if name not in self._entry_lookup:
                raise KeyError(f"unknown entry {name}")
            self._entry_lookup[name].states = states
