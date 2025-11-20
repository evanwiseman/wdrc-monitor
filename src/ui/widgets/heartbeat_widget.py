from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from src.models.heartbeat import Heartbeat


class HeartbeatWidget(QWidget):
    def __init__(self, heartbeat: Heartbeat, parent: QWidget | None = None):
        super().__init__(parent)

        self._hb = heartbeat

        # Status label showing num retries or timeout
        self._status_label = QLabel()
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Layout
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        layout.addWidget(QLabel(heartbeat.name))
        layout.addWidget(self._status_label)
        self.setLayout(layout)

        # Connect signals
        heartbeat.tick_signal.connect(self._on_tick)
        heartbeat.timeout_signal.connect(self._on_timeout)

        # Show initial state
        self._update_status_label(0)

    def reset(self):
        """Reset the timer"""
        self._hb.reset()

    def _on_tick(self, elapsed):
        """Updates status label with elapsed time. Connect to on_tick."""
        self._update_status_label(elapsed)

    def _on_timeout(self):
        """Updates status label to timeout message. Connect to on_timeout."""
        self._status_label.setText("❌ Heartbeat timed out")

    def _update_status_label(self, elapsed):
        """Updates the status label with new time and number of retries left."""
        time_max = self._hb._time_max
        retries = self._hb._retry_attempt
        retries_max = self._hb._retry_limit

        self._status_label.setText(
            f"{elapsed}s / {time_max}s     {retries}/{retries_max} retries"
        )
