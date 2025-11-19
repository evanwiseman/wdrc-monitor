import logging
from typing import Set

import paho.mqtt.client as mqtt
from PyQt6.QtCore import QThread, pyqtSignal

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

    _attempt_retry_signal = pyqtSignal()
    retries_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.config = MqttConfig()

        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self.client.on_connect_fail = self._on_connect_fail

        self._retry_attempt = 0
        self._should_retry = False
        self._attempt_retry_signal.connect(self._retry)

    @property
    def retry_attempt(self) -> int:
        """Current number of connection retry attempts."""
        return self._retry_attempt

    @property
    def retry_limit(self) -> int:
        """Maximum number of retry attempts from config."""
        return self.config.retry_limit

    def run(self):
        """Start MQTT connection and event loop."""
        self._should_retry = True
        self._do_connect()

    def stop(self):
        """Stop loop, disconnect from broker, and quit thread"""
        self.client.loop_stop()
        self.client.disconnect()
        self.quit()

    def cancel(self):
        self._should_retry = False
        self._reset_retries()
        self.stop()

    def _do_connect(self):
        try:
            # Set username and password, connect to MQTT broker, and start loop
            self.client.username_pw_set(self.config.username, self.config.password)
            self.client.connect(self.config.host, self.config.port)
            self.client.loop_start()
        except Exception:
            self.stop()
            self._on_connect_fail(self.client, None, 0x80)

    def _reset_retries(self):
        """Reset the retry counter."""
        self._retry_attempt = 0

    def _retry(self):
        """Attempt to reconnect with retry limit."""
        if not self._should_retry:
            self._reset_retries()
            logger.info("retry cancelled by user")
            return

        self._retry_attempt += 1
        logger.info(f"retries left: {self._retry_attempt} / {self.config.retry_limit}")
        self.retries_signal.emit(self._retry_attempt)

        if self._retry_attempt >= self.config.retry_limit:
            logger.error(f"max retries ({self.config.retry_limit}) reached. Giving up.")
            self._reset_retries()
            return

        # ensure thread is fully dead before restart
        if self.isRunning():
            logger.info("waiting for thread to stop before retry...")
            self.wait()

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
        self.connect_signal.emit(client, userdata, flags, rc)
        logger.info(f"connected to {client.host}:{client.port}: {rc}")

        self._reset_retries()  # reset retries if we've successfully connected

    def _on_connect_fail(
        self,
        client: mqtt.Client,
        userdata: Set,
        rc: int,
    ):
        self.connected = False
        self.connect_fail_signal.emit(client, userdata, rc)
        logger.warning(
            f"failed connecting to {self.config.host}:{self.config.port} rc={rc}"
        )

        self._attempt_retry_signal.emit()

    def _on_disconnect(
        self,
        client: mqtt.Client,
        userdata: Set,
        rc: int,
    ):
        self.connected = False
        self.disconnect_signal.emit(client, userdata, rc)
        logger.info(f"disconnected from {self.config.host}:{self.config.port} rc={rc}")

        if rc != 0:
            logger.warning("Unexpected disconnection, attempting to reconnect...")
            self._attempt_retry_signal.emit()
        else:
            self._reset_retries()  # reset retries if we've succeeded

    def _on_message(
        self,
        client: mqtt.Client,
        userdata: Set,
        msg: mqtt.MQTTMessage,
    ):
        logger.info(f"received message on {msg.topic} from {self.config.host}")
        self.message_signal.emit(client, userdata, msg)
