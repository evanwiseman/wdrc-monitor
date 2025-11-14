import signal
import sys

from PyQt6.QtCore import QTimer

from src.app import Application
from src.services.mqtt_service import MqttService
from src.ui.main_window import MainWindow


def main():
    app = Application(sys.argv)

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    timer = QTimer()
    timer.start(100)
    timer.timeout.connect(lambda: None)

    mqtt = MqttService()
    mqtt.connect()

    main_window = MainWindow(mqtt)
    main_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
