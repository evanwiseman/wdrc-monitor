import logging

import paho.mqtt.client as mqtt
from PyQt6.QtCore import QObject, pyqtSignal

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
    message_signal = pyqtSignal(mqtt.MQTTMessage)
    connect_signal = pyqtSignal(bool)
    disconnect_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.config = MqttConfig()

        self.client = mqtt.Client()

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

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

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: set,
        flags: mqtt.ConnectFlags,
        rc: mqtt.ReasonCode,
    ):
        logging.info(
            f"connected {client.host}:{client.port}: {rc.getId} {rc.getName()}",
        )

    def _on_message(
        self,
        client: mqtt.Client,
        userdata: set,
        msg: mqtt.MQTTMessage,
    ):
        logging.info(
            f"received message from {client.host}:{client.port} to {msg.topic}",
        )
        self.message_signal.emit(msg)

    def _on_connect_fail(
        self,
        client: mqtt.Client,
        userdata: set,
        rc: mqtt.ReasonCode,
    ):
        pass

    def _on_disconnect(
        self,
        client: mqtt.Client,
        userdata: set,
        rc: mqtt.ReasonCode,
    ):
        logger.info(
            f"{self.config.host}:{self.config.port} - "
            + "disconnected with rc: {rc.getId()} {rc.getName()}",
        )
