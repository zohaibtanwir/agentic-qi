"""Knowledge search API endpoints.

This module provides REST API endpoints for searching and retrieving
domain knowledge from the Weaviate vector database.

Endpoints:
    POST /api/knowledge/search - Search knowledge base
    GET /api/knowledge/stats - Get knowledge base statistics
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from ecommerce_agent.clients.weaviate_client import get_weaviate_client
from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


class KnowledgeSearchRequest(BaseModel):
    """Request model for knowledge search."""

    query: str = Field(
        ...,
        description="Search query string",
        min_length=1,
        examples=["cart validation rules"]
    )
    limit: int = Field(
        default=10,
        description="Maximum number of results to return",
        ge=1,
        le=100
    )
    collections: Optional[List[str]] = Field(
        default=None,
        description="Specific collections to search. If not provided, searches all collections.",
        examples=[["EcommerceRule", "EcommerceEdgeCase"]]
    )


class KnowledgeSearchResult(BaseModel):
    """Single search result from the knowledge base."""

    title: str = Field(..., description="Title of the knowledge item")
    type: str = Field(
        ...,
        description="Type of knowledge: Business Rule, Edge Case, Entity, or Workflow"
    )
    content: str = Field(..., description="Full content/description of the item")
    relevance: float = Field(
        ...,
        description="Relevance score (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    metadata: Dict[str, Any] = Field(
        default={},
        description="Additional metadata including collection name and document ID"
    )


class KnowledgeSearchResponse(BaseModel):
    """Response model for knowledge search."""

    query: str = Field(..., description="The original search query")
    results: List[KnowledgeSearchResult] = Field(
        ...,
        description="List of matching knowledge items"
    )
    total_results: int = Field(
        ...,
        description="Total number of results returned"
    )


class KnowledgeStatsResponse(BaseModel):
    """Response model for knowledge base statistics."""

    collections_count: int = Field(..., description="Number of collections in the database")
    documents_count: int = Field(..., description="Total number of documents")
    edge_cases_count: int = Field(..., description="Number of edge case documents")
    business_rules_count: int = Field(..., description="Number of business rule documents")
    connected: bool = Field(..., description="Whether the knowledge base is connected")


@router.post(
    "/search",
    response_model=KnowledgeSearchResponse,
    summary="Search domain knowledge",
    description="Search the knowledge base for business rules, edge cases, entities, and workflows.",
    responses={
        200: {"description": "Search results"},
        503: {"description": "Knowledge base not available"},
        500: {"description": "Search failed"}
    }
)
async def search_knowledge(request: KnowledgeSearchRequest):
    """Search the knowledge base for relevant domain information.

    Searches across multiple collections including:
    - EcommerceRule: Business rules and validation logic
    - EcommerceEdgeCase: Edge cases and exception scenarios
    - EcommerceEntity: Domain entity definitions
    - EcommerceWorkflow: Business process workflows

    Results are sorted by relevance score.
    """
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


@router.get(
    "/stats",
    response_model=KnowledgeStatsResponse,
    summary="Get knowledge base statistics",
    description="Returns counts of documents, collections, and connection status."
)
async def get_knowledge_stats():
    """Get statistics about the knowledge base.

    Returns document counts, collection counts, and connectivity status.
    If the knowledge base is not connected, returns zeros with connected=False.
    """
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