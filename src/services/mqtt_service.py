import logging
from typing import Set

import paho.mqtt.client as mqtt
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from src.config import MqttConfig
from src.constants import MQTT_LOG

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
fh = logging.FileHandler(MQTT_LOG)
logger.addHandler(fh)


class MqttService(QObject):
    # pyqt signals for mqtt events
    message_signal = pyqtSignal(object, object, object)
    connect_signal = pyqtSignal(object, object, object, int)
    connect_fail_signal = pyqtSignal(object, object, int)
    disconnect_signal = pyqtSignal(object, object, int)

    def __init__(self):
        super().__init__()
        self.config = MqttConfig()

        self.client = mqtt.Client()

        self.client.on_connect = self._on_connect
        self.client.on_connect_fail = self._on_connect_fail
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

        self.connected = False

        # retry timer
        self.retry_timer = QTimer()
        self.retry_timer.setInterval(2000)  # 2 seconds
        self.retry_timer.timeout.connect(self._attempt_reconnect)
        self.retry_timer.start()

        # start loop in background thread
        self.client.loop_start()

    def _attempt_reconnect(self):
        """Called by timer — only tries if currently disconnected."""
        if not self.connected:
            logger.info("Trying to connect to MQTT broker...")
            self.connect()

    def connect(self):
        try:
            self.client.username_pw_set(
                username=self.config.username,
                password=self.config.password,
            )

            self.client.connect(
                host=self.config.host,
                port=self.config.port,
            )
        except ConnectionRefusedError:
            logger.warning(f"connection refused {self.config.host}:{self.config.port}")

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def publish(self, topic, payload, qos=0, retain=False):
        self.client.publish(topic, payload, qos, retain)

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
        logger.info(
            f"connected {client.host}:{client.port}: {rc}",
        )
        self.connect_signal.emit(client, userdata, flags, rc)

    def _on_connect_fail(
        self,
        client: mqtt.Client,
        userdata: Set,
        rc: int,
    ):
        self.connected = False
        logger.warning(
            f"connect failed to {self.config.host}:{self.config.port} rc={rc}"
        )
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
        logger.info(f"received message on {msg.topic} from {self.config.host}")
        self.message_signal.emit(client, userdata, msg)
