from typing import Dict, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.models.monitor import Monitor
from src.ui.widgets.entry_widget import EntryWidget


class MonitorWidget(QWidget):
    def __init__(
        self,
        monitor: "Monitor",
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.monitor = monitor

        self._entry_layout = QVBoxLayout()

        self._entry_layout.setSpacing(8)
        self._entry_lookup: Dict[str, EntryWidget] = {}

        for name, entry in sorted(monitor.entries.items()):
            entry_widget = EntryWidget(entry, color=monitor.color)
            self._entry_layout.addWidget(entry_widget)
            self._entry_lookup[name] = entry_widget

        name_label = QLabel(monitor.name)
        name_label.setStyleSheet(f"color: {monitor.color};")

        self._main_layout = QVBoxLayout()
        self._main_layout.setContentsMargins(8, 8, 8, 8)
        self._main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._main_layout.addWidget(name_label)
        self._main_layout.addLayout(self._entry_layout)

        self.setLayout(self._main_layout)

    def update_all(self):
        for entry_widget in self._entry_lookup.values():
            entry_widget.update_states()
