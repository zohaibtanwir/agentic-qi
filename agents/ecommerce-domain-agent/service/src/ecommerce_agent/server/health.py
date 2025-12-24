from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ecommerce_agent.config import get_settings
from ecommerce_agent.utils.logging import get_logger
from ecommerce_agent.server.api import add_api_routes
from ecommerce_agent.clients.weaviate_client import get_weaviate_client

logger = get_logger(__name__)


class HealthResponse(BaseModel):
    status: str
    components: dict[str, str]


class ReadyResponse(BaseModel):
    ready: bool
    checks: dict[str, bool]


def create_health_app() -> FastAPI:
    """Create FastAPI app for health endpoints."""
    app = FastAPI(
        title="eCommerce Domain Agent Health",
        version="0.1.0",
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

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        """Basic health check."""
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

    @app.get("/health/live")
    async def liveness() -> Response:
        """Kubernetes liveness probe."""
        return Response(status_code=200)

    @app.get("/health/ready", response_model=ReadyResponse)
    async def readiness() -> ReadyResponse:
        """Kubernetes readiness probe."""
        checks = {
            "grpc": component_status.get("grpc") == "healthy",
            "weaviate": component_status.get("weaviate") in ("healthy", "unknown"),
            "test_data_agent": component_status.get("test_data_agent") in ("healthy", "unknown"),
        }
        ready = all(checks.values())
        return ReadyResponse(ready=ready, checks=checks)

    @app.get("/metrics")
    async def metrics() -> Response:
        """Prometheus metrics endpoint."""
        # TODO: Integrate with prometheus_client
        return Response(content="# Metrics placeholder", media_type="text/plain")

    def update_component_status(component: str, status: str) -> None:
        """Update component health status."""
        component_status[component] = status

    app.state.update_component_status = update_component_status

    # Add API routes for test data generation
    add_api_routes(app)

    return app