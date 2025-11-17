from typing import Optional, Set

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from src.models.entry import Entry
from src.models.state import State
from src.utils.ui import clear_layout


class EntryWidget(QWidget):
    def __init__(
        self,
        entry: Entry,
        parent: Optional[QWidget] = None,
        states: Set[State] = State.UNKNOWN,
    ):
        super().__init__(parent)
        self._entry = entry
        self._entry_label = QLabel(entry.name)
        self._entry_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self._states = states
        self._states_layout = QHBoxLayout()
        self._states_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        for state in states:
            state_label = QLabel(state.value)
            state_label.setStyleSheet(f"color: {state.color()};")
            self._states_layout.addWidget(state_label)

        self._main_layout = QHBoxLayout()
        self._main_layout.addWidget(self._entry_label)
        self._main_layout.addLayout(self._states_layout)
        self.setLayout(self._main_layout)

    @property
    def entry(self) -> Entry:
        return self._entry

    @entry.setter
    def entry(self, value: Entry) -> None:
        self._entry = value
        self._entry_label.setText(value.name)

    @property
    def states(self) -> Set[State]:
        return self._states

    @states.setter
    def states(self, value: Set[State]) -> None:
        self._states = value
        clear_layout(self._states_layout)

        for state in value:
            state_label = QLabel(state.value)
            state_label.setStyleSheet(f"color: {state.color()};")
            self._states_layout.addWidget(state_label)
