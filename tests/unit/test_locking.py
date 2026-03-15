import time
from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from claude_memory.lock_manager import LockManager
from claude_memory.tools import EntityCreateParams, EntityUpdateParams, MemoryService


@pytest.fixture
def mock_redis() -> Generator[MagicMock, None, None]:
    with patch("claude_memory.lock_manager.redis.Redis") as mock_redis_cls:
        mock_client = mock_redis_cls.return_value
        # Default behavior: Access granted
        mock_client.set.return_value = True
        yield mock_client


class TestLockManager:
    def test_acquire_success(self, mock_redis: MagicMock) -> None:
        manager = LockManager()
        assert manager.acquire("p1") is True
        mock_redis.set.assert_called()

    def test_acquire_failure(self, mock_redis: MagicMock) -> None:
        manager = LockManager()
        # Simulate lock held (set returns False)
        mock_redis.set.return_value = False

        # Should return False after timeout (using short timeout for test)
        start = time.time()
        assert manager.acquire("p1", timeout=0.1) is False
        duration = time.time() - start
        assert duration >= 0.1

    def test_release(self, mock_redis: MagicMock) -> None:
        manager = LockManager()
        manager.release("p1")
        mock_redis.delete.assert_called_with("lock:project:p1")

    def test_context_manager(self, mock_redis: MagicMock) -> None:
        manager = LockManager()
        with manager.lock("p1"):
            pass
        mock_redis.set.assert_called()
        mock_redis.delete.assert_called()


@pytest.fixture
def mock_service_with_lock(mock_redis: MagicMock) -> Generator[MemoryService, None, None]:
    with (
        patch("claude_memory.embedding.EmbeddingService"),
        patch("falkordb.asyncio.FalkorDB"),
        patch("claude_memory.tools.QdrantVectorStore"),
    ):
        service = MemoryService(embedding_service=MagicMock())
        # Make vector_store methods compatible with await
        service.vector_store.upsert = AsyncMock()
        service.vector_store.delete = AsyncMock()

        # Mock the async Redis client for async lock path
        mock_async_client = AsyncMock()
        mock_async_client.set = AsyncMock(return_value=True)
        mock_async_client.delete = AsyncMock()
        service.lock_manager._async_client = mock_async_client

        # The service instantiates LockManager internally, which uses the patched redis
        yield service


@pytest.mark.asyncio
async def test_create_entity_locks_project(
    mock_service_with_lock: MemoryService, mock_redis: MagicMock
) -> None:
    params = EntityCreateParams(name="Test", node_type="Entity", project_id="p1")

    # Mock ontology validation
    mock_service_with_lock.ontology.is_valid_type = MagicMock(return_value=True)
    # Mock repo create
    mock_service_with_lock.repo.create_node = AsyncMock(return_value={"id": "1", "name": "Test"})
    mock_service_with_lock.repo.get_total_node_count = AsyncMock(return_value=1)
    mock_service_with_lock.repo.get_most_recent_entity = AsyncMock(return_value=None)
    mock_service_with_lock.embedder.async_encode = AsyncMock(return_value=[0.1] * 1024)

    await mock_service_with_lock.create_entity(params)

    # Verify lock was acquired for "p1" via async Redis client
    async_client = mock_service_with_lock.lock_manager._async_client
    calls = async_client.set.call_args_list
    assert any("lock:project:p1" in str(c) for c in calls)

    # Verify release via async client
    async_client.delete.assert_called_with("lock:project:p1")


@pytest.mark.asyncio
async def test_update_entity_locks_project(
    mock_service_with_lock: MemoryService, mock_redis: MagicMock
) -> None:
    params = EntityUpdateParams(entity_id="e1", properties={"name": "New"})

    # Mock existing node fetch to return project_id
    mock_service_with_lock.repo.get_node = AsyncMock(return_value={"id": "e1", "project_id": "p2"})
    mock_service_with_lock.repo.update_node = AsyncMock(return_value={"id": "e1"})
    mock_service_with_lock.embedder.async_encode = AsyncMock(return_value=[0.1] * 1024)

    await mock_service_with_lock.update_entity(params)

    # Verify lock for "p2" via async Redis client
    async_client = mock_service_with_lock.lock_manager._async_client
    calls = async_client.set.call_args_list
    assert any("lock:project:p2" in str(c) for c in calls)
    async_client.delete.assert_called_with("lock:project:p2")
