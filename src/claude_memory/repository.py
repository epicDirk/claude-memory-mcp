"""FalkorDB data access layer — Cypher queries, node/edge CRUD, and index management."""

import asyncio
import logging
import os
from typing import Any

from claude_memory.repository_queries import RepositoryQueryMixin
from claude_memory.repository_traversal import RepositoryTraversalMixin
from claude_memory.retry import retry_on_transient

logger = logging.getLogger(__name__)

_CONSTRUCTOR_MAX_RETRIES = 3
_CONSTRUCTOR_BASE_DELAY = 1.0


class MemoryRepository(RepositoryQueryMixin, RepositoryTraversalMixin):
    """
    Data Access Layer for FalkorDB.
    Handles all direct database interactions, Cypher queries, and Index management.

    Uses lazy async initialization — the connection is established on first use,
    not in the constructor, to avoid blocking the event loop.
    """

    def __init__(
        self, host: str | None = None, port: int | None = None, password: str | None = None
    ) -> None:
        """Store connection params. Connection is established lazily on first use."""
        self.host = host or os.getenv("FALKORDB_HOST", "127.0.0.1")
        self.port = port or int(os.getenv("FALKORDB_PORT", "6379"))
        self.password = password or os.getenv("FALKORDB_PASSWORD")

        self._client: Any = None
        self.graph_name = "claude_memory"

    async def _ensure_connected(self) -> Any:
        """Lazy async connection with retry. Returns the FalkorDB client."""
        if self._client is not None:
            return self._client

        from falkordb.asyncio import FalkorDB  # noqa: PLC0415

        for attempt in range(_CONSTRUCTOR_MAX_RETRIES):
            try:
                self._client = FalkorDB(
                    host=self.host,
                    port=self.port,
                    password=self.password,
                )
                return self._client
            except (ConnectionError, TimeoutError, OSError) as exc:
                if attempt == _CONSTRUCTOR_MAX_RETRIES - 1:
                    logger.error(
                        "FalkorDB connection failed after %d attempts: %s",
                        _CONSTRUCTOR_MAX_RETRIES,
                        exc,
                    )
                    raise
                delay = _CONSTRUCTOR_BASE_DELAY * (2**attempt)
                logger.warning(
                    "FalkorDB connect retry %d/%d in %.1fs — %s",
                    attempt + 1,
                    _CONSTRUCTOR_MAX_RETRIES,
                    delay,
                    exc,
                )
                await asyncio.sleep(delay)
        raise ConnectionError("FalkorDB connection exhausted retries")  # pragma: no cover

    @retry_on_transient()
    async def select_graph(self) -> Any:
        """Return the active FalkorDB graph handle."""
        client = await self._ensure_connected()
        return client.select_graph(self.graph_name)

    def ensure_indices(self) -> None:
        """Create necessary indices if they don't exist."""
        pass

    @retry_on_transient()
    async def create_node(self, label: str, properties: dict[str, Any]) -> dict[str, Any]:
        """Creates a node (embedding logic moved to VectorStore)."""
        graph = await self.select_graph()
        props = properties.copy()

        params: dict[str, Any] = {"props": props}
        params["name"] = props.get("name")
        params["project_id"] = props.get("project_id")
        params["updated_at"] = props.get("updated_at")

        query = f"""
        MERGE (n:{label}:Entity {{name: $name, project_id: $project_id}})
        ON CREATE SET n = $props
        ON MATCH SET n.updated_at = $updated_at
        RETURN n
        """

        result = await graph.query(query, params)
        return result.result_set[0][0].properties  # type: ignore[no-any-return]

    @retry_on_transient()
    async def get_node(self, node_id: str) -> dict[str, Any] | None:
        """Retrieves a node by its ID."""
        graph = await self.select_graph()
        query = "MATCH (n) WHERE n.id = $id RETURN n"
        result = await graph.query(query, {"id": node_id})

        if not result.result_set:
            return None

        return result.result_set[0][0].properties  # type: ignore[no-any-return]

    @retry_on_transient()
    async def update_node(self, node_id: str, properties: dict[str, Any]) -> dict[str, Any]:
        """Updates a node's properties."""
        graph = await self.select_graph()
        props = properties.copy()

        query_parts = []
        query_parts.append("MATCH (n:Entity {id: $id})")
        query_parts.append("SET n += $props")
        query_parts.append("RETURN n")

        query = "\n".join(query_parts)
        params = {"id": node_id, "props": props}

        result = await graph.query(query, params)
        if not result.result_set:
            return {}
        return result.result_set[0][0].properties  # type: ignore[no-any-return]

    async def delete_node(
        self, node_id: str, soft_delete: bool = False, reason: str | None = None
    ) -> bool:
        """Deletes a node (hard or soft)."""
        graph = await self.select_graph()

        if soft_delete:
            query = (
                "MATCH (n) WHERE n.id = $id SET n.deleted = true, "
                "n.deletion_reason = $reason RETURN n"
            )
            res = await graph.query(query, {"id": node_id, "reason": reason})
            return bool(res.result_set)
        else:
            query = "MATCH (n) WHERE n.id = $id DETACH DELETE n"
            await graph.query(query, {"id": node_id})
            return True

    async def create_edge(
        self, from_id: str, to_id: str, relation_type: str, properties: dict[str, Any]
    ) -> dict[str, Any]:
        """Creates a relationship between two nodes."""
        graph = await self.select_graph()

        query = f"""
        MATCH (a), (b)
        WHERE a.id = $from AND b.id = $to
        CREATE (a)-[r:{relation_type}]->(b)
        SET r = $props
        RETURN r
        """
        result = await graph.query(query, {"from": from_id, "to": to_id, "props": properties})
        if not result.result_set:
            return {}
        return result.result_set[0][0].properties  # type: ignore[no-any-return]

    async def delete_edge(self, edge_id: str) -> bool:
        """Deletes a relationship by ID."""
        graph = await self.select_graph()
        query = "MATCH ()-[r]->() WHERE r.id = $id DELETE r"
        await graph.query(query, {"id": edge_id})
        return True

    @retry_on_transient()
    async def execute_cypher(self, query: str, params: dict[str, Any] | None = None) -> Any:
        """Executes a raw Cypher query."""
        graph = await self.select_graph()
        return await graph.query(query, params or {})
