"""Logging setup for Legend's Labs using loguru.

Call ``setup_logging()`` once at application startup.  After that, any module
can simply do ``from loguru import logger`` and start logging.
"""

from __future__ import annotations

import sys

from loguru import logger

from legends_labs.core.constants import (
    LOG_CONSOLE_FORMAT,
    LOG_FORMAT,
    LOG_RETENTION_COUNT,
    LOG_ROTATION_SIZE,
    LOGS_DIR,
)

_LOGGING_CONFIGURED: bool = False


def setup_logging(*, verbose: bool = False) -> None:
    """Configure loguru sinks for the application.

    This function is idempotent — calling it more than once is a no-op.

    Parameters
    ----------
    verbose:
        When ``True`` the console sink is set to ``DEBUG`` level, otherwise
        ``INFO``.
    """
    global _LOGGING_CONFIGURED  # noqa: PLW0603
    if _LOGGING_CONFIGURED:
        return

    # Remove the default stderr sink so we can add our own.
    logger.remove()

    # --- Console sink (coloured) -------------------------------------------
    console_level = "DEBUG" if verbose else "INFO"
    logger.add(
        sys.stderr,
        format=LOG_CONSOLE_FORMAT,
        level=console_level,
        colorize=True,
        backtrace=True,
        diagnose=verbose,
    )

    # --- File sink (rotating) ----------------------------------------------
    log_file = LOGS_DIR / "legends_labs_{time:YYYY-MM-DD}.log"
    logger.add(
        str(log_file),
        format=LOG_FORMAT,
        level="DEBUG",
        rotation=LOG_ROTATION_SIZE,
        retention=LOG_RETENTION_COUNT,
        compression="zip",
        backtrace=True,
        diagnose=True,
        enqueue=True,  # thread-safe writes
    )

    logger.info(
        "Logging initialised  ·  console={} file={}",
        console_level,
        LOGS_DIR,
    )
    _LOGGING_CONFIGURED = True
