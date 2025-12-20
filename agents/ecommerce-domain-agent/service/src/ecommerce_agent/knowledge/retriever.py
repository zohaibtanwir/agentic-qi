"""Knowledge retriever for RAG-based domain context retrieval."""

import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from ecommerce_agent.clients.weaviate_client import get_weaviate_client
from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RetrievalResult:
    """Result from knowledge retrieval."""

    item_type: str  # entity, workflow, rule, edge_case, pattern
    title: str
    content: str
    relevance_score: float
    metadata: Dict[str, Any]


class KnowledgeRetriever:
    """Retrieves domain knowledge from Weaviate using semantic search."""

    def __init__(self):
        """Initialize the retriever."""
        self.client = get_weaviate_client()

    def search(
        self,
        query: str,
        categories: Optional[List[str]] = None,
        max_results: int = 10,
    ) -> List[RetrievalResult]:
        """
        Search across all knowledge categories.

        Args:
            query: Natural language query
            categories: Filter by categories (entities, workflows, rules, edge_cases)
            max_results: Maximum results to return

        Returns:
            List of retrieval results sorted by relevance
        """
        all_results = []

        # Define which collections to search based on categories
        collections_to_search = []
        if not categories or "entities" in categories:
            collections_to_search.append("EcommerceEntity")
        if not categories or "workflows" in categories:
            collections_to_search.append("EcommerceWorkflow")
        if not categories or "rules" in categories:
            collections_to_search.append("EcommerceRule")
        if not categories or "edge_cases" in categories:
            collections_to_search.append("EcommerceEdgeCase")

        # Search each collection
        for collection in collections_to_search:
            results = self._search_collection(collection, query, max_results)
            all_results.extend(results)

        # Sort by relevance score and limit
        all_results.sort(key=lambda x: x.relevance_score, reverse=True)
        return all_results[:max_results]

    def _search_collection(
        self,
        collection: str,
        query: str,
        limit: int,
    ) -> List[RetrievalResult]:
        """Search a specific collection."""
        try:
            # Use BM25 for keyword search (simpler than vector search for now)
            results = self.client.search_bm25(
                class_name=collection,
                query=query,
                limit=limit,
            )

            retrieval_results = []
            for item in results:
                # Parse result based on collection type
                if collection == "EcommerceEntity":
                    result = self._parse_entity_result(item)
                elif collection == "EcommerceWorkflow":
                    result = self._parse_workflow_result(item)
                elif collection == "EcommerceRule":
                    result = self._parse_rule_result(item)
                elif collection == "EcommerceEdgeCase":
                    result = self._parse_edge_case_result(item)
                else:
                    continue

                if result:
                    retrieval_results.append(result)

            return retrieval_results

        except Exception as e:
            logger.error(
                "Failed to search collection",
                collection=collection,
                error=str(e),
            )
            return []

    def _parse_entity_result(self, item: Dict[str, Any]) -> Optional[RetrievalResult]:
        """Parse entity search result."""
        try:
            additional = item.get("_additional", {})
            score = additional.get("score", 0.0)

            return RetrievalResult(
                item_type="entity",
                title=item.get("entity_name", "Unknown Entity"),
                content=item.get("description", ""),
                relevance_score=float(score),
                metadata={
                    "category": item.get("category"),
                    "fields": json.loads(item.get("fields_json", "[]")),
                    "relationships": json.loads(item.get("relationships_json", "[]")),
                    "business_rules": item.get("business_rules", []),
                    "edge_cases": item.get("edge_cases", []),
                    "test_scenarios": item.get("test_scenarios", []),
                },
            )
        except Exception as e:
            logger.error("Failed to parse entity result", error=str(e))
            return None

    def _parse_workflow_result(self, item: Dict[str, Any]) -> Optional[RetrievalResult]:
        """Parse workflow search result."""
        try:
            additional = item.get("_additional", {})
            score = additional.get("score", 0.0)

            return RetrievalResult(
                item_type="workflow",
                title=item.get("workflow_name", "Unknown Workflow"),
                content=item.get("description", ""),
                relevance_score=float(score),
                metadata={
                    "steps": json.loads(item.get("steps_json", "[]")),
                    "involved_entities": item.get("involved_entities", []),
                    "business_rules": item.get("business_rules", []),
                    "edge_cases": item.get("edge_cases", []),
                    "test_scenarios": item.get("test_scenarios", []),
                },
            )
        except Exception as e:
            logger.error("Failed to parse workflow result", error=str(e))
            return None

    def _parse_rule_result(self, item: Dict[str, Any]) -> Optional[RetrievalResult]:
        """Parse business rule search result."""
        try:
            additional = item.get("_additional", {})
            score = additional.get("score", 0.0)

            return RetrievalResult(
                item_type="business_rule",
                title=f"{item.get('rule_id', 'Unknown')}: {item.get('name', 'Unknown Rule')}",
                content=item.get("description", ""),
                relevance_score=float(score),
                metadata={
                    "entity": item.get("entity"),
                    "condition": item.get("condition"),
                    "constraint": item.get("constraint"),
                    "severity": item.get("severity"),
                    "validation_logic": item.get("validation_logic"),
                },
            )
        except Exception as e:
            logger.error("Failed to parse rule result", error=str(e))
            return None

    def _parse_edge_case_result(self, item: Dict[str, Any]) -> Optional[RetrievalResult]:
        """Parse edge case search result."""
        try:
            additional = item.get("_additional", {})
            score = additional.get("score", 0.0)

            return RetrievalResult(
                item_type="edge_case",
                title=f"{item.get('edge_case_id', 'Unknown')}: {item.get('name', 'Unknown Edge Case')}",
                content=item.get("description", ""),
                relevance_score=float(score),
                metadata={
                    "category": item.get("category"),
                    "entity": item.get("entity"),
                    "workflow": item.get("workflow"),
                    "test_approach": item.get("test_approach"),
                    "expected_behavior": item.get("expected_behavior"),
                    "severity": item.get("severity"),
                    "example_data": json.loads(item.get("example_data_json", "{}")),
                },
            )
        except Exception as e:
            logger.error("Failed to parse edge case result", error=str(e))
            return None

    def get_entity_context(self, entity_name: str) -> Dict[str, Any]:
        """Get comprehensive context for a specific entity."""
        context = {
            "entity": None,
            "related_workflows": [],
            "business_rules": [],
            "edge_cases": [],
        }

        try:
            # Search for the entity
            entity_results = self.client.search_bm25(
                class_name="EcommerceEntity",
                query=entity_name,
                limit=1,
            )
            if entity_results:
                context["entity"] = entity_results[0]

            # Search for related workflows
            workflow_results = self.client.search_bm25(
                class_name="EcommerceWorkflow",
                query=entity_name,
                limit=5,
            )
            context["related_workflows"] = workflow_results

            # Search for related business rules
            rule_results = self.client.search_bm25(
                class_name="EcommerceRule",
                query=entity_name,
                limit=10,
            )
            context["business_rules"] = rule_results

            # Search for related edge cases
            edge_case_results = self.client.search_bm25(
                class_name="EcommerceEdgeCase",
                query=entity_name,
                limit=10,
            )
            context["edge_cases"] = edge_case_results

        except Exception as e:
            logger.error("Failed to get entity context", entity=entity_name, error=str(e))

        return context

    def get_workflow_context(self, workflow_name: str) -> Dict[str, Any]:
        """Get comprehensive context for a specific workflow."""
        context = {
            "workflow": None,
            "involved_entities": [],
            "business_rules": [],
            "edge_cases": [],
        }

        try:
            # Search for the workflow
            workflow_results = self.client.search_bm25(
                class_name="EcommerceWorkflow",
                query=workflow_name,
                limit=1,
            )
            if workflow_results:
                workflow = workflow_results[0]
                context["workflow"] = workflow

                # Get involved entities
                for entity_name in workflow.get("involved_entities", []):
                    entity_results = self.client.search_bm25(
                        class_name="EcommerceEntity",
                        query=entity_name,
                        limit=1,
                    )
                    if entity_results:
                        context["involved_entities"].append(entity_results[0])

            # Search for related business rules
            rule_results = self.client.search_bm25(
                class_name="EcommerceRule",
                query=workflow_name,
                limit=10,
            )
            context["business_rules"] = rule_results

            # Search for related edge cases
            edge_case_results = self.client.search_bm25(
                class_name="EcommerceEdgeCase",
                query=workflow_name,
                limit=10,
            )
            context["edge_cases"] = edge_case_results

        except Exception as e:
            logger.error("Failed to get workflow context", workflow=workflow_name, error=str(e))

        return context

    def find_test_patterns(
        self,
        entity: str,
        scenario: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Find successful test patterns for an entity/scenario."""
        try:
            query = f"{entity}"
            if scenario:
                query += f" {scenario}"

            results = self.client.search_bm25(
                class_name="EcommerceTestPattern",
                query=query,
                limit=limit,
            )

            # Parse and return patterns
            patterns = []
            for result in results:
                patterns.append({
                    "entity": result.get("entity"),
                    "scenario": result.get("scenario"),
                    "context": result.get("context"),
                    "data": json.loads(result.get("data_json", "{}")),
                    "quality_score": result.get("quality_score", 0.0),
                    "usage_count": result.get("usage_count", 0),
                })

            return patterns

        except Exception as e:
            logger.error("Failed to find test patterns", error=str(e))
            return []

    def summarize_knowledge(self, query: str, max_items: int = 5) -> str:
        """Get a summary of knowledge related to a query."""
        try:
            results = self.search(query, max_results=max_items)

            if not results:
                return "No relevant knowledge found for the query."

            summary_parts = [f"Found {len(results)} relevant items:\n"]

            for result in results:
                summary_parts.append(
                    f"- {result.title} ({result.item_type}): {result.content[:100]}..."
                )

            return "\n".join(summary_parts)

        except Exception as e:
            logger.error("Failed to summarize knowledge", error=str(e))
            return "Failed to retrieve knowledge summary."


def get_retriever() -> KnowledgeRetriever:
    """Get a knowledge retriever instance."""
    return KnowledgeRetriever()