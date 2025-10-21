"""
Structured Logging Configuration for PURPURA

Provides structured logging with JSON output, request context, and correlation IDs.
Uses structlog for structured logging with seamless integration to standard logging.

Environment Variables:
    LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default: INFO
    LOG_FORMAT: Output format (json, console). Default: json in production, console in dev
    ENVIRONMENT: Environment name (development, staging, production). Default: development
"""
import logging
import sys
import os
from typing import Any, Dict, Optional
from datetime import datetime
from contextvars import ContextVar

import structlog
from structlog.types import EventDict, WrappedLogger
from pythonjsonlogger import jsonlogger


# Context variables for request-scoped data
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
endpoint_var: ContextVar[Optional[str]] = ContextVar("endpoint", default=None)
rate_limit_var: ContextVar[Optional[Dict[str, Any]]] = ContextVar("rate_limit", default=None)


def add_request_context(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """
    Add request context to log entries

    Injects request_id, user_id, endpoint, and rate_limit info into every log entry
    """
    request_id = request_id_var.get()
    if request_id:
        event_dict["request_id"] = request_id

    user_id = user_id_var.get()
    if user_id:
        event_dict["user_id"] = user_id

    endpoint = endpoint_var.get()
    if endpoint:
        event_dict["endpoint"] = endpoint

    rate_limit = rate_limit_var.get()
    if rate_limit:
        event_dict["rate_limit"] = rate_limit

    return event_dict


def add_timestamp(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add ISO timestamp to log entries"""
    event_dict["timestamp"] = datetime.utcnow().isoformat() + "Z"
    return event_dict


def add_log_level(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add log level to event dict"""
    if method_name == "warn":
        # Normalize warn to warning
        event_dict["level"] = "warning"
    else:
        event_dict["level"] = method_name
    return event_dict


def add_logger_name(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add logger name to event dict"""
    # Get the logger name from the record if available
    record = event_dict.get("_record")
    if record:
        event_dict["logger"] = record.name
    return event_dict


def drop_color_message_key(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """
    Remove internal structlog keys from final output

    Removes keys used by ConsoleRenderer for colored output
    """
    event_dict.pop("color_message", None)
    return event_dict


def configure_structlog(
    log_level: str = "INFO",
    log_format: str = "auto",
    environment: str = "development"
) -> None:
    """
    Configure structlog with appropriate processors and formatters

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Output format (json, console, auto). Auto chooses based on environment
        environment: Environment name (development, staging, production)
    """
    # Determine format
    if log_format == "auto":
        # Use JSON in production, console in development
        use_json = environment.lower() in ("production", "staging")
    else:
        use_json = log_format.lower() == "json"

    # Shared processors for both structlog and stdlib logging
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        add_timestamp,
        add_request_context,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if use_json:
        # JSON output for production
        renderer = structlog.processors.JSONRenderer()
    else:
        # Console output for development with colors
        renderer = structlog.dev.ConsoleRenderer(
            colors=True,
            exception_formatter=structlog.dev.better_traceback,
        )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            *shared_processors,
            drop_color_message_key,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level.upper())

    # Set uvicorn loggers to use our formatter
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(logger_name)
        logger.handlers = [handler]
        logger.propagate = False


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured structlog logger

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("user_login", user_id="123", ip="192.168.1.1")
        # Output (JSON format):
        # {"event": "user_login", "user_id": "123", "ip": "192.168.1.1",
        #  "timestamp": "2025-10-21T18:30:00Z", "level": "info", "logger": "myapp"}
    """
    return structlog.get_logger(name)


def set_request_context(
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    endpoint: Optional[str] = None,
    rate_limit: Optional[Dict[str, Any]] = None
) -> None:
    """
    Set request context for current async context

    This context will be automatically included in all log entries
    within the same request.

    Args:
        request_id: Unique request identifier
        user_id: User ID making the request
        endpoint: API endpoint being called
        rate_limit: Rate limit info (limit, remaining, reset)

    Example:
        >>> set_request_context(
        ...     request_id="req_123",
        ...     user_id="user_456",
        ...     endpoint="/api/v1/risk",
        ...     rate_limit={"limit": 60, "remaining": 45}
        ... )
    """
    if request_id is not None:
        request_id_var.set(request_id)
    if user_id is not None:
        user_id_var.set(user_id)
    if endpoint is not None:
        endpoint_var.set(endpoint)
    if rate_limit is not None:
        rate_limit_var.set(rate_limit)


def clear_request_context() -> None:
    """
    Clear request context

    Should be called at the end of request processing
    """
    request_id_var.set(None)
    user_id_var.set(None)
    endpoint_var.set(None)
    rate_limit_var.set(None)


# Initialize logging on module import
_log_level = os.getenv("LOG_LEVEL", "INFO")
_log_format = os.getenv("LOG_FORMAT", "auto")
_environment = os.getenv("ENVIRONMENT", "development")

configure_structlog(
    log_level=_log_level,
    log_format=_log_format,
    environment=_environment
)


# Example usage
if __name__ == "__main__":
    logger = get_logger(__name__)

    # Simple log
    logger.info("application_started", version="1.0.0")

    # Log with context
    set_request_context(
        request_id="req_abc123",
        user_id="user_456",
        endpoint="/api/v1/test"
    )
    logger.info("request_received", method="GET", path="/api/v1/test")

    # Log with additional fields
    logger.warning(
        "rate_limit_approaching",
        remaining=5,
        limit=60,
        percentage=8.3
    )

    # Error log with exception
    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.error("error_occurred", exc_info=True, error_type=type(e).__name__)

    clear_request_context()
