from pathlib import Path
from typing import Iterable

import pytest

from src.integrations import MCPClient, MCPConfig, MCPServer
from src.integrations.mcp_client import MCPClientError


def _start_mcp_server(tmp_path: Path, allowed_paths: Iterable[str] | None = None) -> MCPServer:
    config = MCPConfig(
        host="127.0.0.1",
        port=0,
        allowed_paths=list(allowed_paths) if allowed_paths else [str(tmp_path)],
        max_read_size=16 * 1024,
        allowed_extensions=["txt", "md"],
    )
    server = MCPServer(config=config, allowed_roots=config.allowed_paths)
    server.start()
    return server


def test_mcp_read_write_round_trip(tmp_path: Path) -> None:
    server = _start_mcp_server(tmp_path)
    try:
        client = MCPClient(server.url)
        test_file = tmp_path / "phase8.txt"
        result = client.write_file(str(test_file), "phase8 payload")
        assert result["size"] > 0
        assert Path(result["path"]).exists()
        content = client.read_file(str(test_file))
        assert content == "phase8 payload"
        stats = client.stat(str(test_file))
        assert stats["is_file"]
        listing = client.list_dir(str(tmp_path))
        assert any(entry["name"] == "phase8.txt" for entry in listing["entries"])
        metrics = client.get_metrics()
        assert metrics["metrics"]["total_requests"] >= 4
    finally:
        server.stop()


def test_mcp_path_validation(tmp_path: Path) -> None:
    server = _start_mcp_server(tmp_path)
    try:
        client = MCPClient(server.url)
        with pytest.raises(MCPClientError):
            client.read_file("/etc/passwd")
    finally:
        server.stop()


def test_mcp_extension_blacklist(tmp_path: Path) -> None:
    server = _start_mcp_server(tmp_path)
    try:
        client = MCPClient(server.url)
        with pytest.raises(MCPClientError):
            client.write_file(str(tmp_path / "binary.bin"), "data")
    finally:
        server.stop()
