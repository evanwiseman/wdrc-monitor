from typing import Optional, Set

import paho.mqtt.client as mqtt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from src.services.mqtt_service import MqttService


class MqttWidget(QWidget):
    def __init__(self, mqtt_service: MqttService, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._mqtt_service = mqtt_service

        # Connect/Disconnect Button
        self._connect_button = QPushButton("Connect")
        self._connect_button.clicked.connect(self.on_connect_clicked)

        # Status Label
        self._status_label = QLabel("Unknown")
        self._status_label.setStyleSheet("color:gray;")

        # Connect Signals
        self._mqtt_service.retries_signal.connect(self.handle_retries)
        self._mqtt_service.connect_signal.connect(self.handle_connect)
        self._mqtt_service.connect_fail_signal.connect(self.handle_connect_fail)
        self._mqtt_service.disconnect_signal.connect(self.handle_disconnect)

        # Layout
        self._main_layout = QHBoxLayout()
        self._main_layout.setContentsMargins(4, 4, 4, 4)
        self._main_layout.setSpacing(8)
        self._main_layout.addWidget(self._connect_button)
        self._main_layout.addWidget(QLabel("Connection Status:"))
        self._main_layout.addWidget(self._status_label)
        self.setLayout(self._main_layout)

    def _update_status(self, text: str, color: str):
        """Update status label with text and color."""
        self._status_label.setText(text)
        self._status_label.setStyleSheet(f"color: {color};")

    def _status_connected(self):
        self._update_status("Connected", "green")
        self._connect_button.setText("Disconnect")
        self._connect_button.setDisabled(False)

    def _status_connecting(self):
        self._update_status("Connecting...", "orange")
        self._connect_button.setText("Connecting...")
        self._connect_button.setDisabled(True)

    def _status_disconnected(self):
        self._update_status("Disconnected", "gray")
        self._connect_button.setText("Connect")
        self._connect_button.setDisabled(False)

    def on_connect_clicked(self):
        """Handle connect/disconnect button clicks."""
        if self._mqtt_service.client.is_connected():
            self._mqtt_service.cancel()
            self._status_disconnected()
        else:
            if self._mqtt_service.retry_attempt == 0:
                self._mqtt_service.start()
                self._status_connecting()
            else:
                self._mqtt_service.cancel()
                self._status_disconnected()

    def handle_retries(self, retries: int):
        """Handle retry attempts."""
        if retries >= self._mqtt_service.retry_limit:
            # Max retries reached
            self._update_status("Connection Failed (Max Retries)", "red")
            self._connect_button.setText("Connect")
            self._connect_button.setDisabled(False)
        elif retries > 0:
            # Currently retrying
            self._update_status(
                f"Reconnecting... ({retries}/{self._mqtt_service.retry_limit})",
                "orange",
            )
            self._connect_button.setText("Cancel")
            self._connect_button.setDisabled(False)

    def handle_connect(
        self,
        client: mqtt.Client,
        userdata: Set,
        flags: mqtt.ConnectFlags,
        rc: mqtt.ReasonCode,
    ):
        """Handle successful connection."""
        self._status_connected()

    def handle_connect_fail(
        self,
        client: mqtt.Client,
        userdata: Set,
        rc: int,
    ):
        """Handle connection failure."""
        # Note: Status will be updated by handle_retrying if retries are happening
        if self._mqtt_service.retry_attempt != 0:
            self._update_status("Connection Failed", "red")
            self._connect_button.setText("Connect")
            self._connect_button.setDisabled(False)

    def handle_disconnect(
        self,
        client: mqtt.Client,
        userdata: Set,
        rc: int,
    ):
        """Handle disconnection."""
        if rc != 0:
            # Unexpected disconnect - will trigger retry
            self._update_status("Disconnected (Reconnecting...)", "orange")
            self._connect_button.setText("Retrying...")
            self._connect_button.setDisabled(True)
        else:
            # Clean disconnect
            self._status_disconnected()
