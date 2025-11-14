import logging

from PyQt6.QtWidgets import QApplication

from src.config import AppConfig
from src.constants import APP_LOG

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
fh = logging.FileHandler(APP_LOG)
logger.addHandler(fh)


class Application(QApplication):
    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        self.config = AppConfig()
        self.setApplicationName(self.config.name)
        self.setApplicationVersion(self.config.version)
        self.setOrganizationName(self.config.organization)

        self.setStyleSheet(self.config.get_stylesheet())
