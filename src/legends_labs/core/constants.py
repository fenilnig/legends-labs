"""Application-wide constants for Legend's Labs.

Centralises every magic string, default path, and supported format so the rest
of the codebase never hard-codes them.
"""

from __future__ import annotations

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Application identity
# ---------------------------------------------------------------------------
APP_NAME: str = "Legend's Labs"
APP_SLUG: str = "legends-labs"
APP_VERSION: str = "0.1.0"
APP_AUTHOR: str = "Fenil"
ORG_NAME: str = "LegendsLabs"
ORG_DOMAIN: str = "legends-labs.local"

# ---------------------------------------------------------------------------
# Data directories
# ---------------------------------------------------------------------------
# We explicitly use ~/.legends-labs/ on every platform so the user always
# knows where to find (and backup) their data.
DATA_DIR: Path = Path.home() / ".legends-labs"
LOGS_DIR: Path = DATA_DIR / "logs"
MODELS_DIR: Path = DATA_DIR / "models"
CACHE_DIR: Path = DATA_DIR / "cache"
CONFIG_FILE: Path = DATA_DIR / "config.json"
REGISTRY_FILE: Path = MODELS_DIR / "registry.json"

# Ensure critical directories exist at import time so that downstream code
# can unconditionally write into them.
try:
    for _d in (DATA_DIR, LOGS_DIR, MODELS_DIR, CACHE_DIR):
        _d.mkdir(parents=True, exist_ok=True)
except OSError:
    pass  # best-effort; downstream writes will surface the real error

# ---------------------------------------------------------------------------
# Project files
# ---------------------------------------------------------------------------
PROJECT_EXTENSION: str = ".legendsproj"
PROJECT_CACHE_DIR_NAME: str = ".cache"
AUTOSAVE_INTERVAL_MS: int = 60_000  # 60 seconds

# ---------------------------------------------------------------------------
# Supported audio formats
# ---------------------------------------------------------------------------
SUPPORTED_AUDIO_EXTENSIONS: tuple[str, ...] = (
    ".wav",
    ".mp3",
    ".flac",
    ".ogg",
    ".opus",
    ".m4a",
    ".aac",
    ".wma",
)

EXPORT_FORMATS: tuple[str, ...] = (
    "wav",
    "mp3",
    "flac",
    "ogg",
)

# ---------------------------------------------------------------------------
# Audio defaults
# ---------------------------------------------------------------------------
DEFAULT_SAMPLE_RATE: int = 44_100
DEFAULT_BIT_DEPTH: int = 16
DEFAULT_CHANNELS: int = 1  # mono for speech processing

# ---------------------------------------------------------------------------
# AI / VRAM defaults
# ---------------------------------------------------------------------------
def _detect_device() -> str:
    """Lazily detect the compute device without blocking import time."""
    if sys.platform == "win32":
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
        except Exception:
            pass
    return "cpu"

# DEFAULT_DEVICE is no longer evaluated at import time to avoid 5-second 
# torch import blocking the splash screen. Modules should call _detect_device() directly 
# or VRAMManager handles it. We keep DEFAULT_DEVICE as "cpu" for quick config defaults.
DEFAULT_DEVICE: str = "cpu"
VRAM_HEADROOM_MB: int = 512  # keep this much free VRAM as safety margin

# ---------------------------------------------------------------------------
# Model categories (used by ModelRegistry)
# ---------------------------------------------------------------------------
MODEL_CATEGORIES: tuple[str, ...] = (
    "separation",
    "enhancement",
    "tts",
    "stt",
    "emotion",
    "llm",
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_ROTATION_SIZE: str = "10 MB"
LOG_RETENTION_COUNT: int = 5
LOG_FORMAT: str = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
    "<level>{message}</level>"
)
LOG_CONSOLE_FORMAT: str = (
    "<green>{time:HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{line}</cyan> — "
    "<level>{message}</level>"
)
