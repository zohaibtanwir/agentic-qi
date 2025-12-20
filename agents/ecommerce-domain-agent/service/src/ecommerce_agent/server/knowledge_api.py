"""Knowledge search API endpoints."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from ecommerce_agent.clients.weaviate_client import get_weaviate_client
from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


class KnowledgeSearchRequest(BaseModel):
    """Request model for knowledge search."""
    query: str
    limit: int = 10
    collections: Optional[List[str]] = None


class KnowledgeSearchResult(BaseModel):
    """Single search result."""
    title: str
    type: str
    content: str
    relevance: float
    metadata: Dict[str, Any] = {}


class KnowledgeSearchResponse(BaseModel):
    """Response model for knowledge search."""
    query: str
    results: List[KnowledgeSearchResult]
    total_results: int


class KnowledgeStatsResponse(BaseModel):
    """Response model for knowledge stats."""
    collections_count: int
    documents_count: int
    edge_cases_count: int
    business_rules_count: int
    connected: bool


@router.post("/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(request: KnowledgeSearchRequest):
    """Search the knowledge base for relevant information."""
    try:
        client = get_weaviate_client()

        if not client.is_connected():
            raise HTTPException(status_code=503, detail="Knowledge base not available")

        # Default collections to search
        collections = request.collections or [
            "EcommerceRule",
            "EcommerceEdgeCase",
            "EcommerceEntity",
            "EcommerceWorkflow"
        ]

        all_results = []

        # Search each collection
        for collection_name in collections:
            try:
                # Use BM25 search for keyword matching
                results = client.search_bm25(
                    class_name=collection_name,
                    query=request.query,
                    limit=request.limit
                )

                # Convert results to response format
                for result in results:
                    # Determine type based on collection
                    doc_type = {
                        "EcommerceRule": "Business Rule",
                        "EcommerceEdgeCase": "Edge Case",
                        "EcommerceEntity": "Entity",
                        "EcommerceWorkflow": "Workflow"
                    }.get(collection_name, "Document")

                    # Extract title and content based on type
                    if collection_name == "EcommerceRule":
                        title = f"{result.get('rule_id', '')} - {result.get('name', 'Unknown Rule')}"
                        content = result.get('description', '')
                    elif collection_name == "EcommerceEdgeCase":
                        title = f"{result.get('edge_case_id', '')} - {result.get('name', 'Unknown Case')}"
                        content = result.get('description', '')
                    elif collection_name == "EcommerceEntity":
                        title = result.get('entity_name', 'Unknown Entity')
                        content = result.get('description', '')
                    elif collection_name == "EcommerceWorkflow":
                        title = result.get('workflow_name', 'Unknown Workflow')
                        content = result.get('description', '')
                    else:
                        title = "Unknown"
                        content = str(result)

                    # Get relevance score
                    score = result.get('_additional', {}).get('score', 0.5)

                    all_results.append(KnowledgeSearchResult(
                        title=title,
                        type=doc_type,
                        content=content,
                        relevance=score,
                        metadata={
                            "collection": collection_name,
                            "id": result.get('_additional', {}).get('id', '')
                        }
                    ))

            except Exception as e:
                logger.warning(f"Failed to search {collection_name}: {str(e)}")
                continue

        # Sort by relevance
        all_results.sort(key=lambda x: x.relevance, reverse=True)

        # Limit total results
        all_results = all_results[:request.limit]

        return KnowledgeSearchResponse(
            query=request.query,
            results=all_results,
            total_results=len(all_results)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Knowledge search failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.get("/stats", response_model=KnowledgeStatsResponse)
async def get_knowledge_stats():
    """Get statistics about the knowledge base."""
    try:
        client = get_weaviate_client()

        if not client.is_connected():
            return KnowledgeStatsResponse(
                collections_count=0,
                documents_count=0,
                edge_cases_count=0,
                business_rules_count=0,
                connected=False
            )

        # Get counts for each collection
        stats = {
            "collections_count": 0,
            "documents_count": 0,
            "edge_cases_count": 0,
            "business_rules_count": 0,
            "connected": True
        }

        try:
            # Count business rules
            rules = client.search_bm25("EcommerceRule", "*", limit=100)
            stats["business_rules_count"] = len(rules)
            stats["documents_count"] += len(rules)

            # Count edge cases
            edge_cases = client.search_bm25("EcommerceEdgeCase", "*", limit=100)
            stats["edge_cases_count"] = len(edge_cases)
            stats["documents_count"] += len(edge_cases)

            # Count collections
            schema = client.get_schema()
            stats["collections_count"] = len(schema.get("classes", []))

        except Exception as e:
            logger.warning(f"Failed to get stats: {str(e)}")

        return KnowledgeStatsResponse(**stats)

    except Exception as e:
        logger.error(f"Failed to get knowledge stats: {str(e)}")
        return KnowledgeStatsResponse(
            collections_count=0,
            documents_count=0,
            edge_cases_count=0,
            business_rules_count=0,
            connected=False
        )