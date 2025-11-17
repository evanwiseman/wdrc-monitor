from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QLayout,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class ScrollWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._scroll_layout = QVBoxLayout()
        self._scroll_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        self._scroll_layout.setDirection(QVBoxLayout.Direction.TopToBottom)
        self._scroll_layout.setContentsMargins(0, 0, 0, 0)
        self._scroll_layout.setSpacing(8)

        self._scroll_widget = QWidget()
        self._scroll_widget.setLayout(self._scroll_layout)
        self._scroll_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self._scroll_area = QScrollArea()
        self._scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self._scroll_area.verticalScrollBar().setMinimumWidth(20)
        self._scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self._scroll_area.horizontalScrollBar().setMinimumHeight(20)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setWidget(self._scroll_widget)

        self._main_layout = QVBoxLayout()
        self._main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        self._main_layout.addWidget(self._scroll_area)
        self.setLayout(self._main_layout)

    def addWidget(self, widget: QWidget) -> None:
        widget.setParent(self._scroll_widget)
        self._scroll_layout.addWidget(widget)

    def findWidget(self, widget: QWidget) -> int:
        for i in range(self._scroll_layout.count()):
            if self._scroll_layout.itemAt(i).widget() == widget:
                return i
        return -1

    def findLayout(self, layout: QLayout) -> int:
        for i in range(self._scroll_layout.count()):
            if self._scroll_layout.itemAt(i) == layout:
                return i
        return -1

    def removeWidget(self, widget: QWidget) -> None:
        index = self.findWidget(widget)
        if index != -1:
            self._scroll_layout.removeWidget(widget)
            widget.setParent(None)

    def removeLayout(self, layout: QLayout) -> None:
        index = self.findLayout(layout)
        if index != -1:
            self._scroll_layout.removeItem(layout)
            layout.setParent(None)
