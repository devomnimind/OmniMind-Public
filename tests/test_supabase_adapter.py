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

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.integrations.supabase_adapter import (
    SupabaseAdapter,
    SupabaseAdapterError,
    SupabaseConfig,
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

    with patch("src.integrations.supabase_adapter.create_client", return_value=mock_client):
        adapter = SupabaseAdapter(config)
        result = adapter.query_table("notes", filters={"user_id": 1}, limit=5, offset=2)

    assert result == [{"key": "value"}]
    mock_client.table.assert_called_with("notes")
    mock_query.eq.assert_called_with("user_id", 1)


def test_supabase_adapter_requires_service_key_for_lists() -> None:
    config = SupabaseConfig(url="https://example.supabase.co", anon_key="anon")
    with patch("src.integrations.supabase_adapter.create_client", return_value=MagicMock()):
        adapter = SupabaseAdapter(config)
        with pytest.raises(SupabaseAdapterError):
            adapter.list_tables()
