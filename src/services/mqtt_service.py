import logging
from typing import Set

import paho.mqtt.client as mqtt
from PyQt6.QtCore import QThread, QTimer, pyqtSignal

from src.config import MqttConfig
from src.constants import MQTT_LOG

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
fh = logging.FileHandler(MQTT_LOG)
logger.addHandler(fh)


class MqttService(QThread):
    # pyqt signals for mqtt events
    message_signal = pyqtSignal(object, object, object)
    connect_signal = pyqtSignal(object, object, object, int)
    connect_fail_signal = pyqtSignal(object, object, int)
    disconnect_signal = pyqtSignal(object, object, int)

    def __init__(self):
        super().__init__()
        self.config = MqttConfig()

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self.client.on_connect_fail = self._on_connect_fail

        self._retry_timer = QTimer()
        self._retry_timer.setInterval(2000)
        self._retry_timer.timeout.connect(self._retry)

        self._retries = 0

    def run(self):
        try:
            # Set username and password, connect to MQTT broker, and start loop
            self.client.username_pw_set(self.config.username, self.config.password)
            self.client.connect(self.config.host, self.config.port)
            self.client.loop_start()
        except Exception:
            self.stop()
            self._on_connect_fail(self.client, None, 0x80)

    def stop(self):
        # Stop loop, disconnect from broker, and quit thread
        self.client.loop_stop()
        self.client.disconnect()
        self.quit()

    def _retry(self):
        if self._retries >= self.config.retries_max:
            self._retry_timer.stop()
            return
        self._retries += 1
        self.start()

    # ========================
    # MQTT CALLBACKS
    # ========================

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: Set,
        flags: mqtt.ConnectFlags,
        rc: int,
    ):
        self.connected = True
        for topic in self.config.subscriptions:
            self.client.subscribe(topic)
        logger.info(f"connected to {client.host}:{client.port}: {rc}")
        self.connect_signal.emit(client, userdata, flags, rc)

    def _on_connect_fail(
        self,
        client: mqtt.Client,
        userdata: Set,
        rc: int,
    ):
        self.connected = False
        logger.warning(
            f"failed connecting to {self.config.host}:{self.config.port} rc={rc}"
        )

        self._retry_timer.start()
        self.connect_fail_signal.emit(client, userdata, rc)

    def _on_disconnect(
        self,
        client: mqtt.Client,
        userdata: Set,
        rc: int,
    ):
        self.connected = False
        logger.info(f"disconnected from {self.config.host}:{self.config.port} rc={rc}")
        self.disconnect_signal.emit(client, userdata, rc)

    def _on_message(
        self,
        client: mqtt.Client,
        userdata: Set,
        msg: mqtt.MQTTMessage,
    ):
        logger.info(
            f"received message on {msg.topic} from {self.config.host}: {msg.payload}"
        )
        self.message_signal.emit(client, userdata, msg)
