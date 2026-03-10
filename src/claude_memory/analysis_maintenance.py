"""Maintenance operations extracted from analysis.py.

Provides archive, prune, consolidation, and memory-type management
to keep AnalysisMixin under 300 LOC.

Mixed into MemoryService via AnalysisMixin inheritance chain.
"""

import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from .interfaces import Embedder, VectorStore
    from .ontology import OntologyManager
    from .repository import MemoryRepository

logger = logging.getLogger(__name__)


class AnalysisMaintenanceMixin:
    """Maintenance ops — archive, prune, consolidate, ontology types.

    Mixed into :class:`AnalysisMixin` to split file under 300 LOC.
    """

    repo: "MemoryRepository"
    embedder: "Embedder"
    vector_store: "VectorStore"
    ontology: "OntologyManager"

    async def archive_entity(self, entity_id: str) -> dict[str, Any]:
        """Archive an entity (logical hide).

        Deletes Qdrant vector BEFORE graph update to prevent ghost search results.
        """
        await self.vector_store.delete(entity_id)
        return self.repo.update_node(entity_id, {"status": "archived"})  # type: ignore[no-any-return]

    async def prune_stale(self, days: int = 30) -> dict[str, Any]:
        """Hard delete archived entities older than N days.

        Deletes Qdrant vectors BEFORE graph nodes to prevent orphan vectors.
        Order: SELECT IDs → delete vectors → DETACH DELETE graph nodes.
        """
        cutoff = (datetime.now(UTC) - timedelta(days=days)).isoformat()

        # Step 1: SELECT IDs of entities to prune (don't delete yet)
        select_query = """
        MATCH (n:Entity)
        WHERE n.status = 'archived' AND n.archived_at < $cutoff
        RETURN n.id
        """
        res = self.repo.execute_cypher(select_query, {"cutoff": cutoff})
        entity_ids = [row[0] for row in res.result_set] if res.result_set else []

        if not entity_ids:
            return {"status": "success", "deleted_count": 0}

        # Step 2: Delete Qdrant vectors FIRST (fail-safe order)
        for entity_id in entity_ids:
            await self.vector_store.delete(entity_id)

        # Step 3: DETACH DELETE from FalkorDB
        delete_query = """
        MATCH (n:Entity)
        WHERE n.status = 'archived' AND n.archived_at < $cutoff
        DETACH DELETE n
        RETURN count(n) as deleted_count
        """
        del_res = self.repo.execute_cypher(delete_query, {"cutoff": cutoff})
        count = del_res.result_set[0][0] if del_res.result_set else 0
        return {"status": "success", "deleted_count": count}

    async def consolidate_memories(self, entity_ids: list[str], summary: str) -> dict[str, Any]:
        """Merge multiple entities into a new Consolidated concept."""
        from .schema import EntityCreateParams  # noqa: PLC0415

        new_id = str(uuid.uuid4())

        params = EntityCreateParams(
            name=f"Consolidated Memory: {summary[:20]}...",
            node_type="Concept",
            project_id="memory_maintenance",
            properties={"description": summary, "id": new_id, "is_consolidated": True},
        )

        # Compute embedding
        text_to_embed = f"{params.name} {params.node_type} {summary}"
        embedding = self.embedder.encode(text_to_embed)

        props = params.properties.copy()
        props.update(
            {
                "name": params.name,
                "node_type": params.node_type,
                "project_id": params.project_id,
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat(),
            }
        )

        # 1. Write Graph
        new_node_props = self.repo.create_node("Concept", props)

        # 2. Write Vector
        payload = {
            "name": params.name,
            "node_type": params.node_type,
            "project_id": params.project_id,
        }
        await self.vector_store.upsert(id=new_id, vector=embedding, payload=payload)

        # 3. Link old to new
        errors: list[str] = []
        for old_id in entity_ids:
            try:
                link_props = {
                    "confidence": 1.0,
                    "created_at": datetime.now(UTC).isoformat(),
                }
                self.repo.create_edge(old_id, new_id, "PART_OF", link_props)

                # Archive old
                self.repo.update_node(
                    old_id,
                    {"status": "archived", "archived_at": datetime.now(UTC).isoformat()},
                )
            except (ConnectionError, TimeoutError, OSError) as e:
                logger.error("consolidate_memories: failed to archive %s: %s", old_id, e)
                errors.append(f"{old_id}: {e}")

        result = dict(new_node_props) if not isinstance(new_node_props, dict) else new_node_props
        if errors:
            result["consolidation_errors"] = errors
        return result

    def create_memory_type(
        self, name: str, description: str, required_properties: list[str] | None = None
    ) -> dict[str, Any]:
        """Registers a new memory type in the ontology."""
        if required_properties is None:
            required_properties = []
        self.ontology.add_type(name, description, required_properties)
        return {
            "name": name,
            "description": description,
            "required_properties": required_properties,
            "status": "active",
        }
