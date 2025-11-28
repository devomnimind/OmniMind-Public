"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""Global pytest configuration for OmniMind Phase 7 validation."""

import asyncio
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator

import pytest
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


def get_utc_timestamp() -> str:
    """Return the current UTC timestamp in ISO format ending with 'Z'."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@pytest.fixture
def utc_timestamp() -> str:
    """Fixture that provides a timezone-aware UTC timestamp for tests."""
    return get_utc_timestamp()


@pytest.fixture(scope="session")
def event_loop_policy() -> asyncio.AbstractEventLoopPolicy:
    """Configure the global event loop policy with debug awareness."""

    if sys.platform == "win32":
        policy = asyncio.WindowsSelectorEventLoopPolicy()
    else:
        policy = asyncio.DefaultEventLoopPolicy()

    asyncio.set_event_loop_policy(policy)
    return policy


@pytest.fixture(scope="function")
def event_loop(
    event_loop_policy: asyncio.AbstractEventLoopPolicy,
) -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Yield a fresh event loop per test with debug mode enabled."""

    loop = event_loop_policy.new_event_loop()
    loop.set_debug(True)
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def configure_logging() -> logging.Logger:
    """Ensure consistent debug logging during tests."""

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    return logging.getLogger("tests")


@pytest.fixture(scope="session", autouse=True)
def setup_omnimind_env() -> Generator[None, None, None]:
    """Prepare OmniMind directories and environment variables."""

    omn_home = Path.home() / ".omnimind"
    (omn_home / "audit").mkdir(parents=True, exist_ok=True)
    (omn_home / "logs").mkdir(parents=True, exist_ok=True)
    (omn_home / "memory").mkdir(parents=True, exist_ok=True)
    os.environ["OMNIMIND_HOME"] = str(omn_home)
    yield


def pytest_configure(config: pytest.Config) -> None:
    """Register markers and enforce asyncio debug configuration."""

    config.addinivalue_line("markers", "asyncio: mark tests that use async/await")
    config.addinivalue_line("markers", "slow: mark tests that run slowly")
    config.addinivalue_line("markers", "security: mark security-focused tests")

    if hasattr(config, "option"):
        setattr(config.option, "asyncio_mode", "auto")
        setattr(config.option, "asyncio_default_fixture_loop_scope", "function")
        setattr(config.option, "asyncio_debug", True)
