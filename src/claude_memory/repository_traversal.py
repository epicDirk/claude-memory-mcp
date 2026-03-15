"""Mixin for graph traversal and analytics queries."""

import logging
from typing import Any

from claude_memory.retry import retry_on_transient

logger = logging.getLogger(__name__)


class RepositoryTraversalMixin:
    """Methods for traversing the graph and retrieving aggregate data."""

    async def select_graph(self) -> Any:
        """Protocol method to be implemented by the main Repository class."""
        raise NotImplementedError

    @retry_on_transient()
    async def get_subgraph(self, start_node_ids: list[str], depth: int = 1) -> dict[str, Any]:
        """Retrieves a subgraph of connected nodes up to 'depth' hops from start nodes."""
        if not start_node_ids:
            return {"nodes": [], "edges": []}

        graph = await self.select_graph()

        # Optimization: If depth is 0, just fetch nodes directly (Fixes UNWIND bug on empty paths)
        if depth == 0:
            query_nodes = """
            MATCH (n:Entity) WHERE n.id IN $ids
            RETURN collect(distinct {
                id: n.id,
                labels: labels(n),
                properties: properties(n)
            }) as nodes
            """
            res_nodes = await graph.query(query_nodes, {"ids": start_node_ids})
            if res_nodes.result_set:
                return {
                    "nodes": [n["properties"] for n in res_nodes.result_set[0][0]],
                    "edges": [],
                }
            return {"nodes": [], "edges": []}

        query = f"""
        MATCH path = (root:Entity)-[*0..{depth}]-(neighbor)
        WHERE root.id IN $ids
        UNWIND relationships(path) as r
        WITH distinct r, startNode(r) as s, endNode(r) as e
        RETURN collect(distinct {{
            id: r.id,
            source: s.id,
            target: e.id,
            type: type(r),
            properties: properties(r)
        }}) as edges,
        collect(distinct {{
            id: s.id,
            labels: labels(s),
            properties: properties(s)
        }}) + collect(distinct {{
            id: e.id,
            labels: labels(e),
            properties: properties(e)
        }}) as nodes
        """

        result = await graph.query(query, {"ids": start_node_ids})

        if not result.result_set:
            query_nodes = """
             MATCH (n:Entity) WHERE n.id IN $ids
             RETURN collect(distinct {
                id: n.id,
                labels: labels(n),
                properties: properties(n)
             }) as nodes
             """
            res_nodes = await graph.query(query_nodes, {"ids": start_node_ids})
            if res_nodes.result_set:
                return {
                    "nodes": [n["properties"] for n in res_nodes.result_set[0][0]],
                    "edges": [],
                }
            return {"nodes": [], "edges": []}

        row = result.result_set[0]
        edges_data = row[0]
        nodes_data = row[1]

        unique_nodes = {n["id"]: n["properties"] for n in nodes_data}
        unique_edges = {e["id"]: e for e in edges_data}

        return {"nodes": list(unique_nodes.values()), "edges": list(unique_edges.values())}

    async def get_all_nodes(self, limit: int = 1000) -> list[dict[str, Any]]:
        """Retrieves all entity nodes for clustering."""
        graph = await self.select_graph()
        query = """
        MATCH (n:Entity)
        RETURN n
        LIMIT $limit
        """
        result = await graph.query(query, {"limit": limit})
        return [row[0].properties for row in result.result_set]

    async def get_total_node_count(self) -> int:
        """Returns the total number of nodes in the graph (for receipts)."""
        graph = await self.select_graph()
        query = "MATCH (n) RETURN count(n)"
        result = await graph.query(query)
        if not result.result_set:
            return 0
        return int(result.result_set[0][0])

    @retry_on_transient()
    async def increment_salience(self, node_ids: list[str]) -> list[dict[str, Any]]:
        """Atomically increment retrieval_count and recalculate salience_score for nodes.

        Formula: salience_score = 1.0 + log2(1 + retrieval_count)
        Uses log(x)/log(2) since FalkorDB doesn't support log2().
        This gives diminishing returns — early retrievals boost salience fast.
        """
        if not node_ids:
            return []
        graph = await self.select_graph()
        query = """
        MATCH (n:Entity)
        WHERE n.id IN $ids
        SET n.retrieval_count = COALESCE(n.retrieval_count, 0) + 1,
            n.salience_score = 1.0 + log(1 + COALESCE(n.retrieval_count, 0) + 1) / log(2)
        RETURN n.id AS id, n.salience_score AS salience_score, n.retrieval_count AS retrieval_count
        """
        result = await graph.query(query, {"ids": node_ids})
        return [
            {
                "id": row[0],
                "salience_score": row[1],
                "retrieval_count": row[2],
            }
            for row in result.result_set
        ]

    @retry_on_transient()
    async def get_most_recent_entity(self, project_id: str) -> dict[str, Any] | None:
        """Return the most recently created entity in a project (for PRECEDED_BY linking)."""
        graph = await self.select_graph()
        query = """
        MATCH (n:Entity {project_id: $pid})
        RETURN n
        ORDER BY COALESCE(n.occurred_at, n.created_at) DESC
        LIMIT 1
        """
        result = await graph.query(query, {"pid": project_id})
        if not result.result_set:
            return None
        node = result.result_set[0][0]
        return dict(node.properties) if hasattr(node, "properties") else None
