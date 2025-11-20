import json
from typing import List, Optional, Set

import paho.mqtt.client as mqtt
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QDockWidget,
    QFrame,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QWidget,
)

from src.services.health_service import HealthService
from src.services.mqtt_service import MqttService
from src.ui.widgets.heartbeat_widget import HeartbeatWidget
from src.ui.widgets.monitor_widget import MonitorWidget
from src.ui.widgets.mqtt_widget import MqttWidget
from src.ui.widgets.scroll_widget import ScrollWidget
from src.ui.widgets.wdlms_widget import WdlmsWidget


class MainWindow(QMainWindow):
    def __init__(
        self,
        mqtt_service: MqttService,
        health_service: HealthService,
        parent: Optional[QWidget] = None,
        flags: Qt.WindowType = Qt.WindowType.Window,
    ) -> None:
        super().__init__(parent, flags)
        self.setMinimumSize(800, 600)

        self._mqtt_service = mqtt_service
        self.health_service = health_service

        self.init_menu()
        self.init_status()
        self.init_tool()
        self.init_ui()

        self._mqtt_service.message_signal.connect(self.handle_message)

    def init_menu(self):
        self.menu = self.menuBar()

        self.file_menu = self.menu.addMenu("File")
        exit_action = self.file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        self.view_menu = self.menu.addMenu("View")
        self._view_actions: dict[str, QAction] = {}

    def init_status(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def init_tool(self):
        self.tool = QToolBar()
        self.tool.setObjectName("mqttToolBar")
        self.addToolBar(self.tool)

    def init_ui(self):
        self._init_document_area()

        self._init_monitors()
        self._init_heartbeats()
        self._init_wdlms()
        self._init_mqtt()

        self.setCentralWidget(self.document_tabs)

    # ========================
    # Document Tabs
    # ========================

    def _init_document_area(self) -> None:
        # Central document area
        self.document_tabs = QTabWidget()
        self.document_tabs.setTabsClosable(True)
        self.document_tabs.setMovable(True)
        self.document_tabs.setDocumentMode(True)
        self.document_tabs.tabCloseRequested.connect(self.close_tab)

    def add_document(self, widget: QWidget, title: str):
        """Add a new document tab"""
        index = self.document_tabs.addTab(widget, title)
        self.document_tabs.setCurrentIndex(index)
        return index

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

    # ========================
    # Health Service Widgets
    # ========================

    def _init_monitors(self):
        # Create dock widgets for each monitor
        self.monitor_widgets: List[MonitorWidget] = []
        for key, monitor in self.health_service.monitors.items():
            monitor_widget = MonitorWidget(monitor)
            self.monitor_widgets.append(monitor_widget)
            monitor_scroll = ScrollWidget()
            monitor_scroll.addWidget(monitor_widget)

            position = monitor.dock.lower()
            if position == "center":
                self.add_document(monitor_scroll, monitor.name)
                action = self.create_tab_toggle_action(monitor.name, monitor_scroll)
                self.view_menu.addAction(action)
                self._view_actions[key] = action
                continue

            dock = QDockWidget(monitor.name, self)
            dock.setWidget(monitor_scroll)
            dock.setObjectName(f"{key}DockWidget")
            dock.setFeatures(
                QDockWidget.DockWidgetFeature.DockWidgetMovable
                | QDockWidget.DockWidgetFeature.DockWidgetClosable
                | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            )
            action = dock.toggleViewAction()
            self.view_menu.addAction(action)
            self._view_actions[key] = action

            # Place dock based on monitor.dock
            if position == "left":
                self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
            elif position == "right":
                self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
            elif position == "top":
                self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, dock)
            elif position == "bottom":
                self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)

    def _init_heartbeats(self):
        self._heartbeat_widgets: List[HeartbeatWidget] = []
        hb_items = list(self.health_service.heartbeats.items())
        separator = QFrame()

        for idx, (key, heartbeat) in enumerate(hb_items):
            heartbeat_widget = HeartbeatWidget(heartbeat)
            self._mqtt_service.connect_fail_signal.connect(
                lambda: heartbeat_widget.reset()
            )
            self._mqtt_service.disconnect_signal.connect(
                lambda: heartbeat_widget.reset()
            )
            self._heartbeat_widgets.append(heartbeat_widget)
            self.status.addWidget(heartbeat_widget)

            # Separator, only between widgets
            if idx < len(hb_items) - 1:
                separator = QFrame()
                separator.setFrameShape(QFrame.Shape.VLine)
                separator.setFrameShadow(QFrame.Shadow.Plain)
                self.status.addWidget(separator)

    def _init_wdlms(self):
        self._wdlms_widget = WdlmsWidget(self.health_service.wdlms)
        position = self.health_service.wdlms.dock.lower()
        wdlm_scroll = ScrollWidget()
        wdlm_scroll.addWidget(self._wdlms_widget)
        dock = QDockWidget(self.health_service.wdlms.name, self)
        dock.setWidget(wdlm_scroll)
        dock.setObjectName("wdlmDockWidget")
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        action = dock.toggleViewAction()
        self.view_menu.addAction(action)
        self._view_actions["wdlm"] = action
        # Place dock based on monitor.dock
        if position == "left":
            self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
        elif position == "right":
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        elif position == "top":
            self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, dock)
        elif position == "bottom":
            self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)

    # ========================
    # MQTT Service Widgets
    # ========================

    def _init_mqtt(self):
        # Create toolbar to monitor mqtt status
        mqtt_widget = MqttWidget(self._mqtt_service)
        self.tool.addWidget(mqtt_widget)

    # ========================
    # Handlers
    # ========================

    def handle_timeout(self):
        QMessageBox.warning(self, "Timeout", f"{self.sender.name} has timed out")
        self._mqtt_service.disconnect()

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

        self._wdlms_widget.update_all()
