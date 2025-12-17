"""Type stubs for structlog library.

This module provides type hints for the structlog structured logging library,
enabling full type checking support in the OmniMind project.
"""

from typing import Any, Protocol, TypeVar, overload

__all__ = ["get_logger", "BoundLogger", "BoundLoggerProtocol"]

_T = TypeVar("_T")

class BoundLoggerProtocol(Protocol):
    """Protocol defining the interface of a bound logger.

    A bound logger supports structured logging with keyword arguments
    and can be bound to additional context.
    """

    def bind(self, **new_values: Any) -> "BoundLogger":
        """Bind additional context to the logger.

        Args:
            **new_values: Key-value pairs to add to logging context.

        Returns:
            A new logger instance with the bound context.
        """
        ...

    def unbind(self, *keys: str) -> "BoundLogger":
        """Remove bound context from the logger.

        Args:
            *keys: Keys to remove from logging context.

        Returns:
            A new logger instance without the specified context.
        """
        ...

    def try_unbind(self, *keys: str) -> "BoundLogger":
        """Remove bound context from the logger if present.

        Args:
            *keys: Keys to remove from logging context.

        Returns:
            A new logger instance without the specified context.
        """
        ...

    def new(self, **new_values: Any) -> "BoundLogger":
        """Create a new logger with replaced context.

        Args:
            **new_values: Key-value pairs for the new context.

        Returns:
            A new logger instance with the new context.
        """
        ...

    def msg(self, event: str, **kw: Any) -> Any:
        """Log a message with keyword arguments.

        Args:
            event: The log message/event name.
            **kw: Additional structured data.

        Returns:
            The return value from the logging chain.
        """
        ...

    def debug(self, event: str | None = None, **kw: Any) -> Any:
        """Log a debug level message.

        Args:
            event: The log message/event name.
            **kw: Additional structured data.

        Returns:
            The return value from the logging chain.
        """
        ...

    def info(self, event: str | None = None, **kw: Any) -> Any:
        """Log an info level message.

        Args:
            event: The log message/event name.
            **kw: Additional structured data.

        Returns:
            The return value from the logging chain.
        """
        ...

    def warning(self, event: str | None = None, **kw: Any) -> Any:
        """Log a warning level message.

        Args:
            event: The log message/event name.
            **kw: Additional structured data.

        Returns:
            The return value from the logging chain.
        """
        ...

    def warn(self, event: str | None = None, **kw: Any) -> Any:
        """Log a warning level message (alias).

        Args:
            event: The log message/event name.
            **kw: Additional structured data.

        Returns:
            The return value from the logging chain.
        """
        ...

    def error(self, event: str | None = None, **kw: Any) -> Any:
        """Log an error level message.

        Args:
            event: The log message/event name.
            **kw: Additional structured data.

        Returns:
            The return value from the logging chain.
        """
        ...

    def critical(self, event: str | None = None, **kw: Any) -> Any:
        """Log a critical level message.

        Args:
            event: The log message/event name.
            **kw: Additional structured data.

        Returns:
            The return value from the logging chain.
        """
        ...

    def exception(self, event: str | None = None, **kw: Any) -> Any:
        """Log an exception with traceback.

        Args:
            event: The log message/event name.
            **kw: Additional structured data.

        Returns:
            The return value from the logging chain.
        """
        ...

    def log(self, level: int | str, event: str | None = None, **kw: Any) -> Any:
        """Log a message at the specified level.

        Args:
            level: Logging level (int or string).
            event: The log message/event name.
            **kw: Additional structured data.

        Returns:
            The return value from the logging chain.
        """
        ...

class BoundLogger(BoundLoggerProtocol):
    """Concrete implementation of a bound logger.

    This is the actual logger instance returned by get_logger().
    It supports all standard logging levels and context binding.
    """

    def bind(self, **new_values: Any) -> "BoundLogger": ...
    def unbind(self, *keys: str) -> "BoundLogger": ...
    def try_unbind(self, *keys: str) -> "BoundLogger": ...
    def new(self, **new_values: Any) -> "BoundLogger": ...
    def msg(self, event: str, **kw: Any) -> Any: ...
    def debug(self, event: str | None = None, **kw: Any) -> Any: ...
    def info(self, event: str | None = None, **kw: Any) -> Any: ...
    def warning(self, event: str | None = None, **kw: Any) -> Any: ...
    def warn(self, event: str | None = None, **kw: Any) -> Any: ...
    def error(self, event: str | None = None, **kw: Any) -> Any: ...
    def critical(self, event: str | None = None, **kw: Any) -> Any: ...
    def exception(self, event: str | None = None, **kw: Any) -> Any: ...
    def log(self, level: int | str, event: str | None = None, **kw: Any) -> Any: ...

@overload
def get_logger() -> BoundLogger:
    """Get a logger instance without a name.

    Returns:
        A BoundLogger instance for structured logging.
    """
    ...

@overload
def get_logger(name: str) -> BoundLogger:
    """Get a logger instance with a name.

    Args:
        name: The logger name (typically __name__).

    Returns:
        A BoundLogger instance for structured logging.
    """
    ...
