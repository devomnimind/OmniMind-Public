from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Set
from ..integrations.graphql_supabase import ( from ..integrations.supabase_adapter import SupabaseConfig
    from ..memory import EpisodicMemory


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



    GraphQLCollectionPage,
    GraphQLSupabaseError,
    GraphQLSupabaseHelper,
)

if TYPE_CHECKING:
else:
    EpisodicMemory = Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MemoryOnboardingReport:
    nodes_processed: int
    nodes_loaded: int
    errors: List[str]
    last_cursor: Optional[str]


class SupabaseMemoryOnboarding:
    """Seeds episodic memory using Supabase GraphQL collections."""

    def __init__(
        self,
        config: SupabaseConfig,
        memory: EpisodicMemory,
        helper: Optional[GraphQLSupabaseHelper] = None,
    ) -> None:
        self.config = config
        self.memory = memory
        self.helper = helper or GraphQLSupabaseHelper(config)
        self._seen_ids: Set[str] = set()

    def seed_collection(
        self,
        collection: str = "memory_consolidationsCollection",
        node_fields: Optional[Iterable[str]] = None,
        page_size: int = 25,
        max_pages: Optional[int] = None,
    ) -> MemoryOnboardingReport:
        fields = list(node_fields or ["id", "content", "created_at", "metadata"])
        processed = 0
        stored = 0
        last_cursor: Optional[str] = None
        errors: List[str] = []
        after: Optional[str] = None
        page = 0

        while True:
            page += 1
            try:
                page_data: GraphQLCollectionPage = self.helper.fetch_page(
                    collection, fields, first=page_size, after=after
                )
            except GraphQLSupabaseError as exc:
                errors.append(str(exc))
                break

            for node in page_data.nodes:
                processed += 1
                stored += int(self._store_node(node))
                last_cursor = page_data.cursor

            if not page_data.has_next:
                break
            if max_pages and page >= max_pages:
                break
            after = page_data.cursor

        return MemoryOnboardingReport(
            nodes_processed=processed,
            nodes_loaded=stored,
            errors=errors,
            last_cursor=last_cursor,
        )

    def _store_node(self, node: Dict[str, Any]) -> bool:
        node_id = str(node.get("id")) if node.get("id") is not None else None
        if node_id and node_id in self._seen_ids:
            return False
        if node_id:
            self._seen_ids.add(node_id)

        metadata = node.get("metadata") or {}
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except json.JSONDecodeError:
                metadata = {"raw": metadata}

        content = node.get("content") or node.get("payload") or ""
        if not content:
            return False

        task = metadata.get("task", "supabase_memory_onboarding")
        action = metadata.get("action", "memory_import")
        reward_value = metadata.get("reward")
        reward = float(reward_value) if reward_value is not None else 0.0

        payload: Dict[str, Any] = {
            "memory_id": node_id,
            "created_at": node.get("created_at"),
            "source": "supabase_memory_consolidation",
        }
        payload.update({k: v for k, v in metadata.items() if k not in payload})

        try:
            self.memory.store_episode(
                task=task,
                action=action,
                result=content,
                reward=reward,
                metadata=payload,
            )
            return True
        except Exception as exc:
            logger.warning("Failed to store onboarding node %s: %s", node_id, exc)
            return False
