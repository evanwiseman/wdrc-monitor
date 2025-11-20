from typing import Dict, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from src.models.monitor import Monitor, MonitorEntry
from src.utils.ui import clear_layout


class MonitorEntryWidget(QWidget):
    def __init__(
        self,
        entry: MonitorEntry,
        color: str = "white",
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        self._color = color
        self._entry = entry

        # Entry name label
        self._entry_label = QLabel(entry.name)
        self._entry_label.setStyleSheet(f"color: {color};")
        self._entry_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Entry states layout
        self._states_layout = QHBoxLayout()
        self._states_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        for state in entry.states:
            state_label = QLabel(state.value)
            state_label.setStyleSheet(f"color: {state.color()};")
            self._states_layout.addWidget(state_label)

        # Layout
        self._main_layout = QHBoxLayout()
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.addWidget(self._entry_label)
        self._main_layout.addLayout(self._states_layout)
        self.setLayout(self._main_layout)

    @property
    def entry(self) -> MonitorEntry:
        return self._entry

    @entry.setter
    def entry(self, value: MonitorEntry) -> None:
        self._entry = value
        self._entry_label.setText(value.name)

    def update_states(self) -> None:
        """Update states layout from self._entries"""
        clear_layout(self._states_layout)
        for state in self._entry.states:
            state_label = QLabel(state.value)
            state_label.setStyleSheet(f"color: {state.color()};")
            self._states_layout.addWidget(state_label)


class MonitorWidget(QWidget):
    def __init__(
        self,
        monitor: "Monitor",
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.monitor = monitor

        # Layout
        self._main_layout = QVBoxLayout()
        self._main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._main_layout.setContentsMargins(8, 8, 8, 8)
        self._main_layout.setSpacing(8)
        self._entry_lookup: Dict[str, MonitorEntryWidget] = {}

        # Load all entries
        for key, entry in sorted(monitor.entries.items()):
            entry_widget = MonitorEntryWidget(entry, color=monitor.color)
            self._main_layout.addWidget(entry_widget)
            self._entry_lookup[key] = entry_widget

        self.setLayout(self._main_layout)

    def update_all(self):
        """Update states on all entries"""
        for entry_widget in self._entry_lookup.values():
            entry_widget.update_states()
