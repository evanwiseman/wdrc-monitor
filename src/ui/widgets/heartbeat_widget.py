from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from src.models.heartbeat import Heartbeat


class HeartbeatWidget(QWidget):
    def __init__(self, heartbeat: Heartbeat, parent: QWidget | None = None):
        super().__init__(parent)

        self._hb = heartbeat

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QHBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        layout.addWidget(QLabel(heartbeat.name))
        layout.addWidget(self.label)
        self.setLayout(layout)

        # Connect signals
        heartbeat.tick_signal.connect(self._on_tick)
        heartbeat.timeout_signal.connect(self._on_timeout)

        # Show initial state
        self._update_label(0)

    def reset(self):
        self._hb.reset()

    def _on_tick(self, elapsed):
        self._update_label(elapsed)

    def _on_timeout(self):
        self.label.setText("❌ Heartbeat timed out")

    def _update_label(self, elapsed):
        time_max = self._hb._time_max
        retries = self._hb._retry_attempt
        retries_max = self._hb._retry_limit

        self.label.setText(
            f"{elapsed}s / {time_max}s     {retries}/{retries_max} retries"
        )
