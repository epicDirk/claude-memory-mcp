from unittest.mock import AsyncMock, MagicMock

import pytest


MOCK_EMBEDDING = [0.1] * 384


# ── Mock Classes ──────────────────────────────────────────────────────


class MockVectorStore:
    def __init__(self) -> None:
        self.upsert = AsyncMock()
        self.search = AsyncMock(return_value=[])
        self.delete = AsyncMock()


class MockRepository:
    """Mock for MemoryRepository — all methods are now async."""

    def __init__(self) -> None:
        self.create_node = AsyncMock(return_value={"id": "test-id", "name": "Test"})
        self.get_node = AsyncMock(return_value=None)
        self.update_node = AsyncMock(return_value={"id": "test-id", "name": "Test"})
        self.delete_node = AsyncMock(return_value=True)
        self.create_edge = AsyncMock(return_value={"id": "edge-id"})
        self.delete_edge = AsyncMock(return_value=True)
        self.execute_cypher = AsyncMock(return_value=MagicMock(result_set=[]))
        # repository_queries
        self.query_timeline = AsyncMock(return_value=[])
        self.get_temporal_neighbors = AsyncMock(return_value=[])
        self.create_temporal_edge = AsyncMock()
        self.get_bottles = AsyncMock(return_value=[])
        self.get_graph_health = AsyncMock(return_value={})
        self.list_orphans = AsyncMock(return_value=[])
        self.get_all_edges = AsyncMock(return_value=[])
        self.get_all_node_ids = AsyncMock(return_value=[])
        # repository_traversal
        self.get_subgraph = AsyncMock(return_value={"nodes": [], "edges": []})
        self.get_all_nodes = AsyncMock(return_value=[])
        self.get_total_node_count = AsyncMock(return_value=0)
        self.increment_salience = AsyncMock(return_value=[])
        self.get_most_recent_entity = AsyncMock(return_value=None)
        self.select_graph = AsyncMock()


class MockEmbedder:
    """Mock for Embedder — async_encode is async, encode stays sync."""

    def __init__(self) -> None:
        self.encode = MagicMock(return_value=MOCK_EMBEDDING)
        self.async_encode = AsyncMock(return_value=MOCK_EMBEDDING)


class MockLock:
    """Mock for ProjectLock — supports async context manager."""

    def __init__(self) -> None:
        self.acquire = MagicMock(return_value=True)
        self.release = MagicMock()
        self.async_acquire = AsyncMock(return_value=True)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class MockLockManager:
    """Mock for LockManager — lock() returns a MockLock."""

    def __init__(self) -> None:
        self._lock = MockLock()
        self.lock = MagicMock(return_value=self._lock)
        self.async_acquire = AsyncMock(return_value=True)
        self.async_release = AsyncMock()


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def mock_vector_store() -> MockVectorStore:
    return MockVectorStore()


@pytest.fixture
def mock_repo() -> MockRepository:
    return MockRepository()


@pytest.fixture
def mock_embedder() -> MockEmbedder:
    return MockEmbedder()


@pytest.fixture
def mock_lock_manager() -> MockLockManager:
    return MockLockManager()
