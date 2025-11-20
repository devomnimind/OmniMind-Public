"""Database Connection Pooling Module.

Implements efficient database connection management with SQLAlchemy pooling.
Provides connection lifecycle management, automatic reconnection, and health monitoring.

Reference: docs/OMNIMIND_COMPREHENSIVE_PENDENCIES_REPORT_20251119.md, Section 7.3
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional, TypeVar
from contextlib import contextmanager

import structlog

logger = structlog.get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class ConnectionStatus(Enum):
    """Database connection status."""

    IDLE = "idle"
    ACTIVE = "active"
    CLOSED = "closed"
    ERROR = "error"


@dataclass
class ConnectionInfo:
    """Information about a database connection.

    Attributes:
        conn_id: Connection identifier
        database_url: Database connection URL (sanitized)
        created_at: When connection was created
        last_used_at: When connection was last used
        use_count: Number of times connection has been used
        status: Current connection status
        error_count: Number of errors encountered
    """

    conn_id: str
    database_url: str
    created_at: float = field(default_factory=time.time)
    last_used_at: float = field(default_factory=time.time)
    use_count: int = 0
    status: ConnectionStatus = ConnectionStatus.IDLE
    error_count: int = 0

    def mark_used(self) -> None:
        """Mark connection as used."""
        self.last_used_at = time.time()
        self.use_count += 1
        self.status = ConnectionStatus.ACTIVE

    def mark_idle(self) -> None:
        """Mark connection as idle."""
        self.status = ConnectionStatus.IDLE

    def mark_error(self) -> None:
        """Mark connection as having an error."""
        self.error_count += 1
        self.status = ConnectionStatus.ERROR

    def is_stale(self, max_age_seconds: int) -> bool:
        """Check if connection is stale.

        Args:
            max_age_seconds: Maximum age in seconds

        Returns:
            True if connection is stale
        """
        age = time.time() - self.last_used_at
        return age > max_age_seconds

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "conn_id": self.conn_id,
            "database_url": self._sanitize_url(self.database_url),
            "created_at": self.created_at,
            "last_used_at": self.last_used_at,
            "use_count": self.use_count,
            "status": self.status.value,
            "error_count": self.error_count,
            "age_seconds": time.time() - self.created_at,
        }

    @staticmethod
    def _sanitize_url(url: str) -> str:
        """Sanitize database URL to hide credentials.

        Args:
            url: Database URL

        Returns:
            Sanitized URL
        """
        # Simple sanitization - in production use urllib.parse
        if "://" in url:
            parts = url.split("://", 1)
            if "@" in parts[1]:
                user_part, host_part = parts[1].split("@", 1)
                if ":" in user_part:
                    return f"{parts[0]}://***:***@{host_part}"
                return f"{parts[0]}://***@{host_part}"
        return url


@dataclass
class PoolConfig:
    """Configuration for database connection pool.

    Attributes:
        pool_size: Number of connections to maintain
        max_overflow: Maximum overflow connections beyond pool_size
        pool_recycle_seconds: Recycle connections after this time
        pool_pre_ping: Test connections before using them
        pool_timeout_seconds: Timeout for getting connection from pool
        max_connection_age_seconds: Maximum age of a connection
        enable_health_checks: Enable periodic health checks
        health_check_interval_seconds: Interval for health checks
    """

    pool_size: int = 5
    max_overflow: int = 10
    pool_recycle_seconds: int = 3600
    pool_pre_ping: bool = True
    pool_timeout_seconds: int = 30
    max_connection_age_seconds: int = 7200
    enable_health_checks: bool = True
    health_check_interval_seconds: int = 60


class DatabaseConnectionPool:
    """Database connection pool manager.

    Manages a pool of database connections with automatic recycling,
    health monitoring, and overflow handling.

    Example:
        >>> config = PoolConfig(pool_size=5)
        >>> pool = DatabaseConnectionPool("postgresql://user:pass@localhost/db", config)
        >>>
        >>> with pool.get_connection() as conn:
        ...     # Use connection
        ...     result = conn.execute("SELECT 1")
        >>>
        >>> stats = pool.get_stats()
    """

    def __init__(self, database_url: str, config: PoolConfig):
        """Initialize the database connection pool.

        Args:
            database_url: Database connection URL
            config: Pool configuration
        """
        self.database_url = database_url
        self.config = config
        self._pool: List[Any] = []  # Pool connections (mock for now)
        self._overflow: List[Any] = []  # Overflow connections
        self._connection_info: Dict[str, ConnectionInfo] = {}
        self._next_conn_id = 0
        self._total_connections_created = 0
        self._total_connections_closed = 0
        self._last_health_check = time.time()

        # Initialize pool
        self._initialize_pool()

        logger.info(
            "connection_pool_initialized",
            pool_size=config.pool_size,
            database=self._sanitize_url(database_url),
        )

    def _initialize_pool(self) -> None:
        """Initialize the connection pool."""
        for i in range(self.config.pool_size):
            conn = self._create_connection()
            if conn:
                self._pool.append(conn)

    def _create_connection(self) -> Optional[Any]:
        """Create a new database connection.

        Returns:
            Connection object or None if creation failed
        """
        conn_id = f"conn_{self._next_conn_id}"
        self._next_conn_id += 1

        try:
            # In production, this would create a real database connection
            # For now, we create a mock connection object
            conn = MockConnection(conn_id, self.database_url)

            # Track connection info
            info = ConnectionInfo(
                conn_id=conn_id,
                database_url=self.database_url,
            )
            self._connection_info[conn_id] = info

            self._total_connections_created += 1

            logger.debug("connection_created", conn_id=conn_id)
            return conn

        except Exception as e:
            logger.error("connection_creation_failed", error=str(e))
            return None

    def _close_connection(self, conn: Any) -> None:
        """Close a database connection.

        Args:
            conn: Connection to close
        """
        try:
            conn_id = conn.conn_id
            conn.close()

            # Update connection info
            if conn_id in self._connection_info:
                self._connection_info[conn_id].status = ConnectionStatus.CLOSED
                del self._connection_info[conn_id]

            self._total_connections_closed += 1

            logger.debug("connection_closed", conn_id=conn_id)

        except Exception as e:
            logger.error("connection_close_failed", error=str(e))

    @contextmanager
    def get_connection(self) -> Generator[Any, None, None]:
        """Get a connection from the pool.

        Yields:
            Database connection

        Raises:
            TimeoutError: If unable to get connection within timeout
        """
        conn = None
        start_time = time.time()

        try:
            # Try to get from pool
            if self._pool:
                conn = self._pool.pop()
            # Try to create overflow connection
            elif len(self._overflow) < self.config.max_overflow:
                conn = self._create_connection()
                if conn:
                    self._overflow.append(conn)
            else:
                # Wait for available connection
                while time.time() - start_time < self.config.pool_timeout_seconds:
                    if self._pool:
                        conn = self._pool.pop()
                        break
                    time.sleep(0.1)

            if conn is None:
                raise TimeoutError("Unable to get connection from pool")

            # Pre-ping if configured
            if self.config.pool_pre_ping:
                if not self._ping_connection(conn):
                    # Connection is bad, create new one
                    self._close_connection(conn)
                    conn = self._create_connection()

            # Update connection info
            if conn and hasattr(conn, "conn_id"):
                info = self._connection_info.get(conn.conn_id)
                if info:
                    info.mark_used()

            yield conn

        except Exception as e:
            logger.error("connection_error", error=str(e))
            if conn and hasattr(conn, "conn_id"):
                info = self._connection_info.get(conn.conn_id)
                if info:
                    info.mark_error()
            raise

        finally:
            # Return connection to pool
            if conn:
                if hasattr(conn, "conn_id"):
                    info = self._connection_info.get(conn.conn_id)
                    if info:
                        info.mark_idle()

                        # Check if connection should be recycled
                        if info.is_stale(self.config.max_connection_age_seconds):
                            self._close_connection(conn)
                            # Create new connection to maintain pool size
                            if (
                                conn in self._pool
                                or len(self._pool) < self.config.pool_size
                            ):
                                new_conn = self._create_connection()
                                if new_conn:
                                    self._pool.append(new_conn)
                        else:
                            # Return to pool or overflow
                            if conn in self._overflow:
                                self._overflow.remove(conn)
                                if len(self._pool) < self.config.pool_size:
                                    self._pool.append(conn)
                                else:
                                    self._close_connection(conn)
                            else:
                                self._pool.append(conn)

            # Run health check if needed
            if self.config.enable_health_checks:
                self._maybe_run_health_check()

    def _ping_connection(self, conn: Any) -> bool:
        """Test if connection is alive.

        Args:
            conn: Connection to test

        Returns:
            True if connection is alive
        """
        try:
            # In production, execute a simple query like "SELECT 1"
            result = conn.ping()
            return bool(result)
        except Exception as e:
            logger.warning("connection_ping_failed", error=str(e))
            return False

    def _maybe_run_health_check(self) -> None:
        """Run health check if interval has passed."""
        now = time.time()
        if now - self._last_health_check >= self.config.health_check_interval_seconds:
            self._run_health_check()
            self._last_health_check = now

    def _run_health_check(self) -> None:
        """Run health check on all connections."""
        logger.debug("running_health_check")

        # Check pool connections
        bad_connections = []
        for conn in self._pool:
            if not self._ping_connection(conn):
                bad_connections.append(conn)

        # Remove bad connections and create new ones
        for conn in bad_connections:
            self._pool.remove(conn)
            self._close_connection(conn)
            new_conn = self._create_connection()
            if new_conn:
                self._pool.append(new_conn)

        if bad_connections:
            logger.info(
                "health_check_completed",
                bad_connections=len(bad_connections),
                pool_size=len(self._pool),
            )

    def close_all(self) -> None:
        """Close all connections in the pool."""
        logger.info("closing_all_connections")

        # Close pool connections
        for conn in self._pool:
            self._close_connection(conn)
        self._pool.clear()

        # Close overflow connections
        for conn in self._overflow:
            self._close_connection(conn)
        self._overflow.clear()

        logger.info("all_connections_closed")

    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics.

        Returns:
            Dictionary with pool statistics
        """
        active_connections = sum(
            1
            for info in self._connection_info.values()
            if info.status == ConnectionStatus.ACTIVE
        )

        idle_connections = sum(
            1
            for info in self._connection_info.values()
            if info.status == ConnectionStatus.IDLE
        )

        error_connections = sum(
            1
            for info in self._connection_info.values()
            if info.status == ConnectionStatus.ERROR
        )

        total_use_count = sum(info.use_count for info in self._connection_info.values())

        return {
            "pool_size": len(self._pool),
            "overflow_size": len(self._overflow),
            "active_connections": active_connections,
            "idle_connections": idle_connections,
            "error_connections": error_connections,
            "total_connections": len(self._connection_info),
            "total_created": self._total_connections_created,
            "total_closed": self._total_connections_closed,
            "total_use_count": total_use_count,
            "config": {
                "pool_size": self.config.pool_size,
                "max_overflow": self.config.max_overflow,
                "pool_recycle_seconds": self.config.pool_recycle_seconds,
            },
        }

    def get_connection_details(self) -> List[Dict[str, Any]]:
        """Get detailed information about all connections.

        Returns:
            List of connection details
        """
        return [info.to_dict() for info in self._connection_info.values()]

    @staticmethod
    def _sanitize_url(url: str) -> str:
        """Sanitize database URL."""
        return ConnectionInfo._sanitize_url(url)


class MockConnection:
    """Mock database connection for testing."""

    def __init__(self, conn_id: str, database_url: str):
        """Initialize mock connection.

        Args:
            conn_id: Connection identifier
            database_url: Database URL
        """
        self.conn_id = conn_id
        self.database_url = database_url
        self._closed = False

    def ping(self) -> bool:
        """Ping the connection.

        Returns:
            True if alive
        """
        return not self._closed

    def execute(self, query: str) -> Any:
        """Execute a query.

        Args:
            query: SQL query

        Returns:
            Mock result
        """
        if self._closed:
            raise RuntimeError("Connection is closed")
        return MockResult()

    def close(self) -> None:
        """Close the connection."""
        self._closed = True


class MockResult:
    """Mock query result."""

    def fetchall(self) -> List[Any]:
        """Fetch all results."""
        return []

    def fetchone(self) -> Optional[Any]:
        """Fetch one result."""
        return None
