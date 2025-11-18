from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDockWidget, QMainWindow, QTabWidget, QWidget

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

    def init_ui(self):
        # Central document area
        self.document_tabs = QTabWidget()
        self.document_tabs.setTabsClosable(True)
        self.document_tabs.setMovable(True)
        self.document_tabs.setDocumentMode(True)
        self.document_tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.document_tabs)

        # Create dock widgets for each monitor
        for name, monitor in self.health_service.monitors.items():
            monitor_widget = MonitorWidget(monitor)
            monitor_scroll = ScrollWidget()
            monitor_scroll.addWidget(monitor_widget)

            position = monitor.dock.lower()
            if position == "center":
                self.add_document(monitor_scroll, name)
                continue

            dock = QDockWidget(name, self)
            dock.setWidget(monitor_scroll)
            dock.setObjectName(f"{name}DockWidget")
            dock.setFeatures(
                QDockWidget.DockWidgetFeature.DockWidgetMovable
                | QDockWidget.DockWidgetFeature.DockWidgetClosable
                | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            )

            # Place dock based on monitor.dock
            if position == "left":
                self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
            elif position == "right":
                self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
            elif position == "top":
                self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, dock)
            elif position == "bottom":
                self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)

    def close_tab(self, index: int):
        """Handle tab close requests"""
        widget = self.document_tabs.widget(index)
        if widget:
            widget.deleteLater()
        self.document_tabs.removeTab(index)

    def add_document(self, widget: QWidget, title: str):
        """Add a new document tab"""
        index = self.document_tabs.addTab(widget, title)
        self.document_tabs.setCurrentIndex(index)
        return index
