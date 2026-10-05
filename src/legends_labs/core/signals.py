"""Global signal bus for Legend's Labs.

The ``SignalBus`` is a QObject singleton that exposes PySide6 ``Signal``
instances.  Any component can connect to these signals without knowing about
the emitter — classic pub/sub via Qt's thread-safe signal/slot mechanism.

Usage::

    from legends_labs.core.signals import signal_bus

    signal_bus.task_started.connect(my_handler)
    signal_bus.task_started.emit("my-task-id")
"""

from __future__ import annotations

import threading

from PySide6.QtCore import QObject, Signal


class SignalBus(QObject):
    """Application-wide signal hub.

    Signals are grouped by subsystem.  All signals are emitted on the Qt
    thread that owns this object (normally the main/GUI thread).
    """

    # ------------------------------------------------------------------
    # Model / VRAM manager
    # ------------------------------------------------------------------
    model_loaded = Signal(str)          # model_id
    model_unloaded = Signal(str)        # model_id
    vram_updated = Signal(int, int)     # used_mb, total_mb

    # ------------------------------------------------------------------
    # Project management
    # ------------------------------------------------------------------
    project_opened = Signal(str)        # project file path
    project_saved = Signal(str)         # project file path
    project_closed = Signal()

    # ------------------------------------------------------------------
    # Background task lifecycle
    # ------------------------------------------------------------------
    task_started = Signal(str)                  # task_id
    task_progress = Signal(str, int, str)       # task_id, percent, message
    task_finished = Signal(str)                 # task_id
    task_error = Signal(str, str)               # task_id, error_message

    # ------------------------------------------------------------------
    # Audio engine
    # ------------------------------------------------------------------
    playback_position_changed = Signal(float)   # position in seconds
    playback_state_changed = Signal(str)        # "playing" / "paused" / "stopped"

    # ------------------------------------------------------------------
    # Pipeline
    # ------------------------------------------------------------------
    pipeline_node_dirty = Signal(str)           # node_id
    pipeline_executed = Signal()


class _SignalBusFactory:
    """Thread-safe lazy singleton factory for :class:`SignalBus`.

    The singleton is created the first time ``signal_bus`` is accessed.
    Because ``QObject`` construction requires a running ``QCoreApplication``,
    we defer creation until first use rather than module-import time.
    """

    _instance: SignalBus | None = None
    _lock = threading.Lock()

    @classmethod
    def get(cls) -> SignalBus:
        """Return the global :class:`SignalBus` instance, creating it if needed."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = SignalBus()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Tear down the singleton (useful in tests)."""
        with cls._lock:
            cls._instance = None


class _SignalBusProxy:
    """Module-level descriptor that transparently delegates attribute access
    to the lazily-created :class:`SignalBus` singleton.

    This lets callers write ``signal_bus.task_started.emit(...)`` at module
    scope without worrying about import-time QApplication existence.
    """

    def __getattr__(self, name: str) -> object:
        return getattr(_SignalBusFactory.get(), name)


# Public singleton — import this.
signal_bus: SignalBus = _SignalBusProxy()  # type: ignore[assignment]
