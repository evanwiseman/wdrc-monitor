from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
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

        menubar = self.menuBar()

        view_menu = menubar.addMenu("View")
        self._view_actions: dict[str, QAction] = {}

        file_menu = menubar.addMenu("File")
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        # Create dock widgets for each monitor
        for name, monitor in self.health_service.monitors.items():
            monitor_widget = MonitorWidget(monitor)
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
