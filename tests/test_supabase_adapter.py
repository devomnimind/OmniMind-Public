from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.integrations.supabase_adapter import (
    SupabaseAdapter,
    SupabaseConfig,
    SupabaseAdapterError,
)


def test_supabase_config_from_text_parses_entries() -> None:
    sample = """
    NEXT_PUBLIC_SUPABASE_URL=https://example.supabase.co
    NEXT_PUBLIC_SUPABASE_ANON_KEY=anon-123
    OMNIMIND_SUPABASE_SERVICE_ROLE_KEY=service-456
    """
    config = SupabaseConfig.from_text(sample)
    assert config is not None
    assert config.url == "https://example.supabase.co"
    assert config.anon_key == "anon-123"
    assert config.service_role_key == "service-456"


def test_supabase_adapter_query_builds_filters() -> None:
    config = SupabaseConfig(url="https://example.supabase.co", anon_key="anon")
    mock_client = MagicMock()
    mock_query = MagicMock()
    mock_response = MagicMock()
    mock_response.error = None
    mock_response.data = [{"key": "value"}]
    mock_query.select.return_value = mock_query
    mock_query.eq.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.execute.return_value = mock_response
    mock_client.table.return_value = mock_query

    with patch(
        "src.integrations.supabase_adapter.create_client", return_value=mock_client
    ):
        adapter = SupabaseAdapter(config)
        result = adapter.query_table("notes", filters={"user_id": 1}, limit=5, offset=2)

    assert result == [{"key": "value"}]
    mock_client.table.assert_called_with("notes")
    mock_query.eq.assert_called_with("user_id", 1)


def test_supabase_adapter_requires_service_key_for_lists() -> None:
    config = SupabaseConfig(url="https://example.supabase.co", anon_key="anon")
    with patch(
        "src.integrations.supabase_adapter.create_client", return_value=MagicMock()
    ):
        adapter = SupabaseAdapter(config)
        with pytest.raises(SupabaseAdapterError):
            adapter.list_tables()
