import asyncio

import pytest

from web.backend import main


class DummyWebSocket:
    def __init__(self, headers: dict[str, str], query_params: dict[str, str]) -> None:
        self.headers = headers
        self.query_params = query_params


@pytest.mark.parametrize(
    "user, password",
    [
        ("admin", "secret"),
        ("test_user", "s3cr3t!"),
    ],
)
def test_expected_ws_token_encodes_credentials(user: str, password: str) -> None:
    main._dashboard_user = user
    main._dashboard_pass = password

    expected = main._expected_ws_token()
    assert expected == main.b64encode(f"{user}:{password}".encode()).decode()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "header_value",
    [
        "Basic abc123",
        "basic abc123",
    ],
)
async def test_authorize_websocket_accepts_basic_header(header_value: str) -> None:
    user = "admin"
    password = "omnimind2025!"
    main._dashboard_user = user
    main._dashboard_pass = password
    expected_token = main._expected_ws_token()
    websocket = DummyWebSocket({"authorization": f"Basic {expected_token}"}, {})

    assert await main._authorize_websocket(websocket)


@pytest.mark.asyncio
async def test_authorize_websocket_accepts_query_param() -> None:
    user = "agent"
    password = "agentpass"
    main._dashboard_user = user
    main._dashboard_pass = password
    expected_token = main._expected_ws_token()
    websocket = DummyWebSocket({}, {"auth_token": expected_token})

    assert await main._authorize_websocket(websocket)


@pytest.mark.asyncio
async def test_authorize_websocket_rejects_missing_token() -> None:
    main._dashboard_user = "admin"
    main._dashboard_pass = "omnimind"
    websocket = DummyWebSocket({}, {})

    assert not await main._authorize_websocket(websocket)
