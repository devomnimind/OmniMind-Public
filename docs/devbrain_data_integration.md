# DevBrain Data Integration

This document describes how the OmniMind DevBrain now connects securely to Supabase (PostgreSQL) and Qdrant (vector store) through the Model Context Protocol (MCP).

## Supabase Integration

### Credential Loading

1. **Primary source:** export `OMNIMIND_SUPABASE_URL`, `OMNIMIND_SUPABASE_ANON_KEY`, and optionally `OMNIMIND_SUPABASE_SERVICE_ROLE_KEY` / `OMNIMIND_SUPABASE_PROJECT` in your shell, systemd unit, or secrets manager before launching OmniMind. Never store plaintext credentials inside the repository.
2. **MCP assist:** when running through MCP, provide these environment variables via the MCP runtime so `SupabaseConfig.load()` can read them directly without touching the filesystem.

### Adapter Features

- `SupabaseAdapter.query_table(...)` performs filtered selects with pagination.
- `insert_record`, `update_record`, and `delete_records` wrap the Supabase REST API with consistent error handling and logging.
- `describe_table` and `list_tables` rely on the **service role key** to inspect `information_schema` metadata—these methods will raise a `SupabaseAdapterError` if the key is missing or insufficient.
- Operations are logged via `logger.info` and can be integrated with the observability pipeline for dashboards or alerts.
### How Agents Use It

`OrchestratorAgent` loads the `SupabaseAdapter` at startup using MCP, and exposes service status through `dashboard_snapshot` (field `supabase_tables` when the service key exists). Agents can invoke the adapter directly for data enrichment or for bridging new orchestration tasks with Supabase data.

### Real Supabase Metadata (service role key)

- The service role credential must be supplied via `OMNIMIND_SUPABASE_SERVICE_ROLE_KEY`. When that variable is present, `SupabaseConfig.load()` automatically unlocks schema inspection features.
- Using that role key we introspected the GraphQL API at `/graphql/v1` and found the following accessible collections: `backup_metadata`, `evolution_history`, and `memory_consolidations`.
- Each collection uses the Relay-style connection pattern (`<table>Collection`) and returns nodes such as `{ id, content, created_at, metadata }`, so agents can page through records with `first`, `after`, etc.
- A sample GraphQL payload to fetch the latest two memory consolidations looks like:

```graphql
query MemorySample {
	memory_consolidationsCollection(first: 2) {
		edges {
			node {
				id
				content
				created_at
				metadata
			}
		}
	}
}
```

- Despite the GraphQL schema being reachable, the current tables are empty (`edges` came back empty in a live sample), so the adapter can operate without risking data leakage.

### GraphQL pagination helper

- The new `GraphQLSupabaseHelper` builds Relay-style `Collection` queries, paginates with backoff, and logs both successful and failed requests. It requires the service role credential so it can access `memory_consolidations`, `evolution_history`, or any other collection exposed via GraphQL.
- Helpers are instantiated with `SupabaseConfig.load()` and include retry/backoff knobs to survive transient network issues; inject `requests.Session` mocks during unit testing.

### Memory onboarding

- Agents now run `SupabaseMemoryOnboarding` during startup (`ReactAgent` seeds it after creating `EpisodicMemory`), so live Supabase `memory_consolidations` entries pre-populate the Qdrant store. The onboarding namespace handles duplicate IDs, metadata parsing, and audit-friendly logging.
- To trigger onboarding manually, ensure `OMNIMIND_SUPABASE_SERVICE_ROLE_KEY` is available in the environment. The onboarding report includes `nodes_processed`, `nodes_loaded`, and any GraphQL errors encountered; monitor the logs to confirm success before relying on the imported experiences.

## Qdrant Integration

### Installation Instructions

Run Qdrant locally (container or binary). For example:

```bash
docker run --rm -p 6333:6333 qdrant/qdrant:v1.7.3
```

Or install locally via:

```bash
pip install qdrant-client
qdrant-cli start
```

Ensure the service is reachable at `OMNIMIND_QDRANT_URL` (e.g., `http://127.0.0.1:6333`) and set `OMNIMIND_QDRANT_API_KEY` if you enable authentication.

### Adapter Features

- `QdrantAdapter.ensure_collection` creates the collection when missing and enforces vector size + distance.
- `upsert_vectors` bundles vectors/payloads into `PointStruct` objects and handles logging of the inserted count.
- `search_vectors` returns hits with payload metadata for semantic recall scenarios.
- `list_collections` and `delete_vectors` are used by the orchestrator and diagnostic tools to audit the vector store state.

### MCP & Credential Handling

`QdrantConfig.load()` reads `OMNIMIND_QDRANT_*` variables supplied by the host shell or MCP runtime; no plaintext credential files are required.

## Testing & Monitoring

- Run targeted unit tests:

```bash
pytest tests/test_supabase_adapter.py tests/test_qdrant_adapter.py
```

- Observability dashboards (`/observability`) now report `supabase_tables` and `qdrant_collections` when the integrations are available.
- Audit-critical actions (Supabase schema reads, Qdrant upserts) are logged through the main `logger` and can be wiretapped by the existing audit chain.

## Operational Controls

1. **Secure credentials:** Never expose keys in shared repos. Use `direnv`, `systemd`, or `vault` to inject `OMNIMIND_SUPABASE_*` and `OMNIMIND_QDRANT_*` before starting the agents.
2. **Monitoring:** Hook the `dashboard_snapshot` fields to your alerting cadence; missing `supabase_tables` or failing `qdrant_collections` indicates credential issues.
3. **Audit trails:** MCP automatically records file reads/writes; Supabase/Qdrant adapters log operations so you can expand the audit hash chain when required.
4. **Simulated loads:** Use the provided tests (above) to exercise adapters with mocks and ensure new data workflows do not regress.

By following these patterns, DevBrain maintains a traceable and secure data layer bridging Supabase analytics with Qdrant-powered memory recall.
