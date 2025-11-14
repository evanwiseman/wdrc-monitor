from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget

from src.services.mqtt_service import MqttService


class MainWindow(QMainWindow):
    def __init__(
        self,
        mqtt: MqttService,
        parent: QWidget | None = None,
        flags: Qt.WindowType = Qt.WindowType.Window,
    ) -> None:
        super().__init__(parent, flags)
        self.mqtt = mqtt

        self.setMinimumSize(600, 600)
