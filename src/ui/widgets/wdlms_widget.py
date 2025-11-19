from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from src.models.wdlms import WdlmEntry, Wdlms
from src.utils.ui import clear_layout


class WdlmEntryWidget(QWidget):
    def __init__(
        self,
        wdlm_entry: WdlmEntry,
        color: str,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self._wdlm_entry = wdlm_entry
        self._color = color

        # Name
        self._name_label = QLabel(wdlm_entry.name)
        self._name_label.setStyleSheet(f"color: {color};")
        self._name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # State
        self._state_label = QLabel(wdlm_entry.state.value)
        self._state_label.setStyleSheet(f"color: {wdlm_entry.state.color()};")
        self._state_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Layout
        self._main_layout = QHBoxLayout()
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.addWidget(self._name_label)
        self._main_layout.addWidget(self._state_label)
        self.setLayout(self._main_layout)


class WdlmsWidget(QWidget):
    def __init__(
        self,
        wdlms: Wdlms,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self._wdlms = wdlms

        # Layout
        self._main_layout = QVBoxLayout()
        self._main_layout.setContentsMargins(8, 8, 8, 8)
        self._main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._main_layout.setSpacing(8)

        for key, entry in wdlms.entries.items():
            entry_widget = WdlmEntryWidget(entry, wdlms.color)
            self._main_layout.addWidget(entry_widget)

        self.setLayout(self._main_layout)

    def update_all(self):
        clear_layout(self._main_layout)
        for key, entry in self._wdlms.entries.items():
            entry_widget = WdlmEntryWidget(entry, self._wdlms.color)
            self._main_layout.addWidget(entry_widget)
