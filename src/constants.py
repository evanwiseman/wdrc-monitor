from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
ASSETS_DIR = PROJECT_ROOT / "assets"
CONFIG_DIR = PROJECT_ROOT / "config"
LOGS_DIR = PROJECT_ROOT / "logs"

# Asset paths
ICONS_DIR = ASSETS_DIR / "icons"
IMAGES_DIR = ASSETS_DIR / "images"
STYLES_DIR = ASSETS_DIR / "styles"

# App files
LIGHT_STYLESHEET = STYLES_DIR / "light.css"
DARK_STYLESHEET = STYLES_DIR / "dark.css"
APP_CONFIG = CONFIG_DIR / "app.json"
APP_LOG = LOGS_DIR / "app.log"

# Application constants
DEFAULT_APP_NAME = "My Application"
DEFAULT_APP_THEME = "dark"
DEFAULT_APP_VERSION = "1.0.0"
DEFAULT_ORGANIZATION_NAME = "Your Company"

# UI constants
DEFAULT_WINDOW_MIN_WIDTH = 800
DEFAULT_WINDOW_MIN_HEIGHT = 600
DEFAULT_FONT_SIZE = 12

# MQTT files
MQTT_CONFIG = CONFIG_DIR / "mqtt.json"
MQTT_LOG = LOGS_DIR / "mqtt.log"

# MQTT constants
DEFAULT_MQTT_HOST = "localhost"
DEFAULT_MQTT_PORT = 1883
DEFAULT_MQTT_USERNAME = ""
DEFAULT_MQTT_PASSWORD = ""
DEFAULT_MQTT_SUBSCRIPTIONS = ["ppss/health"]

# Health Monitor files
HEALTH_CONFIG = CONFIG_DIR / "health.json"
HEALTH_LOG = LOGS_DIR / "health.log"
