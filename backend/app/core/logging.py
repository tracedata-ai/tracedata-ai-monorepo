"""
TraceData Backend — Centralised Logging Setup.

Cross-cutting concern: every module in the app calls `get_logger(__name__)`
and this module ensures they all write to the same handlers with the same format.

WHY a separate module instead of `logging.basicConfig()`?
  - basicConfig is one-shot and can't be reconfigured after the first call.
  - dictConfig (loaded from logging.yaml) can set per-logger levels, multiple
    handlers, and custom formatters — without touching any importing module.
  - The YAML file lives at the backend root so ops teams can tune log levels
    without a code deploy (just restart the container with a mounted config).

Usage in any module:
    from app.core.logging import get_logger
    logger = get_logger(__name__)
    logger.info("Vehicle %s ingested telemetry ping", vehicle_id)
"""

import logging
import logging.config
import logging.handlers
from pathlib import Path

import yaml

# Path to the logging configuration file at the backend root
_CONFIG_PATH = Path(__file__).parents[3] / "logging.yaml"

# Directory where rotating log files are written
_LOGS_DIR = Path(__file__).parents[3] / "logs"


class _RequestIdFilter(logging.Filter):
    """
    Logging filter that injects a `request_id` into every log record.

    If the request context has set a request ID (via contextvars), it shows
    up in the structured log line. Outside a request context, it shows '-'.

    This makes it trivial to grep all log lines for a single HTTP request:
        grep "req-abc123" logs/backend.log
    """

    def filter(self, record: logging.LogRecord) -> bool:
        # Lazily import to avoid circular imports at module load time
        try:
            from app.core.middleware import get_request_id
            record.request_id = get_request_id()
        except Exception:
            record.request_id = "-"
        return True


def setup_logging() -> None:
    """
    Initialise the logging system from `logging.yaml`.

    Called ONCE at application startup (in main.py lifespan).
    Creates the `logs/` directory if it doesn't exist.
    Falls back to a sensible basicConfig if the YAML file is missing.
    """
    # Ensure the log output directory exists
    _LOGS_DIR.mkdir(parents=True, exist_ok=True)

    if _CONFIG_PATH.exists():
        with _CONFIG_PATH.open() as f:
            config = yaml.safe_load(f)
        logging.config.dictConfig(config)

        # Attach the request ID filter to both handlers so every line has it
        request_filter = _RequestIdFilter()
        for handler in logging.root.handlers:
            handler.addFilter(request_filter)

        logging.getLogger("app").info("Logging configured from %s", _CONFIG_PATH)
    else:
        # Graceful fallback — should never happen in Docker (YAML is COPY'd in)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
        )
        logging.warning("logging.yaml not found at %s — using basicConfig fallback", _CONFIG_PATH)


def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger scoped to the calling module.

    Args:
        name: Pass `__name__` — Python will use the module's dotted path
              (e.g. `app.api.v1.fleet`) as the logger name, making it easy
              to trace exactly which file emitted a log line.

    Returns:
        A standard Python Logger instance.

    Example:
        logger = get_logger(__name__)
        logger.info("Trip %s started", trip_id)
    """
    return logging.getLogger(name)
