"""Tests for repository_traversal.py — coverage gap remediation.

Covers uncovered lines 158-193:
  - increment_salience (empty ids, happy path)
  - get_most_recent_entity (happy, sad/no result, evil/no properties)
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from claude_memory.repository_traversal import RepositoryTraversalMixin

# ─── Helpers ────────────────────────────────────────────────────────


def _make_mixin() -> RepositoryTraversalMixin:
    """Create a RepositoryTraversalMixin with a mocked select_graph."""
    mixin = RepositoryTraversalMixin()
    graph = MagicMock()
    graph.query = AsyncMock()
    mixin.select_graph = AsyncMock(return_value=graph)  # type: ignore[method-assign]
    return mixin


def _mock_result(rows: list[list]) -> MagicMock:
    """Build a mock FalkorDB query result."""
    result = MagicMock()
    result.result_set = rows
    return result


def _entity_node(**props: object) -> SimpleNamespace:
    """Create a mock FalkorDB node with properties."""
    return SimpleNamespace(properties=props)


# ═══════════════════════════════════════════════════════════════
#  increment_salience
# ═══════════════════════════════════════════════════════════════


class TestIncrementSalience:
    """3e/1s/1h for increment_salience."""

    @pytest.mark.asyncio()
    async def test_happy_increments_and_returns(self) -> None:
        """Happy: increments retrieval_count and returns updated scores."""
        m = _make_mixin()
        m.select_graph.return_value.query.return_value = _mock_result([["e1", 1.5, 1], ["e2", 2.0, 3]])

        result = await m.increment_salience(["e1", "e2"])
        assert len(result) == 2
        assert result[0]["id"] == "e1"
        assert result[0]["salience_score"] == 1.5
        assert result[1]["retrieval_count"] == 3

    @pytest.mark.asyncio()
    async def test_sad_empty_ids_returns_empty(self) -> None:
        """Sad: empty node_ids list returns [] without querying."""
        m = _make_mixin()

        result = await m.increment_salience([])
        assert result == []
        m.select_graph.return_value.query.assert_not_called()

    @pytest.mark.asyncio()
    async def test_evil_single_node(self) -> None:
        """Evil: single node incremented correctly."""
        m = _make_mixin()
        m.select_graph.return_value.query.return_value = _mock_result([["e1", 1.0, 1]])

        result = await m.increment_salience(["e1"])
        assert len(result) == 1

    @pytest.mark.asyncio()
    async def test_evil_node_not_found(self) -> None:
        """Evil: non-existent ID → empty result set, no crash."""
        m = _make_mixin()
        m.select_graph.return_value.query.return_value = _mock_result([])

        result = await m.increment_salience(["ghost-id"])
        assert result == []

    @pytest.mark.asyncio()
    async def test_evil_db_error_propagates(self) -> None:
        """Evil: database error is not swallowed (LOUD path)."""
        m = _make_mixin()
        m.select_graph.return_value.query.side_effect = ConnectionError("FalkorDB down")

        with pytest.raises(ConnectionError):
            await m.increment_salience(["e1"])


# ═══════════════════════════════════════════════════════════════
#  get_most_recent_entity
# ═══════════════════════════════════════════════════════════════


class TestGetMostRecentEntity:
    """3e/1s/1h for get_most_recent_entity."""

    @pytest.mark.asyncio()
    async def test_happy_returns_entity(self) -> None:
        """Happy: returns the most recently created entity."""
        m = _make_mixin()
        node = _entity_node(id="e1", name="Latest", project_id="proj-1")
        m.select_graph.return_value.query.return_value = _mock_result([[node]])

        result = await m.get_most_recent_entity("proj-1")
        assert result is not None
        assert result["id"] == "e1"

    @pytest.mark.asyncio()
    async def test_sad_no_entities(self) -> None:
        """Sad: no entities in project returns None."""
        m = _make_mixin()
        m.select_graph.return_value.query.return_value = _mock_result([])

        result = await m.get_most_recent_entity("empty-project")
        assert result is None

    @pytest.mark.asyncio()
    async def test_evil_node_without_properties_attr(self) -> None:
        """Evil: node without 'properties' attr returns None."""
        m = _make_mixin()
        # A raw dict instead of a node with .properties
        m.select_graph.return_value.query.return_value = _mock_result([[{"id": "e1"}]])

        result = await m.get_most_recent_entity("proj-1")
        assert result is None

    @pytest.mark.asyncio()
    async def test_evil_db_error_propagates(self) -> None:
        """Evil: DB error is not swallowed."""
        m = _make_mixin()
        m.select_graph.return_value.query.side_effect = RuntimeError("query failed")

        with pytest.raises(RuntimeError):
            await m.get_most_recent_entity("proj-1")

    @pytest.mark.asyncio()
    async def test_evil_properties_returned_as_dict(self) -> None:
        """Evil: properties are returned as a plain dict, not SimpleNamespace."""
        m = _make_mixin()
        node = _entity_node(id="e1", name="Test")
        m.select_graph.return_value.query.return_value = _mock_result([[node]])

        result = await m.get_most_recent_entity("proj-1")
        assert isinstance(result, dict)
