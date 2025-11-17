from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget


class TimerWidget(QWidget):
    timeout = pyqtSignal()

    def __init__(
        self, title: str, ping: int, time_max: int, parent: QWidget | None = None
    ):
        super().__init__(parent)

        self.title = title
        self.ping = ping
        self.time_max = time_max
        self.time = 0

        self._timer = QTimer()
        self._timer.timeout.connect(self.updateTimer)

        self._time_label = QLabel(f"{self.time}s")

        title_label = QLabel(title)

        self.status_label = QLabel("Unknown")
        self.status_label.setStyleSheet("color: gray;")

        self._main_layout = QHBoxLayout()
        self._main_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(8)
        self._main_layout.addWidget(title_label)
        self._main_layout.addWidget(self.status_label)
        self._main_layout.addWidget(self._time_label)
        self.setLayout(self._main_layout)

    def start(self):
        self._timer.start(1000)

    def stop(self):
        self._timer.stop()

    def setStatus(self, status: str):
        self.status_label.setText(status)
        if status == "On":
            self.status_label.setStyleSheet("color: green;")
        elif status == "Off":
            self.status_label.setStyleSheet("color: gray;")
        elif status == "Unknown":
            self.status_label.setStyleSheet("color: gray;")
        elif status == "Failed":
            self.status_label.setStyleSheet("color: red;")

    def updatePing(self, ping: int):
        if self.ping != ping:
            self.ping = ping
            self.time = 0
            self._time_label.setText(f"{self.time}s")
            self.setStatus("On")
            self.stop()
            self.start()

    def updateTimer(self):
        self.time += 1
        if self.time >= self.time_max:
            if self.time >= self.time_max + 5:
                self.setStatus("Failed")
                self.timeout.emit()
                self.stop()
            else:
                self._timer.start(1000)
        else:
            self._time_label.setText(f"{self.time}s")
            self._timer.start(1000)

    def getStatus(self):
        return self.status_label.text()

    def reset(self):
        self.ping = 0
        self.time = 0
        self._time_label.setText(f"{self.time}s")
        self.setStatus("Unknown")
        self.stop()
