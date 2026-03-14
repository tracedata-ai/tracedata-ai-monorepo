import logging
import sys
import structlog

def setup_logging():
    """
    Configures structured logging for the TraceData AI agents.
    Supports both JSON output for production (GCP/AWS/ELK) 
    and pretty-printing for local development.
    """
    
    # 1. Standard library logging configuration
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    # 2. Structlog configuration
    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # If we're in a TTY (terminal), use pretty printing
    if sys.stderr.isatty():
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer()
        ]
    else:
        # For production/monitoring, use JSON
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer()
        ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Returns a contextual logger for a specific module."""
    return structlog.get_logger(name)
