from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Protocol, cast
import requests
from .supabase_adapter import SupabaseConfig


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


logger = logging.getLogger(__name__)


class GraphQLSupabaseError(Exception):
    pass


@dataclass(frozen=True)
class GraphQLCollectionPage:
    nodes: List[Dict[str, Any]]
    has_next: bool
    cursor: Optional[str]


class GraphQLSessionResponse(Protocol):
    status_code: int
    text: str

    def json(self) -> Dict[str, Any]: ...


class GraphQLSession(Protocol):
    def post(
        self, url: str, json: Dict[str, Any], headers: Dict[str, Any], timeout: float
    ) -> GraphQLSessionResponse: ...


class GraphQLSupabaseHelper:
    """Helper for paging Supabase GraphQL collections with the service-role key."""

    def __init__(
        self,
        config: SupabaseConfig,
        session: Optional[GraphQLSession] = None,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
    ) -> None:
        if not config.service_role_key:
            raise GraphQLSupabaseError("Service role key required for GraphQL helper")
        self.config = config
        self.session: GraphQLSession = session or cast(GraphQLSession, requests.Session())
        self.endpoint = f"{config.url.rstrip('/')}/graphql/v1"
        self.headers = {
            "apikey": config.service_role_key,
            "Authorization": f"Bearer {config.service_role_key}",
            "Content-Type": "application/json",
        }
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def _post(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"query": query, "variables": variables or {}}
        logger.debug("GraphQL request payload %s", payload)
        attempt = 0
        response: Optional[GraphQLSessionResponse] = None
        while attempt < self.max_retries:
            attempt += 1
            try:
                response = self.session.post(
                    self.endpoint, json=payload, headers=self.headers, timeout=15
                )
                if response.status_code == 200:
                    break
                logger.warning(
                    "GraphQL request returned %s on attempt %s: %s",
                    response.status_code,
                    attempt,
                    response.text,
                )
            except requests.RequestException as exc:
                logger.warning("GraphQL request failed on attempt %s: %s", attempt, exc)
                if attempt == self.max_retries:
                    raise GraphQLSupabaseError("GraphQL request failed") from exc
            time.sleep(self.backoff_factor * attempt)

        if response is None or response.status_code != 200:
            raise GraphQLSupabaseError("GraphQL request unexpected status")
        body = response.json()
        if errors := body.get("errors"):
            logger.warning("GraphQL errors: %s", errors)
            raise GraphQLSupabaseError(errors[0].get("message", "GraphQL error"))
        return body.get("data", {})  # type: ignore[no-any-return]

    def fetch_page(
        self,
        collection: str,
        node_fields: Iterable[str],
        first: int,
        after: Optional[str] = None,
    ) -> GraphQLCollectionPage:
        fields = "\n".join(f"        {field}" for field in node_fields)
        query = f"""
query CollectionPage($first: Int!, $after: String) {{
  {collection}(first: $first, after: $after) {{
    edges {{
      node {{
{fields}
      }}
    }}
    pageInfo {{
      hasNextPage
      endCursor
    }}
  }}
}}
"""
        data = self._post(query, {"first": first, "after": after})
        payload = data.get(collection)
        if payload is None:
            raise GraphQLSupabaseError(f"Collection {collection} missing in response")
        edges = payload.get("edges", [])
        nodes = [edge.get("node", {}) for edge in edges if edge.get("node")]
        page_info = payload.get("pageInfo", {})
        return GraphQLCollectionPage(
            nodes=nodes,
            has_next=bool(page_info.get("hasNextPage")),
            cursor=page_info.get("endCursor"),
        )

    def iterate_collection(
        self,
        collection: str,
        node_fields: Iterable[str],
        page_size: int = 50,
        max_pages: Optional[int] = None,
    ) -> Iterable[Dict[str, Any]]:
        fetched = 0
        after: Optional[str] = None
        page = 0
        while True:
            page += 1
            page_data = self.fetch_page(collection, node_fields, first=page_size, after=after)
            for node in page_data.nodes:
                yield node
                fetched += 1
            if not page_data.has_next:
                break
            if max_pages and page >= max_pages:
                break
            after = page_data.cursor
        logger.info("GraphQL fetched %s nodes from %s", fetched, collection)

    def collect_nodes(
        self,
        collection: str,
        node_fields: Iterable[str],
        page_size: int = 50,
        max_pages: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        return list(self.iterate_collection(collection, node_fields, page_size, max_pages))
