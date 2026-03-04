import asyncio
import sys
from unittest.mock import AsyncMock, patch

import pytest

# Fix 1: Windows' ProactorEventLoop hangs during pytest-asyncio teardown.
# SelectorEventLoop works fine for mocked unit tests.
if sys.platform == "win32":

    @pytest.fixture(scope="session")
    def event_loop_policy():
        return asyncio.WindowsSelectorEventLoopPolicy()


# Fix 2: retry_on_transient uses exponential backoff (1+2+4+8+16=31s).
# In tests, this causes timeouts. Patch asyncio.sleep to be instant.
@pytest.fixture(autouse=True)
def _fast_retries():
    with patch("claude_memory.retry.asyncio.sleep", new_callable=AsyncMock):
        with patch("claude_memory.retry.time.sleep"):
            yield


# Define Mock Protocol or just a class
class MockVectorStore:
    def __init__(self) -> None:
        self.upsert = AsyncMock()
        self.search = AsyncMock(return_value=[])
        self.delete = AsyncMock()


@pytest.fixture
def mock_vector_store() -> MockVectorStore:
    return MockVectorStore()
