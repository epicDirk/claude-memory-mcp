"""Tests for MemoryRepository (repository.py).

Covers all uncovered lines: ensure_indices, create_node, get_node (null case),
update_node (empty result), delete_node (soft/hard), create_edge (empty result),
delete_edge, execute_cypher, get_subgraph (depth>0 paths), get_all_nodes,
get_total_node_count.
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ─── Test Constants ─────────────────────────────────────────────────

NODE_ID = "node-001"
NODE_LABEL = "Concept"
NODE_NAME = "TestEntity"
PROJECT_ID = "project-alpha"
UPDATE_PROPS = {"version": "2.0"}
DELETE_REASON = "deprecated"

EDGE_FROM_ID = "node-001"
EDGE_TO_ID = "node-002"
EDGE_TYPE = "RELATED_TO"
EDGE_ID = "edge-001"
EDGE_PROPS: dict[str, Any] = {"confidence": 0.95}

CYPHER_QUERY = "MATCH (n) RETURN n"
CYPHER_PARAMS: dict[str, Any] = {"id": NODE_ID}

GRAPH_NAME = "claude_memory"
SUBGRAPH_DEPTH = 2
SUBGRAPH_IDS = ["node-001", "node-002"]
ALL_NODES_LIMIT = 1000


# ─── Mock Helpers ───────────────────────────────────────────────────


def _make_mock_node(properties: dict[str, Any]) -> MagicMock:
    """Creates a mock FalkorDB node with the given properties."""
    node = MagicMock()
    node.properties = properties
    node.labels = [NODE_LABEL, "Entity"]
    return node


def _make_mock_edge(properties: dict[str, Any]) -> MagicMock:
    """Creates a mock FalkorDB edge with the given properties."""
    edge = MagicMock()
    edge.properties = properties
    return edge


def _make_mock_result(rows: list[list[Any]]) -> MagicMock:
    """Creates a mock FalkorDB query result."""
    result = MagicMock()
    result.result_set = rows
    return result


# ─── Module Import ──────────────────────────────────────────────────


@pytest.fixture()
def mock_graph() -> MagicMock:
    g = MagicMock()
    g.query = AsyncMock()
    return g


@pytest.fixture()
def repo(mock_graph: MagicMock) -> Any:
    from claude_memory.repository import MemoryRepository

    r = MemoryRepository()
    # Bypass lazy async connection — inject the graph directly
    r._client = MagicMock()
    r._client.select_graph.return_value = mock_graph
    return r


# ─── ensure_indices Tests ───────────────────────────────────────────


def test_ensure_indices_is_noop(repo: Any) -> None:
    """ensure_indices is currently a no-op pass statement."""
    repo.ensure_indices()  # Should not raise


# ─── create_node Tests ──────────────────────────────────────────────


async def test_create_node(repo: Any, mock_graph: MagicMock) -> None:
    node_props = {
        "name": NODE_NAME,
        "project_id": PROJECT_ID,
        "updated_at": "2024-01-01T00:00:00Z",
    }
    mock_node = _make_mock_node(node_props)
    mock_graph.query.return_value = _make_mock_result([[mock_node]])

    result = await repo.create_node(NODE_LABEL, node_props)
    assert result == node_props
    mock_graph.query.assert_called_once()


# ─── get_node Tests ─────────────────────────────────────────────────


async def test_get_node_found(repo: Any, mock_graph: MagicMock) -> None:
    node_props = {"id": NODE_ID, "name": NODE_NAME}
    mock_node = _make_mock_node(node_props)
    mock_graph.query.return_value = _make_mock_result([[mock_node]])

    result = await repo.get_node(NODE_ID)
    assert result == node_props


async def test_get_node_not_found(repo: Any, mock_graph: MagicMock) -> None:
    mock_graph.query.return_value = _make_mock_result([])

    result = await repo.get_node(NODE_ID)
    assert result is None


# ─── update_node Tests ──────────────────────────────────────────────


async def test_update_node_success(repo: Any, mock_graph: MagicMock) -> None:
    updated_props = {"id": NODE_ID, **UPDATE_PROPS}
    mock_node = _make_mock_node(updated_props)
    mock_graph.query.return_value = _make_mock_result([[mock_node]])

    result = await repo.update_node(NODE_ID, UPDATE_PROPS)
    assert result == updated_props


async def test_update_node_not_found(repo: Any, mock_graph: MagicMock) -> None:
    mock_graph.query.return_value = _make_mock_result([])

    result = await repo.update_node(NODE_ID, UPDATE_PROPS)
    assert result == {}


# ─── delete_node Tests ──────────────────────────────────────────────


async def test_delete_node_hard(repo: Any, mock_graph: MagicMock) -> None:
    result = await repo.delete_node(NODE_ID)
    assert result is True
    mock_graph.query.assert_called_once()


async def test_delete_node_soft(repo: Any, mock_graph: MagicMock) -> None:
    mock_node = _make_mock_node({"id": NODE_ID, "deleted": True})
    mock_graph.query.return_value = _make_mock_result([[mock_node]])

    result = await repo.delete_node(NODE_ID, soft_delete=True, reason=DELETE_REASON)
    assert result is True


async def test_delete_node_soft_not_found(repo: Any, mock_graph: MagicMock) -> None:
    mock_graph.query.return_value = _make_mock_result([])

    result = await repo.delete_node(NODE_ID, soft_delete=True, reason=DELETE_REASON)
    assert result is False


# ─── create_edge Tests ──────────────────────────────────────────────


async def test_create_edge_success(repo: Any, mock_graph: MagicMock) -> None:
    mock_edge = _make_mock_edge(EDGE_PROPS)
    mock_graph.query.return_value = _make_mock_result([[mock_edge]])

    result = await repo.create_edge(EDGE_FROM_ID, EDGE_TO_ID, EDGE_TYPE, EDGE_PROPS)
    assert result == EDGE_PROPS


async def test_create_edge_nodes_not_found(repo: Any, mock_graph: MagicMock) -> None:
    mock_graph.query.return_value = _make_mock_result([])

    result = await repo.create_edge(EDGE_FROM_ID, EDGE_TO_ID, EDGE_TYPE, EDGE_PROPS)
    assert result == {}


# ─── delete_edge Tests ──────────────────────────────────────────────


async def test_delete_edge(repo: Any, mock_graph: MagicMock) -> None:
    result = await repo.delete_edge(EDGE_ID)
    assert result is True
    mock_graph.query.assert_called_once()


# ─── execute_cypher Tests ───────────────────────────────────────────


async def test_execute_cypher_with_params(repo: Any, mock_graph: MagicMock) -> None:
    expected = _make_mock_result([["result"]])
    mock_graph.query.return_value = expected

    result = await repo.execute_cypher(CYPHER_QUERY, CYPHER_PARAMS)
    assert result is expected
    mock_graph.query.assert_called_once_with(CYPHER_QUERY, CYPHER_PARAMS)


async def test_execute_cypher_without_params(repo: Any, mock_graph: MagicMock) -> None:
    expected = _make_mock_result([["result"]])
    mock_graph.query.return_value = expected

    result = await repo.execute_cypher(CYPHER_QUERY)
    assert result is expected
    mock_graph.query.assert_called_once_with(CYPHER_QUERY, {})


# ─── get_subgraph Tests ────────────────────────────────────────────


async def test_get_subgraph_empty_ids(repo: Any) -> None:
    result = await repo.get_subgraph([])
    assert result == {"nodes": [], "edges": []}


async def test_get_subgraph_depth_zero(repo: Any, mock_graph: MagicMock) -> None:
    """depth=0 uses the simpler MATCH query without UNWIND."""
    node_data = [
        {"id": NODE_ID, "properties": {"id": NODE_ID, "name": NODE_NAME}},
    ]
    mock_graph.query.return_value = _make_mock_result([[node_data]])

    result = await repo.get_subgraph([NODE_ID], depth=0)
    assert len(result["nodes"]) == 1
    assert result["edges"] == []
    assert result["nodes"][0]["id"] == NODE_ID


async def test_get_subgraph_depth_zero_empty(repo: Any, mock_graph: MagicMock) -> None:
    mock_graph.query.return_value = _make_mock_result([])

    result = await repo.get_subgraph([NODE_ID], depth=0)
    assert result == {"nodes": [], "edges": []}


async def test_get_subgraph_with_depth(repo: Any, mock_graph: MagicMock) -> None:
    """depth>0 uses UNWIND on relationships, returns deduplicated nodes/edges."""
    edge_data = [
        {"id": EDGE_ID, "source": EDGE_FROM_ID, "target": EDGE_TO_ID, "type": EDGE_TYPE},
    ]
    node_data = [
        {"id": EDGE_FROM_ID, "properties": {"id": EDGE_FROM_ID, "name": "NodeA"}},
        {"id": EDGE_TO_ID, "properties": {"id": EDGE_TO_ID, "name": "NodeB"}},
    ]
    mock_graph.query.return_value = _make_mock_result([[edge_data, node_data]])

    result = await repo.get_subgraph(SUBGRAPH_IDS, depth=SUBGRAPH_DEPTH)
    assert len(result["nodes"]) == 2
    assert len(result["edges"]) == 1


async def test_get_subgraph_with_depth_empty_result(repo: Any, mock_graph: MagicMock) -> None:
    """When depth>0 UNWIND returns empty, fallback to isolated node query."""
    # First call (UNWIND query) returns empty
    # Second call (fallback node query) returns nodes
    node_data = [
        {"id": NODE_ID, "properties": {"id": NODE_ID, "name": NODE_NAME}},
    ]
    mock_graph.query.side_effect = [
        _make_mock_result([]),  # UNWIND query empty
        _make_mock_result([[node_data]]),  # fallback query
    ]

    result = await repo.get_subgraph([NODE_ID], depth=SUBGRAPH_DEPTH)
    assert len(result["nodes"]) == 1


async def test_get_subgraph_with_depth_completely_empty(repo: Any, mock_graph: MagicMock) -> None:
    """Both UNWIND and fallback queries return empty."""
    mock_graph.query.side_effect = [
        _make_mock_result([]),  # UNWIND query empty
        _make_mock_result([]),  # fallback also empty
    ]

    result = await repo.get_subgraph([NODE_ID], depth=SUBGRAPH_DEPTH)
    assert result == {"nodes": [], "edges": []}


# ─── get_all_nodes Tests ───────────────────────────────────────────


async def test_get_all_nodes(repo: Any, mock_graph: MagicMock) -> None:
    node_props = {"id": NODE_ID, "name": NODE_NAME, "embedding": MOCK_VECTOR}
    mock_node = _make_mock_node(node_props)
    mock_graph.query.return_value = _make_mock_result([[mock_node]])

    result = await repo.get_all_nodes(limit=ALL_NODES_LIMIT)
    assert len(result) == 1
    assert result[0]["id"] == NODE_ID


# ─── get_total_node_count Tests ─────────────────────────────────────


MOCK_VECTOR = [0.1, 0.2, 0.3]


async def test_get_total_node_count(repo: Any, mock_graph: MagicMock) -> None:
    mock_graph.query.return_value = _make_mock_result([[42]])

    result = await repo.get_total_node_count()
    assert result == 42


async def test_get_total_node_count_empty(repo: Any, mock_graph: MagicMock) -> None:
    mock_graph.query.return_value = _make_mock_result([])

    result = await repo.get_total_node_count()
    assert result == 0
