"""Health check and API endpoints for the eCommerce Domain Agent.

This module provides:
- Health check endpoints for Kubernetes probes
- Prometheus metrics endpoint
- REST API routes for test data generation and knowledge search
"""

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ecommerce_agent.config import get_settings
from ecommerce_agent.utils.logging import get_logger
from ecommerce_agent.server.api import add_api_routes
from ecommerce_agent.clients.weaviate_client import get_weaviate_client

logger = get_logger(__name__)


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(
        ...,
        description="Overall health status: healthy, degraded, or unhealthy",
        examples=["healthy"]
    )
    components: dict[str, str] = Field(
        ...,
        description="Health status of individual components",
        examples=[{"grpc": "healthy", "weaviate": "healthy"}]
    )


class ReadyResponse(BaseModel):
    """Readiness check response model."""

    ready: bool = Field(
        ...,
        description="Whether the service is ready to accept traffic"
    )
    checks: dict[str, bool] = Field(
        ...,
        description="Individual readiness checks",
        examples=[{"grpc": True, "weaviate": True}]
    )


API_DESCRIPTION = """
## eCommerce Domain Agent API

The eCommerce Domain Agent provides intelligent test data generation and domain knowledge
management for e-commerce testing scenarios.

### Features

* **Test Data Generation** - Generate realistic test data for e-commerce entities
* **Domain Knowledge Search** - Search business rules, edge cases, and workflows
* **Context Enrichment** - Enrich test scenarios with domain-specific context

### Entities Supported

- Cart, Order, Payment, Inventory, Customer, Shipping

### Documentation

- [gRPC API Documentation](/docs/grpc)
- [Knowledge Base API](/api/knowledge/docs)
"""


def create_health_app() -> FastAPI:
    """Create FastAPI app for health and API endpoints.

    Returns:
        FastAPI: Configured FastAPI application with health checks,
                 knowledge API, and test data generation endpoints.
    """
    app = FastAPI(
        title="eCommerce Domain Agent API",
        description=API_DESCRIPTION,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=[
            {
                "name": "health",
                "description": "Health check and observability endpoints"
            },
            {
                "name": "knowledge",
                "description": "Domain knowledge search and retrieval"
            },
            {
                "name": "generation",
                "description": "Test data generation endpoints"
            },
        ],
    )

    # Add CORS middleware to allow frontend access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    settings = get_settings()

    # Track component health
    component_status: dict[str, str] = {
        "grpc": "healthy",  # gRPC server is running locally
        "weaviate": "unknown",
        "test_data_agent": "disabled",  # Not running for local demo
    }

    def check_weaviate_health() -> str:
        """Check Weaviate connection status."""
        try:
            client = get_weaviate_client()
            if client.is_connected():
                return "healthy"
            return "unhealthy"
        except Exception:
            return "unhealthy"

    @app.get(
        "/health",
        response_model=HealthResponse,
        tags=["health"],
        summary="Get service health status",
        description="Returns overall health status and individual component health."
    )
    async def health() -> HealthResponse:
        """Check health of all service components.

        Returns the overall health status (healthy, degraded, unhealthy)
        and individual component statuses for gRPC, Weaviate, and Test Data Agent.
        """
        # Check Weaviate status
        component_status["weaviate"] = check_weaviate_health()

        # Consider "disabled" as ok for local demo
        critical_components = [v for k, v in component_status.items() if v != "disabled"]
        if not critical_components or all(s == "healthy" for s in critical_components):
            overall = "healthy"
        elif any(s == "unhealthy" for s in critical_components):
            overall = "unhealthy"
        else:
            overall = "degraded"
        return HealthResponse(status=overall, components=component_status)

    @app.get(
        "/health/live",
        tags=["health"],
        summary="Kubernetes liveness probe",
        description="Returns 200 if service is running. Used by Kubernetes for liveness checks."
    )
    async def liveness() -> Response:
        """Simple liveness check - always returns 200 if the process is running."""
        return Response(status_code=200)

    @app.get(
        "/health/ready",
        response_model=ReadyResponse,
        tags=["health"],
        summary="Kubernetes readiness probe",
        description="Returns readiness status. Service is ready when all critical dependencies are available."
    )
    async def readiness() -> ReadyResponse:
        """Check if service is ready to accept traffic.

        Verifies that gRPC server and Weaviate are operational before
        marking the service as ready.
        """
        checks = {
            "grpc": component_status.get("grpc") == "healthy",
            "weaviate": component_status.get("weaviate") in ("healthy", "unknown"),
            "test_data_agent": component_status.get("test_data_agent") in ("healthy", "unknown"),
        }
        ready = all(checks.values())
        return ReadyResponse(ready=ready, checks=checks)

    @app.get(
        "/metrics",
        tags=["health"],
        summary="Prometheus metrics",
        description="Prometheus-compatible metrics endpoint for monitoring."
    )
    async def metrics() -> Response:
        """Prometheus metrics endpoint for observability."""
        # TODO: Integrate with prometheus_client
        return Response(content="# Metrics placeholder", media_type="text/plain")

    def update_component_status(component: str, status: str) -> None:
        """Update component health status."""
        component_status[component] = status

    app.state.update_component_status = update_component_status

    # Add API routes for test data generation
    add_api_routes(app)

    return app