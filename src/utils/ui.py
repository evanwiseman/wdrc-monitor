from PyQt6.QtWidgets import QLayout, QLayoutItem, QWidgetItem


def clear_layout(layout: QLayout) -> None:
    for i in reversed(range(layout.count())):
        item = layout.itemAt(i)
        if isinstance(item, QWidgetItem):
            widget = item.widget()
            if widget is not None:
                layout.removeWidget(widget)
                widget.setParent(None)
        elif isinstance(item, QLayoutItem):
            sub_layout = item.layout()
            if sub_layout is not None:
                clear_layout(sub_layout)
                layout.removeItem(item)
                item.setParent(None)
