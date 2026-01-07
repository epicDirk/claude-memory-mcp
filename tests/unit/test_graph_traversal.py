from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

from claude_memory.tools import MemoryService


@pytest.fixture  # type: ignore
def memory_service() -> Generator[MemoryService, None, None]:
    with patch("claude_memory.tools.FalkorDB"):
        service = MemoryService()
        service.client = MagicMock()
        service.client.select_graph.return_value = MagicMock()
        yield service


@pytest.mark.asyncio  # type: ignore
async def test_get_neighbors(memory_service: MemoryService) -> None:
    graph = memory_service.client.select_graph.return_value

    # Mock result for get_neighbors
    mock_node = MagicMock()
    mock_node.properties = {"id": "n2", "name": "Neighbor"}

    # result_set = [[node1], [node2]] ? No, query returns distinct m.
    # Usually list of rows. Row is list of columns.
    # [[node]]
    graph.query.return_value.result_set = [[mock_node]]

    result = await memory_service.get_neighbors("n1", depth=1)

    assert len(result) == 1
    assert result[0]["id"] == "n2"
    assert "MATCH (n)-[*1..1]-(m)" in graph.query.call_args[0][0]


@pytest.mark.asyncio  # type: ignore
async def test_traverse_path(memory_service: MemoryService) -> None:
    graph = memory_service.client.select_graph.return_value

    # Mock result for traverse_path
    # Returns 'p'. If p is Path object.
    mock_path = MagicMock()

    # Create fake nodes
    node1 = MagicMock()
    node1.properties = {"id": "start"}
    node2 = MagicMock()
    node2.properties = {"id": "end"}

    mock_path.nodes = [node1, node2]

    # Result set: [[path_obj]]
    graph.query.return_value.result_set = [[mock_path]]

    result = await memory_service.traverse_path("start", "end")

    assert len(result) == 2
    assert result[0]["id"] == "start"
    assert result[1]["id"] == "end"

    assert "shortestPath" in graph.query.call_args[0][0]
