import json
from typing import List, Optional, Set

import paho.mqtt.client as mqtt
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QDockWidget,
    QFrame,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QWidget,
)

from src.services.health_service import HealthService
from src.services.mqtt_service import MqttService
from src.ui.widgets.heartbeat_widget import HeartbeatWidget
from src.ui.widgets.monitor_widget import MonitorWidget
from src.ui.widgets.scroll_widget import ScrollWidget


class MainWindow(QMainWindow):
    def __init__(
        self,
        mqtt_service: MqttService,
        health_service: HealthService,
        parent: Optional[QWidget] = None,
        flags: Qt.WindowType = Qt.WindowType.Window,
    ) -> None:
        super().__init__(parent, flags)
        self._mqtt_service = mqtt_service
        self.health_service = health_service

        self.setMinimumSize(800, 600)
        self.init_ui()

        # Attach mqtt handlers
        self._mqtt_service.connect_signal.connect(self.handle_connect)
        self._mqtt_service.connect_fail_signal.connect(self.handle_connect_fail)
        self._mqtt_service.disconnect_signal.connect(self.handle_disconnect)
        self._mqtt_service.message_signal.connect(self.handle_message)

    def init_ui(self):
        # Central document area
        self.document_tabs = QTabWidget()
        self.document_tabs.setTabsClosable(True)
        self.document_tabs.setMovable(True)
        self.document_tabs.setDocumentMode(True)
        self.document_tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.document_tabs)

        # Create menubar for document and dock control
        menu_bar = self.menuBar()

        view_menu = menu_bar.addMenu("View")
        self._view_actions: dict[str, QAction] = {}

        file_menu = menu_bar.addMenu("File")
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        # Create dock widgets for each monitor
        self.monitor_widgets: List[MonitorWidget] = []
        for name, monitor in self.health_service.monitors.items():
            monitor_widget = MonitorWidget(monitor)
            self.monitor_widgets.append(monitor_widget)
            monitor_scroll = ScrollWidget()
            monitor_scroll.addWidget(monitor_widget)

            position = monitor.dock.lower()
            if position == "center":
                self.add_document(monitor_scroll, name)
                action = self.create_tab_toggle_action(name, monitor_scroll)
                view_menu.addAction(action)
                self._view_actions[name] = action
                continue

            dock = QDockWidget(name, self)
            dock.setWidget(monitor_scroll)
            dock.setObjectName(f"{name}DockWidget")
            dock.setFeatures(
                QDockWidget.DockWidgetFeature.DockWidgetMovable
                | QDockWidget.DockWidgetFeature.DockWidgetClosable
                | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            )
            action = dock.toggleViewAction()
            view_menu.addAction(action)
            self._view_actions[name] = action

            # Place dock based on monitor.dock
            if position == "left":
                self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
            elif position == "right":
                self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
            elif position == "top":
                self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, dock)
            elif position == "bottom":
                self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)

        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        separator = QFrame()

        self._heartbeat_widgets: List[HeartbeatWidget] = []
        hb_items = list(self.health_service.heartbeats.items())
        for idx, (name, heartbeat) in enumerate(hb_items):
            heartbeat_widget = HeartbeatWidget(heartbeat)
            self._heartbeat_widgets.append(heartbeat_widget)
            status_bar.addWidget(heartbeat_widget)

            # Separator, only between widgets
            if idx < len(hb_items) - 1:
                separator = QFrame()
                separator.setFrameShape(QFrame.Shape.VLine)
                separator.setFrameShadow(QFrame.Shadow.Plain)
                status_bar.addWidget(separator)

        # Create toolbar to monitor mqtt status
        self.mqtt_status_label = QLabel("Unknown")
        self.mqtt_status_label.setStyleSheet("color:gray;")

        self._connect_button = QPushButton("Connect")
        self._connect_button.clicked.connect(self.handle_connect_button_clicked)

        tool_bar = QToolBar()
        tool_bar.setObjectName("mqttToolBar")
        tool_bar.addWidget(self._connect_button)
        tool_bar.addWidget(QLabel("Connection Status:"))
        tool_bar.addWidget(self.mqtt_status_label)
        self.addToolBar(tool_bar)

    def close_tab(self, index: int):
        """Handle tab close requests"""
        widget = self.document_tabs.widget(index)

        if widget:
            title = self.document_tabs.tabText(index)
            self.document_tabs.removeTab(index)

            # Uncheck the toggle action if it exists
            action = self._view_actions.get(title)
            if action and action.isChecked():
                # Block signals to avoid triggering the toggled slot
                action.blockSignals(True)
                action.setChecked(False)
                action.blockSignals(False)

    def create_tab_toggle_action(self, name: str, widget: QWidget) -> QAction:
        action = QAction(name, self)
        action.setCheckable(True)
        action.setChecked(True)  # initially visible

        def toggled(checked: bool):
            if checked:
                # Add the tab back if it was hidden
                if self.document_tabs.indexOf(widget) == -1:
                    index = self.document_tabs.addTab(widget, name)
                    self.document_tabs.setCurrentIndex(index)
            else:
                # Hide the tab
                idx = self.document_tabs.indexOf(widget)
                if idx != -1:
                    self.document_tabs.removeTab(idx)

        action.toggled.connect(toggled)
        return action

    def add_document(self, widget: QWidget, title: str):
        """Add a new document tab"""
        index = self.document_tabs.addTab(widget, title)
        self.document_tabs.setCurrentIndex(index)
        return index

    # ========================
    # Handlers
    # ========================

    def handle_timeout(self):
        QMessageBox.warning(self, "Timeout", f"{self.sender.name} has timed out")
        self._mqtt_service.disconnect()

    def handle_connect_button_clicked(self):
        if self._mqtt_service.client.is_connected():
            self._mqtt_service.stop()
        else:
            self._connect_button.setText("Connecting...")
            self._mqtt_service.start()

    def handle_message(
        self,
        client: mqtt.Client,
        userdata: Set,
        mqtt_msg: mqtt.MQTTMessage,
    ):
        msg: dict = json.loads(mqtt_msg.payload.decode("utf-8"))
        if "ppss/health" in mqtt_msg.topic.lower():
            try:
                self.health_service.process_message(msg)
            except Exception as e:
                print(str(e))

        for widget in self.monitor_widgets:
            widget.update_all()

    def handle_connect(
        self,
        client: mqtt.Client,
        userdata: Set,
        flags: mqtt.ConnectFlags,
        rc: mqtt.ReasonCode,
    ):
        self._connect_button.setText("Disconnect")
        self.mqtt_status_label.setText("Connected")
        self.mqtt_status_label.setStyleSheet("color:green;")

    def handle_connect_fail(
        self,
        client: mqtt.Client,
        userdata: Set,
        rc: int,
    ):
        self._connect_button.setText("Connect")
        self.mqtt_status_label.setText("Connection Failed")
        self.mqtt_status_label.setStyleSheet("color:orange;")

    def handle_disconnect(
        self,
        client: mqtt.Client,
        userdata: Set,
        rc: int,
    ):
        self._connect_button.setText("Connect")
        self.mqtt_status_label.setText("Disconnected")
        self.mqtt_status_label.setStyleSheet("color:red;")