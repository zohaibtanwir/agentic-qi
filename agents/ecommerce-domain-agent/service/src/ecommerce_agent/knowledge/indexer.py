"""Knowledge indexer for populating Weaviate with domain data."""

import json
from typing import Any, Dict, List
from datetime import datetime

from ecommerce_agent.clients.weaviate_client import get_weaviate_client
from ecommerce_agent.domain.entities import ENTITIES
from ecommerce_agent.knowledge.collections import COLLECTION_SCHEMAS
from ecommerce_agent.knowledge.documents import (
    BUSINESS_RULES_DOCUMENTS,
    EDGE_CASES_DOCUMENTS,
    TEST_SCENARIOS_DOCUMENTS,
    BEST_PRACTICES_DOCUMENTS,
    PERFORMANCE_PATTERNS_DOCUMENTS,
    SECURITY_PATTERNS_DOCUMENTS,
    get_all_knowledge_documents
)
from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)


class KnowledgeIndexer:
    """Indexes domain knowledge into Weaviate for RAG."""

    def __init__(self):
        """Initialize the indexer."""
        self.client = get_weaviate_client()

    def initialize_collections(self, force_recreate: bool = False) -> bool:
        """Initialize all Weaviate collections."""
        try:
            for schema in COLLECTION_SCHEMAS:
                class_name = schema["class"]

                if force_recreate and self.client.class_exists(class_name):
                    logger.info("Recreating collection", class_name=class_name)
                    self.client.delete_class(class_name)

                if not self.client.class_exists(class_name):
                    success = self.client.create_class(schema)
                    if not success:
                        logger.error("Failed to create collection", class_name=class_name)
                        return False
                else:
                    logger.debug("Collection exists", class_name=class_name)

            logger.info("All collections initialized")
            return True

        except Exception as e:
            logger.error("Failed to initialize collections", error=str(e))
            return False

    def index_entities(self) -> int:
        """Index all entity definitions into Weaviate."""
        indexed = 0
        objects = []

        for entity_name, entity_def in ENTITIES.items():
            # Prepare object for indexing
            obj = {
                "entity_name": entity_def.name,
                "description": entity_def.description,
                "category": entity_def.category,
                "fields_json": json.dumps(
                    [
                        {
                            "name": f.name,
                            "type": f.type,
                            "description": f.description,
                            "required": f.required,
                            "example": f.example,
                        }
                        for f in entity_def.fields
                    ]
                ),
                "relationships_json": json.dumps(
                    [
                        {
                            "target": r.target,
                            "type": r.type,
                            "description": r.description,
                            "required": r.required,
                        }
                        for r in entity_def.relationships
                    ]
                ),
                "business_rules": entity_def.business_rules,
                "edge_cases": entity_def.edge_cases,
                "test_scenarios": entity_def.test_scenarios,
            }
            objects.append(obj)

        # Batch add to Weaviate
        if self.client.batch_add_objects("EcommerceEntity", objects):
            indexed = len(objects)
            logger.info("Indexed entities", count=indexed)

        return indexed

    def index_workflows(self) -> int:
        """Index workflow-related test scenarios into Weaviate."""
        indexed = 0
        objects = []

        # For now, index test scenarios as workflows since they represent test workflows
        for scenario in TEST_SCENARIOS_DOCUMENTS:
            # Prepare object for indexing
            obj = {
                "workflow_name": scenario.get("name", ""),
                "description": scenario.get("description", ""),
                "steps_json": json.dumps(scenario.get("test_data", {})),
                "involved_entities": [scenario.get("entity", "")],
                "business_rules": [],
                "edge_cases": [],
                "test_scenarios": [scenario.get("scenario_id", "")],
            }
            objects.append(obj)

        # Batch add to Weaviate if we have objects
        if objects and self.client.batch_add_objects("EcommerceWorkflow", objects):
            indexed = len(objects)
            logger.info("Indexed workflows/scenarios", count=indexed)

        return indexed

    def index_business_rules(self) -> int:
        """Index all business rules into Weaviate."""
        indexed = 0
        objects = []

        for rule in BUSINESS_RULES_DOCUMENTS:
            # Prepare object for indexing - using the document structure directly
            obj = {
                "rule_id": rule.get("rule_id", ""),
                "name": rule.get("name", ""),
                "entity": rule.get("entity", ""),
                "description": rule.get("description", ""),
                "condition": rule.get("condition", ""),
                "constraint": rule.get("constraint", ""),
                "severity": rule.get("severity", "warning"),
                "validation_logic": rule.get("validation_logic", ""),
            }
            objects.append(obj)

        # Batch add to Weaviate
        if objects and self.client.batch_add_objects("EcommerceRule", objects):
            indexed = len(objects)
            logger.info("Indexed business rules", count=indexed)

        return indexed

    def index_edge_cases(self) -> int:
        """Index all edge cases into Weaviate."""
        indexed = 0
        objects = []

        for edge_case in EDGE_CASES_DOCUMENTS:
            # Prepare object for indexing - using the document structure directly
            obj = {
                "edge_case_id": edge_case.get("edge_case_id", ""),
                "name": edge_case.get("name", ""),
                "category": edge_case.get("category", ""),
                "entity": edge_case.get("entity", ""),
                "workflow": edge_case.get("workflow", ""),
                "description": edge_case.get("description", ""),
                "test_approach": edge_case.get("test_approach", ""),
                "expected_behavior": edge_case.get("expected_behavior", ""),
                "severity": edge_case.get("severity", "medium"),
                "example_data_json": edge_case.get("example_data_json", "{}"),
            }
            objects.append(obj)

        # Batch add to Weaviate
        if objects and self.client.batch_add_objects("EcommerceEdgeCase", objects):
            indexed = len(objects)
            logger.info("Indexed edge cases", count=indexed)

        return indexed

    def add_test_pattern(
        self,
        entity: str,
        scenario: str,
        context: str,
        data: Dict[str, Any],
        quality_score: float = 0.8,
    ) -> bool:
        """Add a successful test pattern to the knowledge base."""
        try:
            obj = {
                "entity": entity,
                "scenario": scenario,
                "context": context,
                "data_json": json.dumps(data),
                "quality_score": quality_score,
                "usage_count": 1,
                "created_at": datetime.utcnow().isoformat(),
            }

            result = self.client.add_object("EcommerceTestPattern", obj)
            if result:
                logger.info(
                    "Added test pattern",
                    entity=entity,
                    scenario=scenario,
                )
                return True
            return False

        except Exception as e:
            logger.error("Failed to add test pattern", error=str(e))
            return False

    def index_all(self, force_recreate: bool = False) -> Dict[str, int]:
        """Index all domain knowledge into Weaviate."""
        results = {
            "entities": 0,
            "workflows": 0,
            "business_rules": 0,
            "edge_cases": 0,
        }

        # Initialize collections
        if not self.initialize_collections(force_recreate):
            logger.error("Failed to initialize collections")
            return results

        # Index each type
        results["entities"] = self.index_entities()
        results["workflows"] = self.index_workflows()
        results["business_rules"] = self.index_business_rules()
        results["edge_cases"] = self.index_edge_cases()

        total = sum(results.values())
        logger.info("Indexing complete", total_indexed=total, breakdown=results)

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about indexed knowledge."""
        try:
            schema = self.client.get_schema()
            stats = {
                "collections": len(schema.get("classes", [])),
                "connected": self.client.is_connected(),
                "counts": {},
            }

            # Get counts for each collection
            for class_info in schema.get("classes", []):
                class_name = class_info.get("class")
                # We'd need to implement a count method in the client
                # For now, just indicate the collection exists
                stats["counts"][class_name] = "exists"

            return stats

        except Exception as e:
            logger.error("Failed to get stats", error=str(e))
            return {
                "collections": 0,
                "connected": False,
                "error": str(e),
            }


def get_indexer() -> KnowledgeIndexer:
    """Get a knowledge indexer instance."""
    return KnowledgeIndexer()