import json
import logging
from pathlib import Path
from PySide6.QtCore import QSettings
from typing import Any, Dict

from legends_labs.core.constants import CONFIG_FILE

class AppSettings:
    def __init__(self):
        self.settings = QSettings("LegendsLabs", "LegendsLabsApp")

    def get(self, key: str, default: Any = None) -> Any:
        val = self.settings.value(key, default)
        return val

    def set(self, key: str, value: Any):
        self.settings.setValue(key, value)

class AppConfig:
    def __init__(self):
        self.config_path = CONFIG_FILE
        self.data: Dict[str, Any] = {}
        self.load()

    def load(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {}
        else:
            self.data = {}

    def save(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except (OSError, TypeError) as exc:
            logging.getLogger(__name__).warning("Failed to save config: %s", exc)

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        d = self.data
        for k in keys:
            if isinstance(d, dict) and k in d:
                d = d[k]
            else:
                return default
        return d

    def set(self, key: str, value: Any):
        keys = key.split(".")
        d = self.data
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value
        self.save()

# ---------------------------------------------------------------------------
# Lazy singletons – avoids creating QObjects at import time
# ---------------------------------------------------------------------------
_settings: AppSettings | None = None
_config: AppConfig | None = None

def get_settings() -> AppSettings:
    """Return the global AppSettings singleton, creating it on first call."""
    global _settings
    if _settings is None:
        _settings = AppSettings()
    return _settings

def get_config() -> AppConfig:
    """Return the global AppConfig singleton, creating it on first call."""
    global _config
    if _config is None:
        _config = AppConfig()
    return _config

# Backward-compatible module-level attributes so that existing code like
#   ``from legends_labs.core.config import settings``
# continues to work.  The instances are still created lazily on first access.
def __getattr__(name: str):
    if name == "settings":
        return get_settings()
    if name == "config":
        return get_config()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
