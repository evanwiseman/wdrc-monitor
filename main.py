import signal
import sys

from PyQt6.QtCore import QTimer

from src.app import App
from src.services.health_service import HealthService
from src.services.mqtt_service import MqttService
from src.ui.main_window import MainWindow


def main():
    app = App(sys.argv)

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    timer = QTimer()
    timer.start(100)
    timer.timeout.connect(lambda: None)

    mqtt_service = MqttService()
    mqtt_service.connect()

    monitor_service = HealthService()

    main_window = MainWindow(mqtt_service, monitor_service)
    main_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
