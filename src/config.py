import json
import logging
from typing import Any, List

from src.constants import (
    APP_CONFIG,
    APP_LOG,
    DARK_STYLESHEET,
    DEFAULT_APP_NAME,
    DEFAULT_APP_THEME,
    DEFAULT_APP_VERSION,
    DEFAULT_MQTT_HOST,
    DEFAULT_MQTT_PASSWORD,
    DEFAULT_MQTT_PORT,
    DEFAULT_MQTT_SUBSCRIPTIONS,
    DEFAULT_MQTT_USERNAME,
    DEFAULT_ORGANIZATION_NAME,
    DEFAULT_RETRIES_MAX,
    LIGHT_STYLESHEET,
    MQTT_CONFIG,
    STYLES_DIR,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
fh = logging.FileHandler(APP_LOG)
logger.addHandler(fh)


class Config:
    def __init__(self, fp: str):
        self._fp = fp
        self._data: dict[str, Any] = {}

        try:
            self.load()
        except Exception as e:
            logger.warning(f"failed to load app config: {str(e)}")

    def save(self):
        """Saves the config to the specified filepath"""
        with open(self._fp, "w") as f:
            json.dump(self._data, f, indent=4)

    def load(self):
        """Loads the config from the specified filepath"""
        with open(self._fp, "r") as f:
            self._data = json.load(f)

    @property
    def data(self) -> dict:
        return self._data


class AppConfig(Config):
    def __init__(self):
        """Application config loads from json"""
        super().__init__(APP_CONFIG)

    def save(self):
        """Saves the config to the APP_CONFIG"""
        return super().save()

    def load(self):
        """Loads the config from the APP_CONFIG"""
        return super().load()

    @property
    def name(self) -> str:
        """Name specified in filepath or default app name"""
        return self._data.get("name", DEFAULT_APP_NAME)

    @property
    def version(self) -> str:
        """Version specified in filepath or default app version"""
        return self._data.get("version", DEFAULT_APP_VERSION)

    @property
    def organization(self) -> str:
        """Organization specified in filepath or default organization"""
        return self._data.get("organization", DEFAULT_ORGANIZATION_NAME)

    @property
    def theme(self) -> str:
        """Get theme specified in filepath or default theme"""
        return self._data.get("theme", DEFAULT_APP_THEME)

    @theme.setter
    def theme(self, value: str) -> str:
        """Set the theme in the dictionary"""
        self._data["theme"] = value

    @property
    def stylesheets(self) -> dict[str, str]:
        """Gets filepaths for stylesheets"""
        return {
            "light": LIGHT_STYLESHEET,
            "dark": DARK_STYLESHEET,
        }

    def get_stylesheet(self) -> str | None:
        """Gets the stylesheet from the specified theme"""
        try:
            with open(self.stylesheets.get(self.theme, ""), "r") as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"stylesheet not found at {STYLES_DIR}")
        return None


class MqttConfig(Config):
    def __init__(self):
        super().__init__(MQTT_CONFIG)

    def save(self):
        return super().save()

    def load(self):
        return super().load()

    @property
    def host(self) -> str:
        return self._data.get("host", DEFAULT_MQTT_HOST)

    @property
    def port(self) -> int:
        return self._data.get("port", DEFAULT_MQTT_PORT)

    @property
    def username(self) -> str:
        return self._data.get("username", DEFAULT_MQTT_USERNAME)

    @property
    def password(self) -> str:
        return self._data.get("password", DEFAULT_MQTT_PASSWORD)

    @property
    def subscriptions(self) -> List[str]:
        return self._data.get("subscriptions", DEFAULT_MQTT_SUBSCRIPTIONS)

    @property
    def retries_max(self) -> int:
        return self._data.get("retries_max", DEFAULT_RETRIES_MAX)
