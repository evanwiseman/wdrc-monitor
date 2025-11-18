from PyQt6.QtCore import QObject


class Heartbeat(QObject):
    def __init__(self, name: str, cfg: dict) -> None:
        super().__init__()
        self._name = name
        pass

    def _load(self, cfg: dict) -> None:
        pass

    def _validate_config_structure(self, cfg: dict) -> None:
        pass
