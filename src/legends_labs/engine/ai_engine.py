"""AI Engine — central registry for AI model back-ends.

This module implements a **registry pattern**.  ``AIEngine`` is intentionally
minimal right now; concrete model adapters (e.g. Whisper, Qwen, RVC) will
register themselves here as they are integrated.

Usage
-----
Import the singleton via the lazy accessor::

    from legends_labs.engine.ai_engine import get_ai_engine
    engine = get_ai_engine()
"""

from PySide6.QtCore import QObject


class AIEngine(QObject):
    """Registry that discovers, loads, and routes inference requests to AI
    model back-ends.

    The class is intentionally a stub during early development.  As each AI
    model is integrated it will be registered here so that the rest of the
    application has a single entry-point for inference.
    """

    def __init__(self):
        super().__init__()


_ai_engine_instance: AIEngine | None = None


def get_ai_engine() -> AIEngine:
    """Return the application-wide ``AIEngine`` singleton (created on first call)."""
    global _ai_engine_instance  # noqa: PLW0603
    if _ai_engine_instance is None:
        _ai_engine_instance = AIEngine()
    return _ai_engine_instance
