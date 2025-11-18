import json
from typing import List, Optional, Set

import paho.mqtt.client as mqtt
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QDockWidget,
    QLabel,
    QMainWindow,
    QTabWidget,
    QToolBar,
    QWidget,
)

from src.services.health_service import HealthService
from src.services.mqtt_service import MqttService
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
        self.mqtt_service = mqtt_service
        self.health_service = health_service

        self.setMinimumSize(800, 600)
        self.init_ui()

        # Attach mqtt handlers
        self.mqtt_service.connect_signal.connect(self.handle_connect)
        self.mqtt_service.connect_fail_signal.connect(self.handle_connect_fail)
        self.mqtt_service.disconnect_signal.connect(self.handle_disconnect)
        self.mqtt_service.message_signal.connect(self.handle_message)

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

        # Create toolbar to monitor mqtt status
        self.mqtt_status_label = QLabel("Unknown")
        self.mqtt_status_label.setStyleSheet("color:gray;")
        tool_bar = QToolBar()
        tool_bar.setObjectName("mqttToolBar")
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

    def handle_message(
        self,
        client: mqtt.Client,
        userdata: Set,
        mqtt_msg: mqtt.MQTTMessage,
    ):
        if "ppss/health" in mqtt_msg.topic.lower():
            try:
                msg: dict = json.loads(mqtt_msg.payload.decode("utf-8"))
                cmd = str(msg.get("cmd", ""))
                if cmd in self.health_service.monitors:
                    value = int(msg.get("value", 0))
                    self.health_service.process_monitor(cmd, value)

                    for widget in self.monitor_widgets:
                        widget.update_all()

            except Exception as e:
                print(str(e))

    def handle_connect(
        self,
        client: mqtt.Client,
        userdata: Set,
        flags: mqtt.ConnectFlags,
        rc: mqtt.ReasonCode,
    ):
        self.mqtt_status_label.setText("Connected")
        self.mqtt_status_label.setStyleSheet("color:green;")

    def handle_connect_fail(
        self,
        client: mqtt.Client,
        userdata: Set,
        rc: int,
    ):
        self.mqtt_status_label.setText("Connection Failed")
        self.mqtt_status_label.setStyleSheet("color:orange;")

    def handle_disconnect(
        self,
        client: mqtt.Client,
        userdata: Set,
        rc: int,
    ):
        self.mqtt_status_label.setText("Disconnected")
        self.mqtt_status_label.setStyleSheet("color:red;")