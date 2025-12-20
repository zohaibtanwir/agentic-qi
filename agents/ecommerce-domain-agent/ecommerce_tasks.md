# eCommerce Domain Agent - Implementation Tasks

> **Usage:** Copy individual tasks into your IDE's AI chat (Claude Code, Cursor, Windsurf) to implement incrementally. Each task is self-contained with clear acceptance criteria.

---

## Phase 1: Service Foundation

### Task 1.1: Initialize Monorepo Structure

```
Create the eCommerce Domain Agent monorepo structure.

Create the following directory structure:

ecommerce-domain-agent/
├── README.md
├── docker-compose.yml
├── Makefile
├── .gitignore
│
├── service/
│   ├── pyproject.toml
│   ├── Dockerfile
│   ├── .env.example
│   ├── protos/
│   │   └── .gitkeep
│   ├── src/
│   │   └── ecommerce_agent/
│   │       └── __init__.py
│   ├── tests/
│   │   └── __init__.py
│   └── k8s/
│       └── .gitkeep
│
└── ui/
    └── .gitkeep

Create pyproject.toml:
```toml
[project]
name = "ecommerce-domain-agent"
version = "0.1.0"
description = "eCommerce Domain Agent for QA Intelligence Platform"
requires-python = ">=3.11"
dependencies = [
    "grpcio>=1.60.0",
    "grpcio-tools>=1.60.0",
    "fastapi>=0.109.0",
    "uvicorn>=0.27.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.0.0",
    "anthropic>=0.40.0",
    "weaviate-client>=4.0.0",
    "structlog>=24.0.0",
    "prometheus-client>=0.19.0",
    "opentelemetry-api>=1.22.0",
    "opentelemetry-sdk>=1.22.0",
    "opentelemetry-exporter-otlp>=1.22.0",
    "httpx>=0.26.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "black>=24.0.0",
    "ruff>=0.1.0",
    "mypy>=1.8.0",
    "grpcio-testing>=1.60.0",
]

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.black]
line-length = 100

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W"]
```

Create .env.example:
```
# Service
SERVICE_NAME=ecommerce-domain-agent
GRPC_PORT=9002
HTTP_PORT=8082
LOG_LEVEL=INFO

# LLM - Claude
ANTHROPIC_API_KEY=your-api-key-here
CLAUDE_MODEL=claude-sonnet-4-20250514

# RAG - Weaviate
WEAVIATE_URL=http://localhost:8081

# Test Data Agent
TEST_DATA_AGENT_HOST=localhost
TEST_DATA_AGENT_PORT=9001

# Observability
PROMETHEUS_PORT=9092
OTLP_ENDPOINT=http://localhost:4317
```

Create root Makefile:
```makefile
.PHONY: all dev build test clean

dev:
	docker-compose up

dev-service:
	cd service && python -m ecommerce_agent.main

dev-ui:
	cd ui && pnpm dev

build:
	docker-compose build

test: test-service test-ui

test-service:
	cd service && pytest

test-ui:
	cd ui && pnpm test

proto:
	cd service && python -m grpc_tools.protoc \
		-I./protos \
		--python_out=./src/ecommerce_agent/proto \
		--grpc_python_out=./src/ecommerce_agent/proto \
		./protos/*.proto
	cd ui && pnpm proto:generate

clean:
	docker-compose down -v
```

Acceptance Criteria:
- [ ] Directory structure created
- [ ] pyproject.toml has all dependencies
- [ ] Makefile has all targets
- [ ] .env.example has all variables
```

---

### Task 1.2: Create Configuration Management

```
Create the configuration module using Pydantic Settings.

Create src/ecommerce_agent/config.py:

```python
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Service
    service_name: str = "ecommerce-domain-agent"
    grpc_port: int = 9002
    http_port: int = 8082
    log_level: str = "INFO"
    
    # LLM - Claude
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    claude_model: str = "claude-sonnet-4-20250514"
    claude_max_tokens: int = 4096
    claude_temperature: float = 0.7
    
    # RAG - Weaviate
    weaviate_url: str = "http://weaviate:8080"
    weaviate_api_key: str = ""
    
    # Test Data Agent (client)
    test_data_agent_host: str = "test-data-agent"
    test_data_agent_port: int = 9001
    test_data_agent_timeout: float = 30.0
    
    # Knowledge
    knowledge_refresh_interval: int = 3600
    
    # Observability
    prometheus_port: int = 9092
    otlp_endpoint: str = "http://otel-collector:4317"
    enable_tracing: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
```

Create src/ecommerce_agent/__init__.py:
```python
"""eCommerce Domain Agent for QA Intelligence Platform."""

__version__ = "0.1.0"
```

Acceptance Criteria:
- [ ] Settings class loads all environment variables
- [ ] get_settings() returns cached instance
- [ ] Default values are sensible
- [ ] Required fields (anthropic_api_key) raise error if missing
```

---

### Task 1.3: Create Structured Logging

```
Create the logging module using structlog.

Create src/ecommerce_agent/utils/__init__.py:
```python
"""Utility modules."""
```

Create src/ecommerce_agent/utils/logging.py:

```python
import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor

from ecommerce_agent.config import get_settings


def setup_logging() -> None:
    """Configure structured logging."""
    settings = get_settings()
    
    # Configure structlog processors
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    
    if settings.log_level == "DEBUG":
        # Pretty printing for development
        shared_processors.append(structlog.dev.ConsoleRenderer())
    else:
        # JSON for production
        shared_processors.extend([
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ])
    
    structlog.configure(
        processors=shared_processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Also configure standard logging to use structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a logger instance with the given name."""
    return structlog.get_logger(name)


def bind_context(**kwargs: Any) -> None:
    """Bind context variables to all subsequent log calls."""
    structlog.contextvars.bind_contextvars(**kwargs)


def clear_context() -> None:
    """Clear all context variables."""
    structlog.contextvars.clear_contextvars()
```

Acceptance Criteria:
- [ ] Logs are structured JSON in production
- [ ] Logs are pretty-printed in development (DEBUG level)
- [ ] Context binding works (request_id, etc.)
- [ ] Log level is configurable
```

---

### Task 1.4: Create gRPC Proto Definition

```
Create the gRPC service definition for the eCommerce Domain Agent.

Create service/protos/ecommerce_domain.proto:

```protobuf
syntax = "proto3";

package ecommerce.domain.v1;

option python_package = "ecommerce_agent.proto";

// Service exposed by eCommerce Domain Agent
service EcommerceDomainService {
  // Get domain context for test generation
  rpc GetDomainContext(DomainContextRequest) returns (DomainContextResponse);
  
  // Query domain knowledge
  rpc QueryKnowledge(KnowledgeRequest) returns (KnowledgeResponse);
  
  // Get entity details
  rpc GetEntity(EntityRequest) returns (EntityResponse);
  
  // Get workflow details
  rpc GetWorkflow(WorkflowRequest) returns (WorkflowResponse);
  
  // List all entities
  rpc ListEntities(ListEntitiesRequest) returns (ListEntitiesResponse);
  
  // List all workflows
  rpc ListWorkflows(ListWorkflowsRequest) returns (ListWorkflowsResponse);
  
  // Get edge cases for an entity/workflow
  rpc GetEdgeCases(EdgeCasesRequest) returns (EdgeCasesResponse);
  
  // Generate test data (proxies to Test Data Agent with domain context)
  rpc GenerateTestData(GenerateTestDataRequest) returns (GenerateTestDataResponse);
  
  // Health check
  rpc HealthCheck(HealthCheckRequest) returns (HealthCheckResponse);
}

// ============ Domain Context ============

message DomainContextRequest {
  string request_id = 1;
  string entity = 2;
  string workflow = 3;
  string scenario = 4;
  repeated string aspects = 5;
}

message DomainContextResponse {
  string request_id = 1;
  string context = 2;
  repeated BusinessRule rules = 3;
  repeated EntityRelationship relationships = 4;
  repeated string edge_cases = 5;
  map<string, string> metadata = 6;
}

message BusinessRule {
  string id = 1;
  string name = 2;
  string description = 3;
  string entity = 4;
  string condition = 5;
  string constraint = 6;
  string severity = 7;
}

message EntityRelationship {
  string source_entity = 1;
  string target_entity = 2;
  string relationship_type = 3;
  string description = 4;
  bool required = 5;
}

// ============ Knowledge Query ============

message KnowledgeRequest {
  string request_id = 1;
  string query = 2;
  repeated string categories = 3;
  int32 max_results = 4;
}

message KnowledgeResponse {
  string request_id = 1;
  repeated KnowledgeItem items = 2;
  string summary = 3;
}

message KnowledgeItem {
  string id = 1;
  string category = 2;
  string title = 3;
  string content = 4;
  float relevance_score = 5;
  map<string, string> metadata = 6;
}

// ============ Entities ============

message EntityRequest {
  string entity_name = 1;
  bool include_relationships = 2;
  bool include_rules = 3;
  bool include_edge_cases = 4;
}

message EntityResponse {
  Entity entity = 1;
}

message Entity {
  string name = 1;
  string description = 2;
  repeated EntityField fields = 3;
  repeated BusinessRule rules = 4;
  repeated EntityRelationship relationships = 5;
  repeated string edge_cases = 6;
  repeated string test_scenarios = 7;
}

message EntityField {
  string name = 1;
  string type = 2;
  string description = 3;
  bool required = 4;
  repeated string validations = 5;
  string example = 6;
}

message ListEntitiesRequest {
  string category = 1;
}

message ListEntitiesResponse {
  repeated EntitySummary entities = 1;
}

message EntitySummary {
  string name = 1;
  string description = 2;
  string category = 3;
  int32 field_count = 4;
}

// ============ Workflows ============

message WorkflowRequest {
  string workflow_name = 1;
  bool include_steps = 2;
  bool include_edge_cases = 3;
}

message WorkflowResponse {
  Workflow workflow = 1;
}

message Workflow {
  string name = 1;
  string description = 2;
  repeated WorkflowStep steps = 3;
  repeated string involved_entities = 4;
  repeated BusinessRule rules = 5;
  repeated string edge_cases = 6;
  repeated string test_scenarios = 7;
}

message WorkflowStep {
  int32 order = 1;
  string name = 2;
  string description = 3;
  string entity = 4;
  string action = 5;
  repeated string validations = 6;
  repeated string possible_outcomes = 7;
}

message ListWorkflowsRequest {}

message ListWorkflowsResponse {
  repeated WorkflowSummary workflows = 1;
}

message WorkflowSummary {
  string name = 1;
  string description = 2;
  int32 step_count = 3;
  repeated string involved_entities = 4;
}

// ============ Edge Cases ============

message EdgeCasesRequest {
  string entity = 1;
  string workflow = 2;
  string category = 3;
}

message EdgeCasesResponse {
  repeated EdgeCase edge_cases = 1;
}

message EdgeCase {
  string id = 1;
  string name = 2;
  string description = 3;
  string category = 4;
  string entity = 5;
  string workflow = 6;
  string test_approach = 7;
  map<string, string> example_data = 8;
  string expected_behavior = 9;
  string severity = 10;
}

// ============ Test Data Generation ============

message GenerateTestDataRequest {
  string request_id = 1;
  string entity = 2;
  int32 count = 3;
  string workflow_context = 4;
  repeated string scenarios = 5;
  string custom_context = 6;
  bool include_edge_cases = 7;
  string output_format = 8;
  map<string, int32> scenario_counts = 9;
}

message GenerateTestDataResponse {
  string request_id = 1;
  bool success = 2;
  string data = 3;
  int32 record_count = 4;
  GenerationMetadata metadata = 5;
  string error = 6;
}

message GenerationMetadata {
  string generation_path = 1;
  int32 llm_tokens_used = 2;
  float generation_time_ms = 3;
  float coherence_score = 4;
  string domain_context_used = 5;
  map<string, int32> scenario_counts = 6;
}

// ============ Health ============

message HealthCheckRequest {}

message HealthCheckResponse {
  string status = 1;
  map<string, string> components = 2;
}
```

Copy the Test Data Agent proto for client use:
```bash
# Copy from test-data-agent repo or create reference
cp ../test-data-agent/service/protos/test_data.proto ./service/protos/
```

Generate Python code:
```bash
cd service
mkdir -p src/ecommerce_agent/proto
python -m grpc_tools.protoc \
  -I./protos \
  --python_out=./src/ecommerce_agent/proto \
  --grpc_python_out=./src/ecommerce_agent/proto \
  ./protos/ecommerce_domain.proto \
  ./protos/test_data.proto
```

Create src/ecommerce_agent/proto/__init__.py:
```python
"""Generated protobuf code."""
```

Acceptance Criteria:
- [ ] Proto file compiles without errors
- [ ] Python code is generated
- [ ] Both ecommerce_domain and test_data protos are available
```

---

### Task 1.5: Create gRPC Server Skeleton

```
Create the gRPC server with stub implementations.

Create src/ecommerce_agent/server/__init__.py:
```python
"""Server modules."""
```

Create src/ecommerce_agent/server/grpc_server.py:

```python
import grpc
from concurrent import futures
from typing import Any

from ecommerce_agent.proto import ecommerce_domain_pb2 as pb2
from ecommerce_agent.proto import ecommerce_domain_pb2_grpc as pb2_grpc
from ecommerce_agent.utils.logging import get_logger, bind_context

logger = get_logger(__name__)


class EcommerceDomainServicer(pb2_grpc.EcommerceDomainServiceServicer):
    """gRPC service implementation for eCommerce Domain Agent."""
    
    def __init__(self):
        """Initialize the servicer with dependencies."""
        # Dependencies will be injected later
        pass
    
    async def GetDomainContext(
        self,
        request: pb2.DomainContextRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.DomainContextResponse:
        """Get domain context for test generation."""
        bind_context(request_id=request.request_id, method="GetDomainContext")
        logger.info("Getting domain context", entity=request.entity, workflow=request.workflow)
        
        # TODO: Implement
        return pb2.DomainContextResponse(
            request_id=request.request_id,
            context="Domain context placeholder",
        )
    
    async def QueryKnowledge(
        self,
        request: pb2.KnowledgeRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.KnowledgeResponse:
        """Query domain knowledge."""
        bind_context(request_id=request.request_id, method="QueryKnowledge")
        logger.info("Querying knowledge", query=request.query)
        
        # TODO: Implement
        return pb2.KnowledgeResponse(
            request_id=request.request_id,
            items=[],
            summary="Knowledge query placeholder",
        )
    
    async def GetEntity(
        self,
        request: pb2.EntityRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.EntityResponse:
        """Get entity details."""
        logger.info("Getting entity", entity=request.entity_name)
        
        # TODO: Implement
        return pb2.EntityResponse(
            entity=pb2.Entity(
                name=request.entity_name,
                description="Entity placeholder",
            )
        )
    
    async def GetWorkflow(
        self,
        request: pb2.WorkflowRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.WorkflowResponse:
        """Get workflow details."""
        logger.info("Getting workflow", workflow=request.workflow_name)
        
        # TODO: Implement
        return pb2.WorkflowResponse(
            workflow=pb2.Workflow(
                name=request.workflow_name,
                description="Workflow placeholder",
            )
        )
    
    async def ListEntities(
        self,
        request: pb2.ListEntitiesRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.ListEntitiesResponse:
        """List all entities."""
        logger.info("Listing entities", category=request.category)
        
        # TODO: Implement
        return pb2.ListEntitiesResponse(entities=[])
    
    async def ListWorkflows(
        self,
        request: pb2.ListWorkflowsRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.ListWorkflowsResponse:
        """List all workflows."""
        logger.info("Listing workflows")
        
        # TODO: Implement
        return pb2.ListWorkflowsResponse(workflows=[])
    
    async def GetEdgeCases(
        self,
        request: pb2.EdgeCasesRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.EdgeCasesResponse:
        """Get edge cases."""
        logger.info("Getting edge cases", entity=request.entity, workflow=request.workflow)
        
        # TODO: Implement
        return pb2.EdgeCasesResponse(edge_cases=[])
    
    async def GenerateTestData(
        self,
        request: pb2.GenerateTestDataRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.GenerateTestDataResponse:
        """Generate test data via Test Data Agent."""
        bind_context(request_id=request.request_id, method="GenerateTestData")
        logger.info("Generating test data", entity=request.entity, count=request.count)
        
        # TODO: Implement with Test Data Agent client
        return pb2.GenerateTestDataResponse(
            request_id=request.request_id,
            success=False,
            error="Not implemented yet",
        )
    
    async def HealthCheck(
        self,
        request: pb2.HealthCheckRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.HealthCheckResponse:
        """Health check."""
        return pb2.HealthCheckResponse(
            status="healthy",
            components={"grpc": "healthy"},
        )


async def create_server(port: int) -> grpc.aio.Server:
    """Create and configure the gRPC server."""
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ("grpc.max_receive_message_length", 50 * 1024 * 1024),  # 50MB
            ("grpc.max_send_message_length", 50 * 1024 * 1024),
        ],
    )
    
    servicer = EcommerceDomainServicer()
    pb2_grpc.add_EcommerceDomainServiceServicer_to_server(servicer, server)
    
    server.add_insecure_port(f"[::]:{port}")
    
    logger.info("gRPC server created", port=port)
    return server
```

Acceptance Criteria:
- [ ] Server compiles without errors
- [ ] All RPC methods have stub implementations
- [ ] Health check returns healthy
- [ ] Logging is integrated
```

---

### Task 1.6: Create Health HTTP Endpoints

```
Create FastAPI health endpoints.

Create src/ecommerce_agent/server/health.py:

```python
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ecommerce_agent.config import get_settings
from ecommerce_agent.utils.logging import get_logger

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
    settings = get_settings()
    
    # Track component health
    component_status: dict[str, str] = {
        "grpc": "unknown",
        "weaviate": "unknown",
        "test_data_agent": "unknown",
    }
    
    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        """Basic health check."""
        overall = "healthy" if all(
            s == "healthy" for s in component_status.values()
        ) else "degraded"
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
    
    return app
```

Acceptance Criteria:
- [ ] /health returns overall status
- [ ] /health/live returns 200
- [ ] /health/ready returns readiness checks
- [ ] Component status is trackable
```

---

### Task 1.7: Create Main Entry Point

```
Create the main entry point that starts both gRPC and HTTP servers.

Create src/ecommerce_agent/main.py:

```python
import asyncio
import signal
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn

from ecommerce_agent.config import get_settings
from ecommerce_agent.server.grpc_server import create_server
from ecommerce_agent.server.health import create_health_app
from ecommerce_agent.utils.logging import setup_logging, get_logger

logger = get_logger(__name__)


async def run_grpc_server(port: int) -> None:
    """Run the gRPC server."""
    server = await create_server(port)
    await server.start()
    logger.info("gRPC server started", port=port)
    
    # Wait for termination
    await server.wait_for_termination()


async def run_http_server(port: int) -> None:
    """Run the HTTP server for health endpoints."""
    app = create_health_app()
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=port,
        log_level="warning",
    )
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    """Main entry point."""
    setup_logging()
    settings = get_settings()
    
    logger.info(
        "Starting eCommerce Domain Agent",
        service=settings.service_name,
        grpc_port=settings.grpc_port,
        http_port=settings.http_port,
    )
    
    # Handle shutdown signals
    shutdown_event = asyncio.Event()
    
    def handle_shutdown(sig: signal.Signals) -> None:
        logger.info("Received shutdown signal", signal=sig.name)
        shutdown_event.set()
    
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, handle_shutdown, sig)
    
    # Run servers concurrently
    try:
        await asyncio.gather(
            run_grpc_server(settings.grpc_port),
            run_http_server(settings.http_port),
        )
    except asyncio.CancelledError:
        logger.info("Servers cancelled")
    
    logger.info("eCommerce Domain Agent stopped")


if __name__ == "__main__":
    asyncio.run(main())
```

Acceptance Criteria:
- [ ] Running `python -m ecommerce_agent.main` starts both servers
- [ ] gRPC server listens on configured port
- [ ] HTTP server listens on configured port
- [ ] Graceful shutdown on SIGTERM/SIGINT
```

---

### Task 1.8: Create Dockerfile

```
Create the Dockerfile for the service.

Create service/Dockerfile:

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir build && \
    pip install --no-cache-dir .

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/
COPY protos/ ./protos/

# Set ownership
RUN chown -R appuser:appuser /app

USER appuser

# Expose ports
EXPOSE 9002 8082

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8082/health/live')" || exit 1

# Run
CMD ["python", "-m", "ecommerce_agent.main"]
```

Create docker-compose.yml in root:

```yaml
version: '3.8'

services:
  service:
    build: ./service
    ports:
      - "9002:9002"
      - "8082:8082"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - WEAVIATE_URL=http://weaviate:8080
      - TEST_DATA_AGENT_HOST=test-data-agent
      - TEST_DATA_AGENT_PORT=9001
      - LOG_LEVEL=DEBUG
    depends_on:
      - weaviate
    networks:
      - qa-platform

  weaviate:
    image: semitechnologies/weaviate:latest
    ports:
      - "8081:8080"
    environment:
      - QUERY_DEFAULTS_LIMIT=25
      - AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true
      - PERSISTENCE_DATA_PATH=/var/lib/weaviate
    volumes:
      - weaviate_data:/var/lib/weaviate
    networks:
      - qa-platform

networks:
  qa-platform:
    name: qa-platform
    driver: bridge

volumes:
  weaviate_data:
```

Acceptance Criteria:
- [ ] docker build -t ecommerce-agent ./service succeeds
- [ ] docker-compose up starts service and weaviate
- [ ] Health check passes
- [ ] Service connects to weaviate
```

---

### Task 1.9: Write Phase 1 Tests

```
Write tests for Phase 1 components.

Create tests/conftest.py:

```python
import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    settings = MagicMock()
    settings.service_name = "test-service"
    settings.grpc_port = 9002
    settings.http_port = 8082
    settings.log_level = "DEBUG"
    settings.anthropic_api_key = "test-key"
    settings.weaviate_url = "http://localhost:8080"
    settings.test_data_agent_host = "localhost"
    settings.test_data_agent_port = 9001
    return settings
```

Create tests/unit/test_config.py:

```python
import os
import pytest
from unittest.mock import patch

from ecommerce_agent.config import Settings, get_settings


class TestSettings:
    def test_default_values(self):
        """Test default configuration values."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            settings = Settings()
            assert settings.service_name == "ecommerce-domain-agent"
            assert settings.grpc_port == 9002
            assert settings.http_port == 8082
    
    def test_required_api_key(self):
        """Test that API key is required."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(Exception):
                Settings()
    
    def test_get_settings_caching(self):
        """Test that get_settings returns cached instance."""
        get_settings.cache_clear()
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            s1 = get_settings()
            s2 = get_settings()
            assert s1 is s2
```

Create tests/unit/test_health.py:

```python
import pytest
from fastapi.testclient import TestClient

from ecommerce_agent.server.health import create_health_app


@pytest.fixture
def client():
    app = create_health_app()
    return TestClient(app)


class TestHealthEndpoints:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "components" in data
    
    def test_liveness(self, client):
        response = client.get("/health/live")
        assert response.status_code == 200
    
    def test_readiness(self, client):
        response = client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert "ready" in data
        assert "checks" in data
```

Acceptance Criteria:
- [ ] pytest runs without errors
- [ ] Config tests pass
- [ ] Health endpoint tests pass
- [ ] At least 80% coverage for Phase 1 code
```

---

## Phase 2: Domain Model

### Task 2.1: Create Entity Definitions

```
Create the eCommerce entity definitions.

Create src/ecommerce_agent/domain/__init__.py:
```python
"""Domain model modules."""
```

Create src/ecommerce_agent/domain/entities.py:

```python
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EntityField:
    """Definition of an entity field."""
    name: str
    type: str
    description: str
    required: bool = True
    validations: list[str] = field(default_factory=list)
    example: str = ""


@dataclass
class EntityRelationship:
    """Relationship between entities."""
    target: str
    type: str  # belongs_to, has_many, has_one, many_to_many
    description: str = ""
    required: bool = False


@dataclass
class EntityDefinition:
    """Complete entity definition."""
    name: str
    description: str
    category: str  # core, transactional, financial, catalog, etc.
    fields: list[EntityField]
    relationships: list[EntityRelationship] = field(default_factory=list)
    business_rules: list[str] = field(default_factory=list)
    edge_cases: list[str] = field(default_factory=list)
    test_scenarios: list[str] = field(default_factory=list)


# Entity Definitions
ENTITIES: dict[str, EntityDefinition] = {
    "cart": EntityDefinition(
        name="cart",
        description="Shopping cart containing items before checkout",
        category="transactional",
        fields=[
            EntityField("cart_id", "string", "Unique cart identifier", example="CRT-2025-1234567"),
            EntityField("customer_id", "string", "Customer who owns the cart", example="USR-1234567"),
            EntityField("items", "array", "List of cart items"),
            EntityField("subtotal", "decimal", "Sum of item prices before tax", example="149.99"),
            EntityField("tax", "decimal", "Calculated tax amount", example="12.37"),
            EntityField("total", "decimal", "Final cart total including tax", example="162.36"),
            EntityField("currency", "string", "Currency code", example="USD"),
            EntityField("status", "enum", "Cart status: active, abandoned, converted", example="active"),
            EntityField("created_at", "datetime", "Cart creation timestamp"),
            EntityField("updated_at", "datetime", "Last modification timestamp"),
        ],
        relationships=[
            EntityRelationship("customer", "belongs_to", "Customer who owns this cart", required=True),
            EntityRelationship("cart_item", "has_many", "Items in the cart"),
            EntityRelationship("order", "converts_to", "Order created from this cart"),
        ],
        business_rules=[
            "BR001: Cart must have at least 1 item at checkout",
            "BR002: Cart total must be >= $1.00 for payment",
            "BR003: Item quantity must be 1-99",
        ],
        edge_cases=[
            "Concurrent cart updates from multiple sessions",
            "Cart with out-of-stock items",
            "Cart with expired promotions",
            "Cart exceeding max item limit",
        ],
        test_scenarios=[
            "happy_path", "high_value", "single_item", "max_items",
            "abandoned", "multi_currency",
        ],
    ),
    
    "order": EntityDefinition(
        name="order",
        description="Completed purchase after checkout",
        category="transactional",
        fields=[
            EntityField("order_id", "string", "Unique order identifier", example="ORD-2025-1234567"),
            EntityField("customer_id", "string", "Customer who placed the order"),
            EntityField("cart_id", "string", "Source cart ID"),
            EntityField("items", "array", "Ordered items"),
            EntityField("subtotal", "decimal", "Items total before tax"),
            EntityField("tax", "decimal", "Tax amount"),
            EntityField("shipping", "decimal", "Shipping cost"),
            EntityField("total", "decimal", "Final order total"),
            EntityField("status", "enum", "Order status: pending, confirmed, shipped, delivered, cancelled"),
            EntityField("payment_status", "enum", "Payment status: pending, paid, failed, refunded"),
            EntityField("shipping_address", "object", "Delivery address"),
            EntityField("billing_address", "object", "Billing address"),
            EntityField("placed_at", "datetime", "Order placement time"),
        ],
        relationships=[
            EntityRelationship("customer", "belongs_to", required=True),
            EntityRelationship("cart", "created_from"),
            EntityRelationship("payment", "has_many"),
            EntityRelationship("shipment", "has_many"),
            EntityRelationship("return", "has_many"),
        ],
        business_rules=[
            "BR004: Order total must match payment amount",
            "BR005: Shipping address required for physical items",
            "BR006: Cannot cancel shipped orders",
        ],
        edge_cases=[
            "Order with partial inventory availability",
            "Order during price change",
            "Split shipment order",
            "Order with mixed digital and physical items",
        ],
        test_scenarios=[
            "happy_path", "high_value", "express_shipping", "international",
            "partial_fulfillment", "cancelled",
        ],
    ),
    
    "payment": EntityDefinition(
        name="payment",
        description="Payment transaction for an order",
        category="financial",
        fields=[
            EntityField("payment_id", "string", "Unique payment identifier"),
            EntityField("order_id", "string", "Associated order"),
            EntityField("amount", "decimal", "Payment amount"),
            EntityField("currency", "string", "Currency code"),
            EntityField("method", "enum", "Payment method: card, paypal, apple_pay, etc."),
            EntityField("status", "enum", "Status: pending, authorized, captured, failed, refunded"),
            EntityField("gateway_reference", "string", "Payment gateway reference ID"),
            EntityField("card_last_four", "string", "Last 4 digits of card", required=False),
            EntityField("processor_response", "string", "Gateway response code"),
            EntityField("created_at", "datetime", "Payment initiation time"),
            EntityField("completed_at", "datetime", "Payment completion time", required=False),
        ],
        relationships=[
            EntityRelationship("order", "belongs_to", required=True),
            EntityRelationship("refund", "has_many"),
        ],
        business_rules=[
            "BR007: Payment amount must match order total",
            "BR008: Card expiry must be future date",
            "BR009: CVV required for card payments",
        ],
        edge_cases=[
            "Payment timeout after authorization",
            "Duplicate payment submission",
            "Payment with expired card",
            "3D Secure authentication failure",
        ],
        test_scenarios=[
            "card_success", "card_declined", "paypal_success", "apple_pay",
            "insufficient_funds", "fraud_detected",
        ],
    ),
    
    "customer": EntityDefinition(
        name="customer",
        description="Registered or guest customer",
        category="core",
        fields=[
            EntityField("customer_id", "string", "Unique customer identifier"),
            EntityField("email", "email", "Customer email address"),
            EntityField("first_name", "string", "First name"),
            EntityField("last_name", "string", "Last name"),
            EntityField("phone", "phone", "Phone number", required=False),
            EntityField("type", "enum", "Customer type: registered, guest"),
            EntityField("status", "enum", "Account status: active, suspended, deleted"),
            EntityField("created_at", "datetime", "Registration time"),
            EntityField("last_login", "datetime", "Last login time", required=False),
        ],
        relationships=[
            EntityRelationship("address", "has_many"),
            EntityRelationship("cart", "has_many"),
            EntityRelationship("order", "has_many"),
            EntityRelationship("review", "has_many"),
        ],
        business_rules=[
            "BR010: Email must be unique for registered customers",
            "BR011: Password required for registered customers",
        ],
        edge_cases=[
            "Guest checkout conversion to registered",
            "Customer with multiple addresses",
            "Merged duplicate accounts",
        ],
        test_scenarios=[
            "registered_new", "registered_returning", "guest", "vip",
        ],
    ),
    
    "product": EntityDefinition(
        name="product",
        description="Sellable product in catalog",
        category="catalog",
        fields=[
            EntityField("product_id", "string", "Unique product identifier"),
            EntityField("sku", "string", "Stock keeping unit"),
            EntityField("name", "string", "Product name"),
            EntityField("description", "string", "Product description"),
            EntityField("price", "decimal", "Current price"),
            EntityField("compare_at_price", "decimal", "Original price for sale items", required=False),
            EntityField("category", "string", "Product category"),
            EntityField("inventory_quantity", "integer", "Available stock"),
            EntityField("status", "enum", "Status: active, draft, archived"),
            EntityField("attributes", "object", "Product attributes (size, color, etc.)"),
        ],
        relationships=[
            EntityRelationship("category", "belongs_to"),
            EntityRelationship("review", "has_many"),
            EntityRelationship("cart_item", "has_many"),
        ],
        business_rules=[
            "BR012: Price must be positive",
            "BR013: SKU must be unique",
            "BR014: Cannot sell products with 0 inventory",
        ],
        edge_cases=[
            "Product with negative inventory (oversell)",
            "Product with pending price update",
            "Discontinued product in active carts",
        ],
        test_scenarios=[
            "in_stock", "low_stock", "out_of_stock", "on_sale", "new_arrival",
        ],
    ),
    
    "shipment": EntityDefinition(
        name="shipment",
        description="Shipment of order items",
        category="fulfillment",
        fields=[
            EntityField("shipment_id", "string", "Unique shipment identifier"),
            EntityField("order_id", "string", "Associated order"),
            EntityField("tracking_number", "string", "Carrier tracking number"),
            EntityField("carrier", "string", "Shipping carrier"),
            EntityField("status", "enum", "Status: pending, shipped, in_transit, delivered, returned"),
            EntityField("items", "array", "Items in this shipment"),
            EntityField("shipped_at", "datetime", "Ship date", required=False),
            EntityField("delivered_at", "datetime", "Delivery date", required=False),
            EntityField("address", "object", "Delivery address"),
        ],
        relationships=[
            EntityRelationship("order", "belongs_to", required=True),
        ],
        business_rules=[
            "BR015: Tracking number required when shipped",
            "BR016: Cannot deliver before shipping",
        ],
        edge_cases=[
            "Split shipment from single order",
            "Failed delivery attempt",
            "Address change after shipping",
        ],
        test_scenarios=[
            "standard", "express", "international", "delayed", "returned_to_sender",
        ],
    ),
    
    "return": EntityDefinition(
        name="return",
        description="Return request for order items",
        category="post_purchase",
        fields=[
            EntityField("return_id", "string", "Unique return identifier"),
            EntityField("order_id", "string", "Original order"),
            EntityField("items", "array", "Items being returned"),
            EntityField("reason", "enum", "Return reason: defective, wrong_item, not_as_described, etc."),
            EntityField("status", "enum", "Status: requested, approved, received, processed, denied"),
            EntityField("refund_amount", "decimal", "Amount to refund"),
            EntityField("requested_at", "datetime", "Return request time"),
            EntityField("processed_at", "datetime", "Processing completion time", required=False),
        ],
        relationships=[
            EntityRelationship("order", "belongs_to", required=True),
            EntityRelationship("refund", "has_one"),
        ],
        business_rules=[
            "BR017: Return must be within 30 days of delivery",
            "BR018: Item must be in original condition for full refund",
        ],
        edge_cases=[
            "Return of partial order",
            "Return after return window",
            "Return with missing items",
        ],
        test_scenarios=[
            "full_refund", "partial_refund", "exchange", "denied",
        ],
    ),
    
    "review": EntityDefinition(
        name="review",
        description="Customer product review",
        category="engagement",
        fields=[
            EntityField("review_id", "string", "Unique review identifier"),
            EntityField("product_id", "string", "Reviewed product"),
            EntityField("customer_id", "string", "Reviewer"),
            EntityField("order_id", "string", "Associated order", required=False),
            EntityField("rating", "integer", "Rating 1-5"),
            EntityField("title", "string", "Review title"),
            EntityField("body", "string", "Review text"),
            EntityField("status", "enum", "Status: pending, approved, rejected"),
            EntityField("verified_purchase", "boolean", "Is verified purchase"),
            EntityField("created_at", "datetime", "Review submission time"),
        ],
        relationships=[
            EntityRelationship("product", "belongs_to", required=True),
            EntityRelationship("customer", "belongs_to", required=True),
            EntityRelationship("order", "belongs_to"),
        ],
        business_rules=[
            "BR019: Rating must be 1-5",
            "BR020: One review per customer per product",
            "BR021: Verified purchase requires matching order",
        ],
        edge_cases=[
            "Review for returned product",
            "Review with profanity",
            "Duplicate review attempt",
        ],
        test_scenarios=[
            "positive", "negative", "detailed", "minimal", "with_photos",
        ],
    ),
}


def get_entity(name: str) -> EntityDefinition | None:
    """Get entity definition by name."""
    return ENTITIES.get(name.lower())


def list_entities(category: str | None = None) -> list[EntityDefinition]:
    """List all entities, optionally filtered by category."""
    entities = list(ENTITIES.values())
    if category:
        entities = [e for e in entities if e.category == category]
    return entities


def get_entity_categories() -> list[str]:
    """Get all unique entity categories."""
    return list(set(e.category for e in ENTITIES.values()))
```

Acceptance Criteria:
- [ ] All eCommerce entities defined
- [ ] Each entity has fields, relationships, rules, edge cases
- [ ] get_entity() returns correct entity
- [ ] list_entities() filters by category
```

---

### Task 2.2: Create Workflow Definitions

```
Create the eCommerce workflow definitions.

Create src/ecommerce_agent/domain/workflows.py:

```python
from dataclasses import dataclass, field


@dataclass
class WorkflowStep:
    """A single step in a workflow."""
    order: int
    name: str
    description: str
    entity: str
    action: str  # create, update, validate, delete, notify
    validations: list[str] = field(default_factory=list)
    possible_outcomes: list[str] = field(default_factory=list)


@dataclass
class WorkflowDefinition:
    """Complete workflow definition."""
    name: str
    description: str
    steps: list[WorkflowStep]
    involved_entities: list[str]
    business_rules: list[str] = field(default_factory=list)
    edge_cases: list[str] = field(default_factory=list)
    test_scenarios: list[str] = field(default_factory=list)


WORKFLOWS: dict[str, WorkflowDefinition] = {
    "checkout": WorkflowDefinition(
        name="checkout",
        description="Complete purchase flow from cart to order confirmation",
        steps=[
            WorkflowStep(
                order=1,
                name="cart_validation",
                description="Validate cart contents and availability",
                entity="cart",
                action="validate",
                validations=["items_exist", "items_in_stock", "prices_current"],
                possible_outcomes=["valid", "items_unavailable", "price_changed"],
            ),
            WorkflowStep(
                order=2,
                name="inventory_reservation",
                description="Reserve inventory for cart items",
                entity="product",
                action="update",
                validations=["sufficient_stock"],
                possible_outcomes=["reserved", "insufficient_stock"],
            ),
            WorkflowStep(
                order=3,
                name="pricing_calculation",
                description="Calculate final pricing with tax and shipping",
                entity="cart",
                action="update",
                validations=["tax_calculated", "shipping_calculated"],
                possible_outcomes=["calculated", "tax_error", "shipping_unavailable"],
            ),
            WorkflowStep(
                order=4,
                name="shipping_selection",
                description="Select shipping method and address",
                entity="shipment",
                action="create",
                validations=["address_valid", "method_available"],
                possible_outcomes=["selected", "address_invalid", "method_unavailable"],
            ),
            WorkflowStep(
                order=5,
                name="payment_processing",
                description="Process payment through gateway",
                entity="payment",
                action="create",
                validations=["card_valid", "amount_matches", "fraud_check"],
                possible_outcomes=["authorized", "declined", "fraud_detected", "timeout"],
            ),
            WorkflowStep(
                order=6,
                name="order_creation",
                description="Create order from cart and payment",
                entity="order",
                action="create",
                validations=["payment_authorized", "inventory_reserved"],
                possible_outcomes=["created", "creation_failed"],
            ),
            WorkflowStep(
                order=7,
                name="confirmation",
                description="Send order confirmation to customer",
                entity="order",
                action="notify",
                validations=["email_valid"],
                possible_outcomes=["sent", "delivery_failed"],
            ),
        ],
        involved_entities=["cart", "product", "customer", "payment", "order", "shipment"],
        business_rules=[
            "Cart must have at least 1 item",
            "All items must be in stock",
            "Payment must be authorized before order creation",
            "Inventory reservation expires after 15 minutes",
        ],
        edge_cases=[
            "Concurrent checkout for same cart",
            "Price change during checkout",
            "Inventory depleted during checkout",
            "Payment timeout after authorization",
            "Network failure after payment",
        ],
        test_scenarios=[
            "happy_path", "payment_declined", "inventory_conflict",
            "address_validation_failure", "express_checkout",
        ],
    ),
    
    "return_flow": WorkflowDefinition(
        name="return_flow",
        description="Customer return and refund process",
        steps=[
            WorkflowStep(
                order=1,
                name="return_request",
                description="Customer initiates return request",
                entity="return",
                action="create",
                validations=["within_return_window", "item_returnable"],
                possible_outcomes=["created", "outside_window", "non_returnable"],
            ),
            WorkflowStep(
                order=2,
                name="return_approval",
                description="Review and approve return request",
                entity="return",
                action="update",
                validations=["reason_valid", "not_fraudulent"],
                possible_outcomes=["approved", "denied", "pending_review"],
            ),
            WorkflowStep(
                order=3,
                name="return_shipment",
                description="Generate return shipping label",
                entity="shipment",
                action="create",
                validations=["address_valid"],
                possible_outcomes=["label_generated", "generation_failed"],
            ),
            WorkflowStep(
                order=4,
                name="item_receipt",
                description="Receive and inspect returned item",
                entity="return",
                action="update",
                validations=["item_received", "condition_acceptable"],
                possible_outcomes=["accepted", "rejected", "partial_credit"],
            ),
            WorkflowStep(
                order=5,
                name="inventory_update",
                description="Return item to inventory if applicable",
                entity="product",
                action="update",
                validations=["item_sellable"],
                possible_outcomes=["restocked", "written_off"],
            ),
            WorkflowStep(
                order=6,
                name="refund_processing",
                description="Process refund to original payment method",
                entity="payment",
                action="create",
                validations=["amount_calculated", "method_available"],
                possible_outcomes=["refunded", "refund_failed"],
            ),
        ],
        involved_entities=["order", "return", "shipment", "product", "payment"],
        business_rules=[
            "Returns must be within 30 days of delivery",
            "Items must be in original condition",
            "Refund to original payment method",
        ],
        edge_cases=[
            "Return of partial order",
            "Return with damaged item",
            "Refund to expired card",
            "Return after return window with exception",
        ],
        test_scenarios=[
            "full_refund", "partial_refund", "denied_return",
            "exchange_request", "store_credit",
        ],
    ),
    
    "cart_abandonment": WorkflowDefinition(
        name="cart_abandonment",
        description="Abandoned cart recovery flow",
        steps=[
            WorkflowStep(
                order=1,
                name="abandonment_detection",
                description="Detect cart abandoned after threshold time",
                entity="cart",
                action="validate",
                validations=["inactive_duration", "has_items"],
                possible_outcomes=["abandoned", "still_active", "empty"],
            ),
            WorkflowStep(
                order=2,
                name="recovery_email",
                description="Send cart recovery email",
                entity="customer",
                action="notify",
                validations=["email_subscribed", "not_recently_contacted"],
                possible_outcomes=["sent", "unsubscribed", "too_recent"],
            ),
            WorkflowStep(
                order=3,
                name="incentive_offer",
                description="Optionally apply discount incentive",
                entity="cart",
                action="update",
                validations=["eligible_for_discount"],
                possible_outcomes=["discount_applied", "not_eligible"],
            ),
        ],
        involved_entities=["cart", "customer", "promotion"],
        business_rules=[
            "Cart is abandoned after 1 hour of inactivity",
            "Maximum 3 recovery emails per cart",
            "Discount incentive after 2nd email",
        ],
        edge_cases=[
            "Cart with out-of-stock items",
            "Customer unsubscribed from emails",
            "Multiple abandoned carts same customer",
        ],
        test_scenarios=[
            "first_reminder", "with_discount", "recovered", "expired",
        ],
    ),
    
    "inventory_sync": WorkflowDefinition(
        name="inventory_sync",
        description="Inventory synchronization with warehouse",
        steps=[
            WorkflowStep(
                order=1,
                name="fetch_warehouse_levels",
                description="Get current inventory from warehouse system",
                entity="product",
                action="validate",
                validations=["warehouse_connected"],
                possible_outcomes=["fetched", "connection_failed"],
            ),
            WorkflowStep(
                order=2,
                name="compare_levels",
                description="Compare warehouse vs system inventory",
                entity="product",
                action="validate",
                validations=["levels_match"],
                possible_outcomes=["in_sync", "discrepancy_found"],
            ),
            WorkflowStep(
                order=3,
                name="update_inventory",
                description="Update system inventory to match warehouse",
                entity="product",
                action="update",
                validations=["adjustment_within_threshold"],
                possible_outcomes=["updated", "manual_review_required"],
            ),
        ],
        involved_entities=["product"],
        business_rules=[
            "Sync runs every 15 minutes",
            "Discrepancies > 10% require manual review",
            "Never increase inventory during active sale",
        ],
        edge_cases=[
            "Warehouse system offline",
            "Large discrepancy detected",
            "Sync during high-traffic period",
        ],
        test_scenarios=[
            "normal_sync", "discrepancy_small", "discrepancy_large",
            "warehouse_offline",
        ],
    ),
}


def get_workflow(name: str) -> WorkflowDefinition | None:
    """Get workflow definition by name."""
    return WORKFLOWS.get(name.lower())


def list_workflows() -> list[WorkflowDefinition]:
    """List all workflows."""
    return list(WORKFLOWS.values())


def get_workflows_for_entity(entity: str) -> list[WorkflowDefinition]:
    """Get all workflows involving a specific entity."""
    return [w for w in WORKFLOWS.values() if entity in w.involved_entities]
```

Acceptance Criteria:
- [ ] All major eCommerce workflows defined
- [ ] Each workflow has steps with validations and outcomes
- [ ] get_workflow() returns correct workflow
- [ ] get_workflows_for_entity() filters correctly
```

---

### Task 2.3: Create Business Rules

```
Create the business rules definitions.

Create src/ecommerce_agent/domain/business_rules.py:

```python
from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class BusinessRule:
    """A business rule definition."""
    id: str
    name: str
    entity: str
    description: str
    condition: str  # When this rule applies
    constraint: str  # What the rule enforces
    severity: Severity
    validation_logic: str = ""  # Pseudo-code or description of validation


BUSINESS_RULES: list[BusinessRule] = [
    # Cart Rules
    BusinessRule(
        id="BR001",
        name="cart_item_quantity_limit",
        entity="cart_item",
        description="Limit quantity per item in cart",
        condition="Always",
        constraint="Quantity per item must be between 1 and 99",
        severity=Severity.ERROR,
        validation_logic="1 <= item.quantity <= 99",
    ),
    BusinessRule(
        id="BR002",
        name="cart_total_minimum",
        entity="cart",
        description="Minimum cart total for checkout",
        condition="At checkout",
        constraint="Cart total must be >= $1.00 for payment processing",
        severity=Severity.ERROR,
        validation_logic="cart.total >= 1.00",
    ),
    BusinessRule(
        id="BR003",
        name="cart_item_limit",
        entity="cart",
        description="Maximum items in cart",
        condition="When adding items",
        constraint="Cart cannot exceed 100 unique items",
        severity=Severity.ERROR,
        validation_logic="len(cart.items) <= 100",
    ),
    
    # Order Rules
    BusinessRule(
        id="BR004",
        name="payment_amount_match",
        entity="payment",
        description="Payment amount must match order",
        condition="At payment creation",
        constraint="Payment amount must match order total exactly",
        severity=Severity.ERROR,
        validation_logic="payment.amount == order.total",
    ),
    BusinessRule(
        id="BR005",
        name="shipping_address_required",
        entity="order",
        description="Shipping address required for physical items",
        condition="At order creation",
        constraint="Orders with physical items must have shipping address",
        severity=Severity.ERROR,
        validation_logic="has_physical_items implies shipping_address is not None",
    ),
    BusinessRule(
        id="BR006",
        name="cancel_before_ship",
        entity="order",
        description="Cannot cancel shipped orders",
        condition="At cancellation request",
        constraint="Order can only be cancelled before shipping",
        severity=Severity.ERROR,
        validation_logic="order.status not in ['shipped', 'delivered']",
    ),
    
    # Payment Rules
    BusinessRule(
        id="BR007",
        name="card_expiry_future",
        entity="payment",
        description="Card must not be expired",
        condition="At payment with card",
        constraint="Card expiry must be in the future",
        severity=Severity.ERROR,
        validation_logic="card.expiry_date > current_date",
    ),
    BusinessRule(
        id="BR008",
        name="cvv_required",
        entity="payment",
        description="CVV required for card payments",
        condition="At payment with card",
        constraint="CVV must be provided for card transactions",
        severity=Severity.ERROR,
        validation_logic="card.cvv is not None and len(card.cvv) in [3, 4]",
    ),
    
    # Return Rules
    BusinessRule(
        id="BR009",
        name="return_window",
        entity="return",
        description="Return within allowed window",
        condition="At return request",
        constraint="Return must be within 30 days of delivery",
        severity=Severity.ERROR,
        validation_logic="days_since_delivery <= 30",
    ),
    BusinessRule(
        id="BR010",
        name="return_condition",
        entity="return",
        description="Item condition for full refund",
        condition="At return processing",
        constraint="Item must be in original condition for full refund",
        severity=Severity.WARNING,
        validation_logic="item.condition == 'original' for full_refund",
    ),
    
    # Customer Rules
    BusinessRule(
        id="BR011",
        name="unique_email",
        entity="customer",
        description="Unique email for registered customers",
        condition="At registration",
        constraint="Email must be unique for registered customers",
        severity=Severity.ERROR,
        validation_logic="not exists(customer where email == new_email and type == 'registered')",
    ),
    
    # Product Rules
    BusinessRule(
        id="BR012",
        name="positive_price",
        entity="product",
        description="Price must be positive",
        condition="Always",
        constraint="Product price must be greater than zero",
        severity=Severity.ERROR,
        validation_logic="product.price > 0",
    ),
    BusinessRule(
        id="BR013",
        name="unique_sku",
        entity="product",
        description="SKU must be unique",
        condition="At product creation/update",
        constraint="SKU must be unique across all products",
        severity=Severity.ERROR,
        validation_logic="not exists(product where sku == new_sku)",
    ),
    BusinessRule(
        id="BR014",
        name="stock_required_for_sale",
        entity="product",
        description="Cannot sell out-of-stock items",
        condition="At add to cart",
        constraint="Product must have positive inventory to be purchasable",
        severity=Severity.ERROR,
        validation_logic="product.inventory_quantity > 0",
    ),
    
    # Review Rules
    BusinessRule(
        id="BR015",
        name="rating_range",
        entity="review",
        description="Rating must be 1-5",
        condition="At review submission",
        constraint="Rating must be an integer between 1 and 5",
        severity=Severity.ERROR,
        validation_logic="1 <= review.rating <= 5",
    ),
    BusinessRule(
        id="BR016",
        name="one_review_per_product",
        entity="review",
        description="One review per customer per product",
        condition="At review submission",
        constraint="Customer can only submit one review per product",
        severity=Severity.ERROR,
        validation_logic="not exists(review where customer_id == customer and product_id == product)",
    ),
]


def get_rules_for_entity(entity: str) -> list[BusinessRule]:
    """Get all rules for a specific entity."""
    return [r for r in BUSINESS_RULES if r.entity == entity]


def get_rules_by_severity(severity: Severity) -> list[BusinessRule]:
    """Get all rules with a specific severity."""
    return [r for r in BUSINESS_RULES if r.severity == severity]


def get_rule_by_id(rule_id: str) -> BusinessRule | None:
    """Get a specific rule by ID."""
    for rule in BUSINESS_RULES:
        if rule.id == rule_id:
            return rule
    return None


def get_all_rules() -> list[BusinessRule]:
    """Get all business rules."""
    return BUSINESS_RULES
```

Acceptance Criteria:
- [ ] All business rules defined with unique IDs
- [ ] Rules have condition, constraint, and severity
- [ ] get_rules_for_entity() filters correctly
- [ ] Rules cover all major entities
```

---

### Task 2.4: Create Edge Cases

```
Create the edge case definitions.

Create src/ecommerce_agent/domain/edge_cases.py:

```python
from dataclasses import dataclass, field
from enum import Enum


class EdgeCaseCategory(str, Enum):
    CONCURRENCY = "concurrency"
    NETWORK = "network"
    BOUNDARY = "boundary"
    DATA = "data"
    TIMING = "timing"
    SECURITY = "security"
    INTEGRATION = "integration"


class EdgeCaseSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class EdgeCase:
    """An edge case definition for testing."""
    id: str
    name: str
    category: EdgeCaseCategory
    entity: str
    workflow: str = ""
    description: str = ""
    test_approach: str = ""
    expected_behavior: str = ""
    severity: EdgeCaseSeverity = EdgeCaseSeverity.MEDIUM
    example_data: dict = field(default_factory=dict)


EDGE_CASES: list[EdgeCase] = [
    # Concurrency Edge Cases
    EdgeCase(
        id="EC001",
        name="concurrent_cart_update",
        category=EdgeCaseCategory.CONCURRENCY,
        entity="cart",
        workflow="checkout",
        description="Two sessions update the same cart simultaneously",
        test_approach="Race condition testing with parallel requests modifying cart items",
        expected_behavior="Last write wins with optimistic locking, or conflict error returned",
        severity=EdgeCaseSeverity.HIGH,
        example_data={
            "scenario": "Two browser tabs adding items to same cart",
            "timing": "Requests within 100ms of each other",
        },
    ),
    EdgeCase(
        id="EC002",
        name="inventory_oversell",
        category=EdgeCaseCategory.CONCURRENCY,
        entity="order",
        workflow="checkout",
        description="Multiple orders for last item in stock placed simultaneously",
        test_approach="Parallel checkout requests for item with quantity=1",
        expected_behavior="Only one order succeeds, others fail with inventory error",
        severity=EdgeCaseSeverity.CRITICAL,
        example_data={
            "product_inventory": 1,
            "concurrent_orders": 5,
        },
    ),
    EdgeCase(
        id="EC003",
        name="double_payment_submission",
        category=EdgeCaseCategory.CONCURRENCY,
        entity="payment",
        workflow="checkout",
        description="User double-clicks payment button submitting twice",
        test_approach="Rapid duplicate POST requests to payment endpoint",
        expected_behavior="Idempotency key prevents duplicate charge",
        severity=EdgeCaseSeverity.CRITICAL,
        example_data={
            "idempotency_key": "same-key-both-requests",
            "time_between_requests": "50ms",
        },
    ),
    
    # Network Edge Cases
    EdgeCase(
        id="EC004",
        name="payment_timeout_after_success",
        category=EdgeCaseCategory.NETWORK,
        entity="payment",
        workflow="checkout",
        description="Payment gateway succeeds but response times out",
        test_approach="Inject network delay after payment gateway returns success",
        expected_behavior="Reconciliation job detects and completes order, or retry is idempotent",
        severity=EdgeCaseSeverity.CRITICAL,
        example_data={
            "gateway_response": "success",
            "timeout_point": "after_gateway_response",
        },
    ),
    EdgeCase(
        id="EC005",
        name="webhook_delivery_failure",
        category=EdgeCaseCategory.NETWORK,
        entity="payment",
        description="Payment webhook fails to deliver",
        test_approach="Block webhook endpoint, verify retry behavior",
        expected_behavior="Gateway retries webhook, system handles eventual delivery",
        severity=EdgeCaseSeverity.HIGH,
    ),
    
    # Boundary Edge Cases
    EdgeCase(
        id="EC006",
        name="cart_max_items",
        category=EdgeCaseCategory.BOUNDARY,
        entity="cart",
        description="Cart with maximum allowed items (100)",
        test_approach="Add 100 items to cart, attempt to add 101st",
        expected_behavior="101st item rejected with clear error message",
        severity=EdgeCaseSeverity.MEDIUM,
        example_data={
            "current_items": 100,
            "action": "add_item",
        },
    ),
    EdgeCase(
        id="EC007",
        name="item_quantity_boundary",
        category=EdgeCaseCategory.BOUNDARY,
        entity="cart_item",
        description="Item quantity at boundaries (0, 1, 99, 100)",
        test_approach="Test quantity updates at boundary values",
        expected_behavior="0 removes item, 1-99 accepted, 100+ rejected",
        severity=EdgeCaseSeverity.MEDIUM,
        example_data={
            "test_quantities": [0, 1, 99, 100],
        },
    ),
    EdgeCase(
        id="EC008",
        name="large_order_total",
        category=EdgeCaseCategory.BOUNDARY,
        entity="order",
        description="Order with very large total ($999,999.99)",
        test_approach="Create cart with high-value items summing to max",
        expected_behavior="System handles large amounts, fraud check may trigger",
        severity=EdgeCaseSeverity.MEDIUM,
    ),
    
    # Data Edge Cases
    EdgeCase(
        id="EC009",
        name="special_characters_in_names",
        category=EdgeCaseCategory.DATA,
        entity="customer",
        description="Customer name with special characters, unicode, emojis",
        test_approach="Create customers with names like: O'Brien, 日本語, 🎉",
        expected_behavior="All valid unicode names accepted and displayed correctly",
        severity=EdgeCaseSeverity.LOW,
        example_data={
            "test_names": ["O'Brien", "José García", "日本語", "🎉 Party"],
        },
    ),
    EdgeCase(
        id="EC010",
        name="product_with_zero_price",
        category=EdgeCaseCategory.DATA,
        entity="product",
        description="Free product or product with $0.00 price",
        test_approach="Add free product to cart, complete checkout",
        expected_behavior="Free products handled, may skip payment step",
        severity=EdgeCaseSeverity.MEDIUM,
    ),
    EdgeCase(
        id="EC011",
        name="empty_string_fields",
        category=EdgeCaseCategory.DATA,
        entity="customer",
        description="Required fields submitted as empty strings",
        test_approach="Submit forms with '' for required fields",
        expected_behavior="Empty strings treated as missing, validation fails",
        severity=EdgeCaseSeverity.MEDIUM,
    ),
    
    # Timing Edge Cases
    EdgeCase(
        id="EC012",
        name="checkout_at_midnight",
        category=EdgeCaseCategory.TIMING,
        entity="order",
        workflow="checkout",
        description="Checkout exactly at midnight when day changes",
        test_approach="Execute checkout at 23:59:59, verify date handling",
        expected_behavior="Order date is consistent throughout transaction",
        severity=EdgeCaseSeverity.LOW,
    ),
    EdgeCase(
        id="EC013",
        name="price_change_during_checkout",
        category=EdgeCaseCategory.TIMING,
        entity="cart",
        workflow="checkout",
        description="Product price changes while customer is checking out",
        test_approach="Update price between cart creation and payment",
        expected_behavior="Customer notified of price change, must re-confirm",
        severity=EdgeCaseSeverity.HIGH,
    ),
    EdgeCase(
        id="EC014",
        name="promotion_expires_during_checkout",
        category=EdgeCaseCategory.TIMING,
        entity="cart",
        workflow="checkout",
        description="Applied promotion expires during checkout process",
        test_approach="Apply promo, wait until expiry, attempt checkout",
        expected_behavior="Expired promo removed, customer notified",
        severity=EdgeCaseSeverity.MEDIUM,
    ),
    
    # Security Edge Cases
    EdgeCase(
        id="EC015",
        name="sql_injection_in_search",
        category=EdgeCaseCategory.SECURITY,
        entity="product",
        description="SQL injection attempt in product search",
        test_approach="Search with: '; DROP TABLE products; --",
        expected_behavior="Input sanitized, no SQL execution, search returns no results",
        severity=EdgeCaseSeverity.CRITICAL,
    ),
    EdgeCase(
        id="EC016",
        name="xss_in_review",
        category=EdgeCaseCategory.SECURITY,
        entity="review",
        description="XSS script in review content",
        test_approach="Submit review with: <script>alert('xss')</script>",
        expected_behavior="HTML escaped or sanitized, no script execution",
        severity=EdgeCaseSeverity.HIGH,
    ),
    
    # Integration Edge Cases
    EdgeCase(
        id="EC017",
        name="payment_gateway_down",
        category=EdgeCaseCategory.INTEGRATION,
        entity="payment",
        workflow="checkout",
        description="Payment gateway is unavailable",
        test_approach="Mock gateway to return 503, attempt checkout",
        expected_behavior="Graceful error, suggest retry or alternate payment",
        severity=EdgeCaseSeverity.HIGH,
    ),
    EdgeCase(
        id="EC018",
        name="shipping_api_timeout",
        category=EdgeCaseCategory.INTEGRATION,
        entity="shipment",
        workflow="checkout",
        description="Shipping rate API times out",
        test_approach="Mock shipping API with 30s delay",
        expected_behavior="Timeout with fallback rates or retry option",
        severity=EdgeCaseSeverity.MEDIUM,
    ),
]


def get_edge_cases_for_entity(entity: str) -> list[EdgeCase]:
    """Get all edge cases for a specific entity."""
    return [ec for ec in EDGE_CASES if ec.entity == entity]


def get_edge_cases_for_workflow(workflow: str) -> list[EdgeCase]:
    """Get all edge cases for a specific workflow."""
    return [ec for ec in EDGE_CASES if ec.workflow == workflow]


def get_edge_cases_by_category(category: EdgeCaseCategory) -> list[EdgeCase]:
    """Get all edge cases in a category."""
    return [ec for ec in EDGE_CASES if ec.category == category]


def get_edge_cases_by_severity(severity: EdgeCaseSeverity) -> list[EdgeCase]:
    """Get all edge cases with a specific severity."""
    return [ec for ec in EDGE_CASES if ec.severity == severity]


def get_all_edge_cases() -> list[EdgeCase]:
    """Get all edge cases."""
    return EDGE_CASES
```

Acceptance Criteria:
- [ ] Edge cases cover all categories (concurrency, network, boundary, etc.)
- [ ] Each edge case has test approach and expected behavior
- [ ] Severity levels assigned appropriately
- [ ] Filter functions work correctly
```

---

## Phase 3: Knowledge Layer

### Task 3.1: Create Weaviate Client

```
Create the Weaviate client for RAG operations.

Create src/ecommerce_agent/clients/__init__.py:
```python
"""Client modules."""
```

Create src/ecommerce_agent/clients/weaviate.py:

```python
import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import MetadataQuery
from typing import Any

from ecommerce_agent.config import get_settings
from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)


class WeaviateClient:
    """Client for Weaviate vector database operations."""
    
    def __init__(self):
        settings = get_settings()
        self.client = weaviate.connect_to_custom(
            http_host=settings.weaviate_url.replace("http://", "").split(":")[0],
            http_port=int(settings.weaviate_url.split(":")[-1]),
            http_secure=False,
            grpc_host=settings.weaviate_url.replace("http://", "").split(":")[0],
            grpc_port=50051,
            grpc_secure=False,
        )
        self._ensure_collections()
    
    def _ensure_collections(self) -> None:
        """Ensure all required collections exist."""
        collections = [
            {
                "name": "EcommerceEntities",
                "properties": [
                    Property(name="entity_name", data_type=DataType.TEXT),
                    Property(name="description", data_type=DataType.TEXT),
                    Property(name="category", data_type=DataType.TEXT),
                    Property(name="fields_json", data_type=DataType.TEXT),
                    Property(name="relationships_json", data_type=DataType.TEXT),
                ],
            },
            {
                "name": "EcommerceWorkflows",
                "properties": [
                    Property(name="workflow_name", data_type=DataType.TEXT),
                    Property(name="description", data_type=DataType.TEXT),
                    Property(name="steps_json", data_type=DataType.TEXT),
                    Property(name="involved_entities", data_type=DataType.TEXT_ARRAY),
                ],
            },
            {
                "name": "EcommerceRules",
                "properties": [
                    Property(name="rule_id", data_type=DataType.TEXT),
                    Property(name="name", data_type=DataType.TEXT),
                    Property(name="entity", data_type=DataType.TEXT),
                    Property(name="description", data_type=DataType.TEXT),
                    Property(name="constraint", data_type=DataType.TEXT),
                    Property(name="severity", data_type=DataType.TEXT),
                ],
            },
            {
                "name": "EcommerceEdgeCases",
                "properties": [
                    Property(name="edge_case_id", data_type=DataType.TEXT),
                    Property(name="name", data_type=DataType.TEXT),
                    Property(name="category", data_type=DataType.TEXT),
                    Property(name="entity", data_type=DataType.TEXT),
                    Property(name="workflow", data_type=DataType.TEXT),
                    Property(name="description", data_type=DataType.TEXT),
                    Property(name="test_approach", data_type=DataType.TEXT),
                    Property(name="severity", data_type=DataType.TEXT),
                ],
            },
            {
                "name": "EcommerceTestPatterns",
                "properties": [
                    Property(name="entity", data_type=DataType.TEXT),
                    Property(name="scenario", data_type=DataType.TEXT),
                    Property(name="context", data_type=DataType.TEXT),
                    Property(name="data_json", data_type=DataType.TEXT),
                    Property(name="quality_score", data_type=DataType.NUMBER),
                ],
            },
        ]
        
        for coll_config in collections:
            name = coll_config["name"]
            if not self.client.collections.exists(name):
                self.client.collections.create(
                    name=name,
                    properties=coll_config["properties"],
                    vectorizer_config=Configure.Vectorizer.text2vec_transformers(),
                )
                logger.info(f"Created collection: {name}")
    
    async def search(
        self,
        collection: str,
        query: str,
        limit: int = 10,
        filters: dict | None = None,
    ) -> list[dict[str, Any]]:
        """Semantic search in a collection."""
        coll = self.client.collections.get(collection)
        
        response = coll.query.near_text(
            query=query,
            limit=limit,
            return_metadata=MetadataQuery(distance=True),
        )
        
        results = []
        for obj in response.objects:
            result = obj.properties.copy()
            result["_distance"] = obj.metadata.distance
            result["_id"] = str(obj.uuid)
            results.append(result)
        
        return results
    
    async def insert(
        self,
        collection: str,
        data: dict[str, Any],
    ) -> str:
        """Insert a document into a collection."""
        coll = self.client.collections.get(collection)
        uuid = coll.data.insert(data)
        return str(uuid)
    
    async def batch_insert(
        self,
        collection: str,
        data: list[dict[str, Any]],
    ) -> int:
        """Batch insert documents."""
        coll = self.client.collections.get(collection)
        with coll.batch.dynamic() as batch:
            for item in data:
                batch.add_object(properties=item)
        return len(data)
    
    def close(self) -> None:
        """Close the client connection."""
        self.client.close()
```

Acceptance Criteria:
- [ ] Client connects to Weaviate
- [ ] Collections are created on startup
- [ ] search() returns semantically relevant results
- [ ] insert() and batch_insert() work correctly
```

---

### Task 3.2: Create Knowledge Retriever

```
Create the knowledge retriever for RAG-based queries.

Create src/ecommerce_agent/knowledge/__init__.py:
```python
"""Knowledge layer modules."""
```

Create src/ecommerce_agent/knowledge/retriever.py:

```python
import json
from dataclasses import dataclass
from typing import Any

from ecommerce_agent.clients.weaviate import WeaviateClient
from ecommerce_agent.domain.entities import get_entity, list_entities, EntityDefinition
from ecommerce_agent.domain.workflows import get_workflow, list_workflows, WorkflowDefinition
from ecommerce_agent.domain.business_rules import get_rules_for_entity, BusinessRule
from ecommerce_agent.domain.edge_cases import get_edge_cases_for_entity, get_edge_cases_for_workflow, EdgeCase
from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class KnowledgeItem:
    """A retrieved knowledge item."""
    id: str
    category: str  # entity, workflow, rule, edge_case, pattern
    title: str
    content: str
    relevance_score: float
    metadata: dict[str, Any]


@dataclass
class EntityContext:
    """Complete context for an entity."""
    entity: EntityDefinition
    rules: list[BusinessRule]
    edge_cases: list[EdgeCase]
    related_workflows: list[str]


@dataclass
class WorkflowContext:
    """Complete context for a workflow."""
    workflow: WorkflowDefinition
    entity_contexts: dict[str, EntityContext]
    edge_cases: list[EdgeCase]


class KnowledgeRetriever:
    """Retrieves domain knowledge from various sources."""
    
    def __init__(self, weaviate_client: WeaviateClient):
        self.weaviate = weaviate_client
    
    async def query(
        self,
        query: str,
        categories: list[str] | None = None,
        max_results: int = 10,
    ) -> list[KnowledgeItem]:
        """
        Query domain knowledge across all categories.
        
        Categories: entities, workflows, rules, edge_cases, patterns
        """
        results: list[KnowledgeItem] = []
        
        # Default to all categories
        if not categories:
            categories = ["entities", "workflows", "rules", "edge_cases", "patterns"]
        
        collection_map = {
            "entities": "EcommerceEntities",
            "workflows": "EcommerceWorkflows",
            "rules": "EcommerceRules",
            "edge_cases": "EcommerceEdgeCases",
            "patterns": "EcommerceTestPatterns",
        }
        
        for category in categories:
            if category not in collection_map:
                continue
            
            collection = collection_map[category]
            try:
                items = await self.weaviate.search(
                    collection=collection,
                    query=query,
                    limit=max_results // len(categories) + 1,
                )
                
                for item in items:
                    results.append(KnowledgeItem(
                        id=item.get("_id", ""),
                        category=category,
                        title=item.get("name", item.get("entity_name", item.get("workflow_name", ""))),
                        content=item.get("description", ""),
                        relevance_score=1 - item.get("_distance", 1),
                        metadata=item,
                    ))
            except Exception as e:
                logger.warning(f"Failed to search {collection}: {e}")
        
        # Sort by relevance and limit
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:max_results]
    
    def get_entity_context(self, entity_name: str) -> EntityContext | None:
        """Get complete context for an entity."""
        entity = get_entity(entity_name)
        if not entity:
            return None
        
        rules = get_rules_for_entity(entity_name)
        edge_cases = get_edge_cases_for_entity(entity_name)
        
        # Find workflows involving this entity
        related_workflows = [
            w.name for w in list_workflows()
            if entity_name in w.involved_entities
        ]
        
        return EntityContext(
            entity=entity,
            rules=rules,
            edge_cases=edge_cases,
            related_workflows=related_workflows,
        )
    
    def get_workflow_context(self, workflow_name: str) -> WorkflowContext | None:
        """Get complete context for a workflow."""
        workflow = get_workflow(workflow_name)
        if not workflow:
            return None
        
        # Get context for each involved entity
        entity_contexts = {}
        for entity_name in workflow.involved_entities:
            ctx = self.get_entity_context(entity_name)
            if ctx:
                entity_contexts[entity_name] = ctx
        
        edge_cases = get_edge_cases_for_workflow(workflow_name)
        
        return WorkflowContext(
            workflow=workflow,
            entity_contexts=entity_contexts,
            edge_cases=edge_cases,
        )
    
    async def get_similar_patterns(
        self,
        entity: str,
        scenario: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Get similar test data patterns from history."""
        query = f"{entity} {scenario}"
        results = await self.weaviate.search(
            collection="EcommerceTestPatterns",
            query=query,
            limit=limit,
        )
        return results
    
    async def store_pattern(
        self,
        entity: str,
        scenario: str,
        context: str,
        data: str,
        quality_score: float,
    ) -> str:
        """Store a successful test data pattern."""
        return await self.weaviate.insert(
            collection="EcommerceTestPatterns",
            data={
                "entity": entity,
                "scenario": scenario,
                "context": context,
                "data_json": data,
                "quality_score": quality_score,
            },
        )
```

Acceptance Criteria:
- [ ] query() searches across knowledge categories
- [ ] get_entity_context() returns complete entity info
- [ ] get_workflow_context() returns workflow with entity contexts
- [ ] Pattern storage and retrieval works
```

---

### Task 3.3: Create Knowledge Indexer

```
Create the knowledge indexer to seed domain knowledge into Weaviate.

Create src/ecommerce_agent/knowledge/indexer.py:

```python
import json

from ecommerce_agent.clients.weaviate import WeaviateClient
from ecommerce_agent.domain.entities import ENTITIES
from ecommerce_agent.domain.workflows import WORKFLOWS
from ecommerce_agent.domain.business_rules import BUSINESS_RULES
from ecommerce_agent.domain.edge_cases import EDGE_CASES
from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)


class KnowledgeIndexer:
    """Indexes domain knowledge into Weaviate."""
    
    def __init__(self, weaviate_client: WeaviateClient):
        self.weaviate = weaviate_client
    
    async def index_all(self) -> dict[str, int]:
        """Index all domain knowledge."""
        counts = {}
        
        counts["entities"] = await self.index_entities()
        counts["workflows"] = await self.index_workflows()
        counts["rules"] = await self.index_rules()
        counts["edge_cases"] = await self.index_edge_cases()
        
        logger.info("Knowledge indexing complete", counts=counts)
        return counts
    
    async def index_entities(self) -> int:
        """Index entity definitions."""
        data = []
        for entity in ENTITIES.values():
            data.append({
                "entity_name": entity.name,
                "description": entity.description,
                "category": entity.category,
                "fields_json": json.dumps([
                    {"name": f.name, "type": f.type, "description": f.description}
                    for f in entity.fields
                ]),
                "relationships_json": json.dumps([
                    {"target": r.target, "type": r.type}
                    for r in entity.relationships
                ]),
            })
        
        return await self.weaviate.batch_insert("EcommerceEntities", data)
    
    async def index_workflows(self) -> int:
        """Index workflow definitions."""
        data = []
        for workflow in WORKFLOWS.values():
            data.append({
                "workflow_name": workflow.name,
                "description": workflow.description,
                "steps_json": json.dumps([
                    {
                        "order": s.order,
                        "name": s.name,
                        "description": s.description,
                        "entity": s.entity,
                        "action": s.action,
                    }
                    for s in workflow.steps
                ]),
                "involved_entities": workflow.involved_entities,
            })
        
        return await self.weaviate.batch_insert("EcommerceWorkflows", data)
    
    async def index_rules(self) -> int:
        """Index business rules."""
        data = []
        for rule in BUSINESS_RULES:
            data.append({
                "rule_id": rule.id,
                "name": rule.name,
                "entity": rule.entity,
                "description": rule.description,
                "constraint": rule.constraint,
                "severity": rule.severity.value,
            })
        
        return await self.weaviate.batch_insert("EcommerceRules", data)
    
    async def index_edge_cases(self) -> int:
        """Index edge cases."""
        data = []
        for ec in EDGE_CASES:
            data.append({
                "edge_case_id": ec.id,
                "name": ec.name,
                "category": ec.category.value,
                "entity": ec.entity,
                "workflow": ec.workflow,
                "description": ec.description,
                "test_approach": ec.test_approach,
                "severity": ec.severity.value,
            })
        
        return await self.weaviate.batch_insert("EcommerceEdgeCases", data)


async def seed_knowledge() -> None:
    """Seed all domain knowledge into Weaviate."""
    client = WeaviateClient()
    indexer = KnowledgeIndexer(client)
    
    try:
        counts = await indexer.index_all()
        logger.info("Knowledge seeding complete", **counts)
    finally:
        client.close()
```

Acceptance Criteria:
- [ ] index_all() indexes all domain knowledge
- [ ] Each category has dedicated indexing method
- [ ] Batch insert is used for efficiency
- [ ] seed_knowledge() can be run as standalone script
```

---

## Phase 4: Test Data Agent Integration

### Task 4.1: Create Test Data Agent Client

```
Create the gRPC client for calling the Test Data Agent.

Create src/ecommerce_agent/clients/test_data_client.py:

```python
import grpc
from typing import Any

from ecommerce_agent.proto import test_data_pb2 as pb2
from ecommerce_agent.proto import test_data_pb2_grpc as pb2_grpc
from ecommerce_agent.config import get_settings
from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)


class TestDataAgentClient:
    """gRPC client for Test Data Agent service."""
    
    def __init__(self):
        settings = get_settings()
        self.host = settings.test_data_agent_host
        self.port = settings.test_data_agent_port
        self.timeout = settings.test_data_agent_timeout
        self._channel: grpc.aio.Channel | None = None
        self._stub: pb2_grpc.TestDataServiceStub | None = None
    
    async def _ensure_connected(self) -> None:
        """Ensure connection to Test Data Agent."""
        if self._channel is None:
            self._channel = grpc.aio.insecure_channel(
                f"{self.host}:{self.port}",
                options=[
                    ("grpc.max_receive_message_length", 50 * 1024 * 1024),
                    ("grpc.max_send_message_length", 50 * 1024 * 1024),
                ],
            )
            self._stub = pb2_grpc.TestDataServiceStub(self._channel)
            logger.info(
                "Connected to Test Data Agent",
                host=self.host,
                port=self.port,
            )
    
    async def generate_data(
        self,
        request_id: str,
        domain: str,
        entity: str,
        count: int,
        context: str = "",
        scenarios: list[dict[str, Any]] | None = None,
        hints: list[str] | None = None,
        output_format: str = "JSON",
        use_cache: bool = False,
        learn_from_history: bool = False,
        defect_triggering: bool = False,
        production_like: bool = False,
        inline_schema: str = "",
        schema: dict[str, Any] | None = None,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Generate test data via Test Data Agent.
        
        Args:
            request_id: Unique request ID for tracing
            domain: Domain name (ecommerce, supply_chain, etc.)
            entity: Entity name (cart, order, payment, etc.)
            count: Number of records to generate
            context: Natural language context for LLM
            scenarios: List of scenario dicts with name, count, description, overrides
            hints: Routing hints (realistic, edge_case, defect_triggering)
            output_format: JSON, CSV, or SQL
            use_cache: Use cached data pools
            learn_from_history: Use RAG patterns
            defect_triggering: Generate bug-finding data
            production_like: Mimic production distributions
            inline_schema: JSON string of complete schema definition
            schema: Schema dict with fields or predefined_schema
            constraints: Field constraints dict
        
        Returns the response as a dictionary.
        """
        await self._ensure_connected()
        
        # Build scenarios
        proto_scenarios = []
        if scenarios:
            for s in scenarios:
                proto_scenarios.append(pb2.Scenario(
                    name=s.get("name", ""),
                    count=s.get("count", 10),
                    description=s.get("description", ""),
                    overrides=s.get("overrides", {}),
                ))
        
        # Build schema if provided
        proto_schema = None
        if schema:
            if "predefined_schema" in schema:
                proto_schema = pb2.Schema(predefined_schema=schema["predefined_schema"])
            elif "fields" in schema:
                # Build fields recursively
                proto_schema = pb2.Schema(fields=self._build_fields(schema["fields"]))
        
        # Build constraints if provided
        proto_constraints = None
        if constraints:
            field_constraints = {}
            for field_name, constraint in constraints.items():
                field_constraints[field_name] = pb2.FieldConstraint(
                    min=constraint.get("min"),
                    max=constraint.get("max"),
                    enum_values=constraint.get("enum_values", []),
                    regex=constraint.get("regex"),
                    min_length=constraint.get("min_length"),
                    max_length=constraint.get("max_length"),
                    format=constraint.get("format"),
                )
            proto_constraints = pb2.Constraints(field_constraints=field_constraints)
        
        # Build request
        request = pb2.GenerateRequest(
            request_id=request_id,
            domain=domain,
            entity=entity,
            count=count,
            context=context,
            scenarios=proto_scenarios,
            hints=hints or [],
            output_format=self._get_output_format(output_format),
            use_cache=use_cache,
            learn_from_history=learn_from_history,
            defect_triggering=defect_triggering,
            production_like=production_like,
            inline_schema=inline_schema,
        )
        
        # Add optional fields if provided
        if proto_schema:
            request.schema.CopyFrom(proto_schema)
        if proto_constraints:
            request.constraints.CopyFrom(proto_constraints)
        
        logger.info(
            "Calling Test Data Agent",
            request_id=request_id,
            entity=entity,
            count=count,
        )
        
        try:
            response = await self._stub.GenerateData(
                request,
                timeout=self.timeout,
            )
            
            return {
                "request_id": response.request_id,
                "success": response.success,
                "data": response.data,
                "record_count": response.record_count,
                "metadata": {
                    "generation_path": response.metadata.generation_path,
                    "llm_tokens_used": response.metadata.llm_tokens_used,
                    "generation_time_ms": response.metadata.generation_time_ms,
                    "coherence_score": response.metadata.coherence_score,
                    "scenario_counts": dict(response.metadata.scenario_counts),
                },
                "error": response.error or None,
            }
        except grpc.aio.AioRpcError as e:
            logger.error(
                "Test Data Agent call failed",
                request_id=request_id,
                error=str(e),
            )
            return {
                "request_id": request_id,
                "success": False,
                "data": "",
                "record_count": 0,
                "metadata": {},
                "error": str(e),
            }
    
    async def get_schemas(self, domain: str = "") -> list[dict[str, Any]]:
        """Get available schemas from Test Data Agent."""
        await self._ensure_connected()
        
        request = pb2.GetSchemasRequest(domain=domain)
        
        try:
            response = await self._stub.GetSchemas(request, timeout=10)
            return [
                {
                    "name": s.name,
                    "domain": s.domain,
                    "description": s.description,
                    "fields": list(s.fields),
                }
                for s in response.schemas
            ]
        except grpc.aio.AioRpcError as e:
            logger.error("Failed to get schemas", error=str(e))
            return []
    
    async def health_check(self) -> dict[str, Any]:
        """Check Test Data Agent health."""
        await self._ensure_connected()
        
        try:
            response = await self._stub.HealthCheck(
                pb2.HealthCheckRequest(),
                timeout=5,
            )
            return {
                "status": response.status,
                "components": dict(response.components),
            }
        except grpc.aio.AioRpcError as e:
            logger.error("Health check failed", error=str(e))
            return {"status": "unhealthy", "components": {}}
    
    def _get_output_format(self, format_str: str) -> int:
        """Convert output format string to proto enum."""
        formats = {"JSON": 0, "CSV": 1, "SQL": 2}
        return formats.get(format_str.upper(), 0)
    
    def _build_fields(self, fields: list[dict]) -> list:
        """Recursively build proto Field messages."""
        proto_fields = []
        for f in fields:
            field_type = self._get_field_type(f.get("type", "STRING"))
            proto_field = pb2.Field(
                name=f.get("name", ""),
                type=field_type,
                required=f.get("required", False),
                description=f.get("description", ""),
            )
            # Handle nested fields for OBJECT and ARRAY types
            if "nested_fields" in f and f["nested_fields"]:
                proto_field.nested_fields.extend(self._build_fields(f["nested_fields"]))
            proto_fields.append(proto_field)
        return proto_fields
    
    def _get_field_type(self, type_str: str) -> int:
        """Convert field type string to proto enum."""
        types = {
            "STRING": 0, "INTEGER": 1, "FLOAT": 2, "BOOLEAN": 3,
            "DATE": 4, "DATETIME": 5, "EMAIL": 6, "PHONE": 7,
            "ADDRESS": 8, "UUID": 9, "ENUM": 10, "OBJECT": 11, "ARRAY": 12,
        }
        return types.get(type_str.upper(), 0)
    
    async def close(self) -> None:
        """Close the connection."""
        if self._channel:
            await self._channel.close()
            self._channel = None
            self._stub = None
```

Acceptance Criteria:
- [ ] Client connects to Test Data Agent
- [ ] generate_data() calls GenerateData RPC
- [ ] Response is converted to dictionary
- [ ] Error handling returns structured error
- [ ] get_schemas() and health_check() work
```

---

### Task 4.2: Create Context Builder

```
Create the context builder that enriches requests with domain knowledge.

Create src/ecommerce_agent/context/__init__.py:
```python
"""Context building modules."""
```

Create src/ecommerce_agent/context/builder.py:

```python
from dataclasses import dataclass
from typing import Any

from ecommerce_agent.knowledge.retriever import KnowledgeRetriever, EntityContext, WorkflowContext
from ecommerce_agent.domain.entities import get_entity
from ecommerce_agent.domain.workflows import get_workflow
from ecommerce_agent.domain.business_rules import get_rules_for_entity
from ecommerce_agent.domain.edge_cases import get_edge_cases_for_entity, get_edge_cases_for_workflow
from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class DomainContext:
    """Rich domain context for test generation."""
    entity: str
    workflow: str | None
    natural_language_context: str
    business_rules: list[str]
    relationships: list[str]
    edge_cases: list[str]
    hints: list[str]


class DomainContextBuilder:
    """Builds rich domain context for STLC agents."""
    
    def __init__(self, knowledge_retriever: KnowledgeRetriever):
        self.retriever = knowledge_retriever
    
    def build_context(
        self,
        entity: str,
        workflow: str | None = None,
        scenario: str | None = None,
        custom_context: str = "",
        include_edge_cases: bool = False,
    ) -> DomainContext:
        """
        Build comprehensive domain context for test generation.
        
        Combines:
        1. Entity schema and relationships
        2. Applicable business rules
        3. Workflow context if provided
        4. Edge cases if requested
        5. Custom context from user
        """
        # Get entity context
        entity_ctx = self.retriever.get_entity_context(entity)
        if not entity_ctx:
            logger.warning(f"Entity not found: {entity}")
            return DomainContext(
                entity=entity,
                workflow=workflow,
                natural_language_context=custom_context,
                business_rules=[],
                relationships=[],
                edge_cases=[],
                hints=[],
            )
        
        # Build natural language context
        nl_parts = [
            f"Generate {entity} data for eCommerce domain.",
            f"\nEntity: {entity_ctx.entity.description}",
        ]
        
        # Add field descriptions
        nl_parts.append("\nFields:")
        for field in entity_ctx.entity.fields[:10]:  # Limit to avoid too long context
            nl_parts.append(f"- {field.name} ({field.type}): {field.description}")
        
        # Add business rules
        business_rules = []
        nl_parts.append("\nBusiness Rules to Honor:")
        for rule in entity_ctx.rules:
            rule_text = f"{rule.id}: {rule.constraint}"
            business_rules.append(rule_text)
            nl_parts.append(f"- {rule_text}")
        
        # Add relationships
        relationships = []
        nl_parts.append("\nEntity Relationships:")
        for rel in entity_ctx.entity.relationships:
            rel_text = f"{entity} {rel.type} {rel.target}"
            relationships.append(rel_text)
            nl_parts.append(f"- {rel_text}")
        
        # Add workflow context if provided
        hints = []
        if workflow:
            workflow_ctx = self.retriever.get_workflow_context(workflow)
            if workflow_ctx:
                nl_parts.append(f"\nWorkflow Context: {workflow}")
                nl_parts.append(workflow_ctx.workflow.description)
                
                # Find relevant steps
                relevant_steps = [
                    s for s in workflow_ctx.workflow.steps
                    if s.entity == entity
                ]
                if relevant_steps:
                    nl_parts.append(f"\nRelevant Steps in {workflow}:")
                    for step in relevant_steps:
                        nl_parts.append(f"- {step.name}: {step.description}")
                
                hints.append(f"{workflow}_flow")
        
        # Add edge cases if requested
        edge_cases = []
        if include_edge_cases:
            entity_edge_cases = get_edge_cases_for_entity(entity)
            if workflow:
                workflow_edge_cases = get_edge_cases_for_workflow(workflow)
                entity_edge_cases.extend(workflow_edge_cases)
            
            nl_parts.append("\nEdge Cases to Consider:")
            for ec in entity_edge_cases[:5]:  # Limit
                ec_text = f"{ec.name}: {ec.description}"
                edge_cases.append(ec_text)
                nl_parts.append(f"- {ec_text}")
            
            hints.append("edge_case")
        
        # Add custom context
        if custom_context:
            nl_parts.append(f"\nAdditional Requirements:\n{custom_context}")
        
        # Add coherence hint
        hints.append("realistic")
        
        return DomainContext(
            entity=entity,
            workflow=workflow,
            natural_language_context="\n".join(nl_parts),
            business_rules=business_rules,
            relationships=relationships,
            edge_cases=edge_cases,
            hints=hints,
        )
    
    def build_scenarios(
        self,
        entity: str,
        scenario_counts: dict[str, int] | None = None,
        include_edge_cases: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Build test scenarios based on entity and options.
        
        Returns list of scenarios with counts and descriptions.
        """
        entity_def = get_entity(entity)
        if not entity_def:
            return [{"name": "happy_path", "count": 10}]
        
        scenarios = []
        
        if scenario_counts:
            # Use provided scenario counts
            for name, count in scenario_counts.items():
                desc = self._get_scenario_description(entity, name)
                scenarios.append({
                    "name": name,
                    "count": count,
                    "description": desc,
                })
        else:
            # Use entity's defined test scenarios
            total = 50  # Default total
            per_scenario = total // len(entity_def.test_scenarios)
            
            for scenario_name in entity_def.test_scenarios:
                desc = self._get_scenario_description(entity, scenario_name)
                scenarios.append({
                    "name": scenario_name,
                    "count": per_scenario,
                    "description": desc,
                })
        
        return scenarios
    
    def _get_scenario_description(self, entity: str, scenario: str) -> str:
        """Get description for a scenario."""
        # Standard scenario descriptions
        descriptions = {
            "happy_path": f"Standard valid {entity} with typical values",
            "high_value": f"{entity} with high monetary values (>$500)",
            "low_value": f"{entity} with minimal monetary values (<$10)",
            "single_item": f"{entity} with exactly one item",
            "max_items": f"{entity} with maximum allowed items",
            "edge_case": f"{entity} at boundary conditions",
            "abandoned": f"Abandoned {entity} scenario",
            "multi_currency": f"{entity} with non-USD currency",
            "international": f"{entity} with international addresses",
            "express_shipping": f"{entity} with express delivery",
            "payment_declined": f"{entity} where payment fails",
            "card_success": "Successful card payment",
            "card_declined": "Declined card payment",
            "paypal_success": "Successful PayPal payment",
            "full_refund": "Full refund scenario",
            "partial_refund": "Partial refund scenario",
            "denied_return": "Return request denied",
            "positive": "Positive review (4-5 stars)",
            "negative": "Negative review (1-2 stars)",
            "detailed": "Detailed review with long text",
        }
        
        return descriptions.get(scenario, f"{scenario} scenario for {entity}")
```

Acceptance Criteria:
- [ ] build_context() creates rich natural language context
- [ ] Business rules are included
- [ ] Workflow context is added when provided
- [ ] Edge cases are included when requested
- [ ] build_scenarios() creates appropriate scenarios
```

---

### Task 4.3: Create Generation Orchestrator

```
Create the orchestrator that coordinates domain-aware test data generation.

Create src/ecommerce_agent/context/orchestrator.py:

```python
import time
import uuid
from dataclasses import dataclass
from typing import Any

from ecommerce_agent.clients.test_data_client import TestDataAgentClient
from ecommerce_agent.context.builder import DomainContextBuilder, DomainContext
from ecommerce_agent.knowledge.retriever import KnowledgeRetriever
from ecommerce_agent.utils.logging import get_logger, bind_context

logger = get_logger(__name__)


@dataclass
class GenerationResult:
    """Result of test data generation."""
    request_id: str
    success: bool
    data: str
    record_count: int
    generation_path: str
    llm_tokens_used: int
    generation_time_ms: float
    coherence_score: float
    domain_context_used: str
    scenario_counts: dict[str, int]
    error: str | None = None


class GenerationOrchestrator:
    """Orchestrates domain-aware test data generation."""
    
    def __init__(
        self,
        test_data_client: TestDataAgentClient,
        context_builder: DomainContextBuilder,
        knowledge_retriever: KnowledgeRetriever,
    ):
        self.test_data_client = test_data_client
        self.context_builder = context_builder
        self.knowledge_retriever = knowledge_retriever
    
    async def generate(
        self,
        entity: str,
        count: int,
        workflow_context: str | None = None,
        scenarios: list[str] | None = None,
        custom_context: str = "",
        include_edge_cases: bool = False,
        output_format: str = "JSON",
        scenario_counts: dict[str, int] | None = None,
    ) -> GenerationResult:
        """
        Generate test data with full domain context.
        
        Steps:
        1. Build domain context
        2. Build scenarios
        3. Call Test Data Agent with enriched request
        4. Validate and score results
        5. Store successful patterns
        """
        request_id = f"ecom-{uuid.uuid4().hex[:8]}"
        bind_context(request_id=request_id)
        
        start_time = time.time()
        
        logger.info(
            "Starting domain-aware generation",
            entity=entity,
            count=count,
            workflow=workflow_context,
        )
        
        try:
            # Step 1: Build domain context
            domain_ctx = self.context_builder.build_context(
                entity=entity,
                workflow=workflow_context,
                custom_context=custom_context,
                include_edge_cases=include_edge_cases,
            )
            
            # Step 2: Build scenarios
            if scenario_counts:
                built_scenarios = self.context_builder.build_scenarios(
                    entity=entity,
                    scenario_counts=scenario_counts,
                    include_edge_cases=include_edge_cases,
                )
            elif scenarios:
                built_scenarios = [
                    {
                        "name": s,
                        "count": count // len(scenarios),
                        "description": self.context_builder._get_scenario_description(entity, s),
                    }
                    for s in scenarios
                ]
            else:
                built_scenarios = [{"name": "happy_path", "count": count}]
            
            # Adjust counts to match total
            total_scenario_count = sum(s["count"] for s in built_scenarios)
            if total_scenario_count != count:
                # Adjust first scenario
                diff = count - total_scenario_count
                built_scenarios[0]["count"] += diff
            
            # Step 3: Call Test Data Agent
            response = await self.test_data_client.generate_data(
                request_id=request_id,
                domain="ecommerce",
                entity=entity,
                count=count,
                context=domain_ctx.natural_language_context,
                scenarios=built_scenarios,
                hints=domain_ctx.hints,
                output_format=output_format,
                use_cache=False,
                learn_from_history=True,
                defect_triggering=include_edge_cases,
                production_like=not include_edge_cases,
            )
            
            generation_time_ms = (time.time() - start_time) * 1000
            
            if not response["success"]:
                logger.error(
                    "Generation failed",
                    error=response.get("error"),
                )
                return GenerationResult(
                    request_id=request_id,
                    success=False,
                    data="",
                    record_count=0,
                    generation_path="",
                    llm_tokens_used=0,
                    generation_time_ms=generation_time_ms,
                    coherence_score=0,
                    domain_context_used=domain_ctx.natural_language_context,
                    scenario_counts={},
                    error=response.get("error"),
                )
            
            # Step 4: Get metadata
            metadata = response.get("metadata", {})
            
            # Step 5: Store successful pattern (async, don't wait)
            coherence_score = metadata.get("coherence_score", 0.0)
            if coherence_score >= 0.8:
                # Store pattern for future RAG
                try:
                    await self.knowledge_retriever.store_pattern(
                        entity=entity,
                        scenario=built_scenarios[0]["name"] if built_scenarios else "default",
                        context=domain_ctx.natural_language_context,
                        data=response["data"][:1000],  # Store truncated sample
                        quality_score=coherence_score,
                    )
                except Exception as e:
                    logger.warning(f"Failed to store pattern: {e}")
            
            logger.info(
                "Generation complete",
                record_count=response["record_count"],
                generation_path=metadata.get("generation_path"),
                coherence_score=coherence_score,
            )
            
            return GenerationResult(
                request_id=request_id,
                success=True,
                data=response["data"],
                record_count=response["record_count"],
                generation_path=metadata.get("generation_path", "unknown"),
                llm_tokens_used=metadata.get("llm_tokens_used", 0),
                generation_time_ms=generation_time_ms,
                coherence_score=coherence_score,
                domain_context_used=domain_ctx.natural_language_context,
                scenario_counts=metadata.get("scenario_counts", {}),
            )
            
        except Exception as e:
            logger.exception("Generation orchestration failed")
            return GenerationResult(
                request_id=request_id,
                success=False,
                data="",
                record_count=0,
                generation_path="",
                llm_tokens_used=0,
                generation_time_ms=(time.time() - start_time) * 1000,
                coherence_score=0,
                domain_context_used="",
                scenario_counts={},
                error=str(e),
            )
```

Acceptance Criteria:
- [ ] Orchestrator builds context and calls Test Data Agent
- [ ] Scenarios are properly built and adjusted
- [ ] Successful patterns are stored for RAG
- [ ] Errors are handled gracefully
- [ ] Metrics are captured (time, tokens, coherence)
```

---

### Task 4.4: Update gRPC Service Implementation

```
Update the gRPC service to use the orchestrator and domain components.

Update src/ecommerce_agent/server/grpc_server.py to wire up all dependencies:

```python
import grpc
from concurrent import futures
from typing import Any

from ecommerce_agent.proto import ecommerce_domain_pb2 as pb2
from ecommerce_agent.proto import ecommerce_domain_pb2_grpc as pb2_grpc
from ecommerce_agent.clients.weaviate import WeaviateClient
from ecommerce_agent.clients.test_data_client import TestDataAgentClient
from ecommerce_agent.knowledge.retriever import KnowledgeRetriever
from ecommerce_agent.context.builder import DomainContextBuilder
from ecommerce_agent.context.orchestrator import GenerationOrchestrator
from ecommerce_agent.domain.entities import get_entity, list_entities
from ecommerce_agent.domain.workflows import get_workflow, list_workflows
from ecommerce_agent.domain.edge_cases import get_edge_cases_for_entity, get_edge_cases_for_workflow
from ecommerce_agent.utils.logging import get_logger, bind_context

logger = get_logger(__name__)


class EcommerceDomainServicer(pb2_grpc.EcommerceDomainServiceServicer):
    """gRPC service implementation for eCommerce Domain Agent."""
    
    def __init__(self):
        """Initialize with dependencies."""
        # Initialize clients
        self.weaviate_client = WeaviateClient()
        self.test_data_client = TestDataAgentClient()
        
        # Initialize knowledge layer
        self.knowledge_retriever = KnowledgeRetriever(self.weaviate_client)
        
        # Initialize context layer
        self.context_builder = DomainContextBuilder(self.knowledge_retriever)
        
        # Initialize orchestrator
        self.orchestrator = GenerationOrchestrator(
            test_data_client=self.test_data_client,
            context_builder=self.context_builder,
            knowledge_retriever=self.knowledge_retriever,
        )
        
        logger.info("EcommerceDomainServicer initialized")
    
    async def GetDomainContext(
        self,
        request: pb2.DomainContextRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.DomainContextResponse:
        """Get domain context for test generation."""
        bind_context(request_id=request.request_id, method="GetDomainContext")
        
        domain_ctx = self.context_builder.build_context(
            entity=request.entity,
            workflow=request.workflow if request.workflow else None,
            scenario=request.scenario if request.scenario else None,
        )
        
        # Convert to proto
        rules = []
        entity_ctx = self.knowledge_retriever.get_entity_context(request.entity)
        if entity_ctx:
            for rule in entity_ctx.rules:
                rules.append(pb2.BusinessRule(
                    id=rule.id,
                    name=rule.name,
                    description=rule.description,
                    entity=rule.entity,
                    condition=rule.condition,
                    constraint=rule.constraint,
                    severity=rule.severity.value,
                ))
        
        relationships = []
        if entity_ctx:
            for rel in entity_ctx.entity.relationships:
                relationships.append(pb2.EntityRelationship(
                    source_entity=request.entity,
                    target_entity=rel.target,
                    relationship_type=rel.type,
                    description=rel.description,
                    required=rel.required,
                ))
        
        return pb2.DomainContextResponse(
            request_id=request.request_id,
            context=domain_ctx.natural_language_context,
            rules=rules,
            relationships=relationships,
            edge_cases=domain_ctx.edge_cases,
        )
    
    async def QueryKnowledge(
        self,
        request: pb2.KnowledgeRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.KnowledgeResponse:
        """Query domain knowledge."""
        bind_context(request_id=request.request_id, method="QueryKnowledge")
        
        results = await self.knowledge_retriever.query(
            query=request.query,
            categories=list(request.categories) if request.categories else None,
            max_results=request.max_results or 10,
        )
        
        items = [
            pb2.KnowledgeItem(
                id=r.id,
                category=r.category,
                title=r.title,
                content=r.content,
                relevance_score=r.relevance_score,
                metadata=r.metadata,
            )
            for r in results
        ]
        
        return pb2.KnowledgeResponse(
            request_id=request.request_id,
            items=items,
            summary=f"Found {len(items)} relevant items",
        )
    
    async def GetEntity(
        self,
        request: pb2.EntityRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.EntityResponse:
        """Get entity details."""
        entity_ctx = self.knowledge_retriever.get_entity_context(request.entity_name)
        
        if not entity_ctx:
            await context.abort(grpc.StatusCode.NOT_FOUND, f"Entity not found: {request.entity_name}")
        
        entity = entity_ctx.entity
        
        fields = [
            pb2.EntityField(
                name=f.name,
                type=f.type,
                description=f.description,
                required=f.required,
                validations=f.validations,
                example=f.example,
            )
            for f in entity.fields
        ]
        
        rules = []
        if request.include_rules:
            for rule in entity_ctx.rules:
                rules.append(pb2.BusinessRule(
                    id=rule.id,
                    name=rule.name,
                    description=rule.description,
                    entity=rule.entity,
                    condition=rule.condition,
                    constraint=rule.constraint,
                    severity=rule.severity.value,
                ))
        
        relationships = []
        if request.include_relationships:
            for rel in entity.relationships:
                relationships.append(pb2.EntityRelationship(
                    source_entity=entity.name,
                    target_entity=rel.target,
                    relationship_type=rel.type,
                    description=rel.description,
                    required=rel.required,
                ))
        
        edge_cases = entity_ctx.edge_cases if request.include_edge_cases else []
        
        return pb2.EntityResponse(
            entity=pb2.Entity(
                name=entity.name,
                description=entity.description,
                fields=fields,
                rules=rules,
                relationships=relationships,
                edge_cases=[ec.description for ec in edge_cases],
                test_scenarios=entity.test_scenarios,
            )
        )
    
    async def ListEntities(
        self,
        request: pb2.ListEntitiesRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.ListEntitiesResponse:
        """List all entities."""
        entities = list_entities(request.category if request.category else None)
        
        summaries = [
            pb2.EntitySummary(
                name=e.name,
                description=e.description,
                category=e.category,
                field_count=len(e.fields),
            )
            for e in entities
        ]
        
        return pb2.ListEntitiesResponse(entities=summaries)
    
    async def GetWorkflow(
        self,
        request: pb2.WorkflowRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.WorkflowResponse:
        """Get workflow details."""
        workflow = get_workflow(request.workflow_name)
        
        if not workflow:
            await context.abort(grpc.StatusCode.NOT_FOUND, f"Workflow not found: {request.workflow_name}")
        
        steps = []
        if request.include_steps:
            for step in workflow.steps:
                steps.append(pb2.WorkflowStep(
                    order=step.order,
                    name=step.name,
                    description=step.description,
                    entity=step.entity,
                    action=step.action,
                    validations=step.validations,
                    possible_outcomes=step.possible_outcomes,
                ))
        
        edge_cases = []
        if request.include_edge_cases:
            edge_cases = [ec.description for ec in get_edge_cases_for_workflow(workflow.name)]
        
        return pb2.WorkflowResponse(
            workflow=pb2.Workflow(
                name=workflow.name,
                description=workflow.description,
                steps=steps,
                involved_entities=workflow.involved_entities,
                edge_cases=edge_cases,
                test_scenarios=workflow.test_scenarios,
            )
        )
    
    async def ListWorkflows(
        self,
        request: pb2.ListWorkflowsRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.ListWorkflowsResponse:
        """List all workflows."""
        workflows = list_workflows()
        
        summaries = [
            pb2.WorkflowSummary(
                name=w.name,
                description=w.description,
                step_count=len(w.steps),
                involved_entities=w.involved_entities,
            )
            for w in workflows
        ]
        
        return pb2.ListWorkflowsResponse(workflows=summaries)
    
    async def GetEdgeCases(
        self,
        request: pb2.EdgeCasesRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.EdgeCasesResponse:
        """Get edge cases."""
        edge_cases = []
        
        if request.entity:
            edge_cases.extend(get_edge_cases_for_entity(request.entity))
        if request.workflow:
            edge_cases.extend(get_edge_cases_for_workflow(request.workflow))
        
        # Filter by category if provided
        if request.category:
            edge_cases = [ec for ec in edge_cases if ec.category.value == request.category]
        
        return pb2.EdgeCasesResponse(
            edge_cases=[
                pb2.EdgeCase(
                    id=ec.id,
                    name=ec.name,
                    description=ec.description,
                    category=ec.category.value,
                    entity=ec.entity,
                    workflow=ec.workflow,
                    test_approach=ec.test_approach,
                    expected_behavior=ec.expected_behavior,
                    severity=ec.severity.value,
                    example_data=ec.example_data,
                )
                for ec in edge_cases
            ]
        )
    
    async def GenerateTestData(
        self,
        request: pb2.GenerateTestDataRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.GenerateTestDataResponse:
        """Generate test data via orchestrator."""
        bind_context(request_id=request.request_id, method="GenerateTestData")
        
        result = await self.orchestrator.generate(
            entity=request.entity,
            count=request.count,
            workflow_context=request.workflow_context if request.workflow_context else None,
            scenarios=list(request.scenarios) if request.scenarios else None,
            custom_context=request.custom_context,
            include_edge_cases=request.include_edge_cases,
            output_format=request.output_format or "JSON",
            scenario_counts=dict(request.scenario_counts) if request.scenario_counts else None,
        )
        
        return pb2.GenerateTestDataResponse(
            request_id=result.request_id,
            success=result.success,
            data=result.data,
            record_count=result.record_count,
            metadata=pb2.GenerationMetadata(
                generation_path=result.generation_path,
                llm_tokens_used=result.llm_tokens_used,
                generation_time_ms=result.generation_time_ms,
                coherence_score=result.coherence_score,
                domain_context_used=result.domain_context_used,
                scenario_counts=result.scenario_counts,
            ),
            error=result.error or "",
        )
    
    async def HealthCheck(
        self,
        request: pb2.HealthCheckRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.HealthCheckResponse:
        """Health check."""
        components = {"grpc": "healthy"}
        
        # Check Test Data Agent
        try:
            tda_health = await self.test_data_client.health_check()
            components["test_data_agent"] = tda_health.get("status", "unknown")
        except Exception:
            components["test_data_agent"] = "unhealthy"
        
        # Check Weaviate (basic)
        components["weaviate"] = "healthy"  # TODO: Add actual check
        
        overall = "healthy" if all(v == "healthy" for v in components.values()) else "degraded"
        
        return pb2.HealthCheckResponse(
            status=overall,
            components=components,
        )


async def create_server(port: int) -> grpc.aio.Server:
    """Create and configure the gRPC server."""
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ("grpc.max_receive_message_length", 50 * 1024 * 1024),
            ("grpc.max_send_message_length", 50 * 1024 * 1024),
        ],
    )
    
    servicer = EcommerceDomainServicer()
    pb2_grpc.add_EcommerceDomainServiceServicer_to_server(servicer, server)
    
    server.add_insecure_port(f"[::]:{port}")
    
    logger.info("gRPC server created", port=port)
    return server
```

Acceptance Criteria:
- [ ] All RPC methods implemented
- [ ] Dependencies are wired correctly
- [ ] GenerateTestData calls the orchestrator
- [ ] Health check includes all components
```

---

## Phase 5: UI Implementation

The UI tasks follow the same pattern as the Test Data Agent UI. Create equivalent tasks for:

### Task 5.1-5.15: UI Implementation

Follow the same task structure as UI PRD/TASKS from Test Data Agent, with these key differences:

1. **Pages:**
   - Domain Explorer (home)
   - Entity Browser
   - Workflow Explorer
   - Test Data Generator
   - Knowledge Query

2. **API Routes:**
   - /api/domain/entities
   - /api/domain/entities/[name]
   - /api/domain/workflows
   - /api/domain/workflows/[name]
   - /api/domain/query
   - /api/generate
   - /api/health

3. **Components:**
   - Entity explorer with relationship diagram
   - Workflow diagram (steps visualization)
   - Business rules display
   - Edge cases browser
   - Generation form with domain context

4. **Port:** 3001 (to not conflict with Test Data Agent UI on 3000)

---

## Task Checklist

### Phase 1: Service Foundation
- [ ] Task 1.1: Initialize Monorepo Structure
- [ ] Task 1.2: Create Configuration Management
- [ ] Task 1.3: Create Structured Logging
- [ ] Task 1.4: Create gRPC Proto Definition
- [ ] Task 1.5: Create gRPC Server Skeleton
- [ ] Task 1.6: Create Health HTTP Endpoints
- [ ] Task 1.7: Create Main Entry Point
- [ ] Task 1.8: Create Dockerfile
- [ ] Task 1.9: Write Phase 1 Tests

### Phase 2: Domain Model
- [ ] Task 2.1: Create Entity Definitions
- [ ] Task 2.2: Create Workflow Definitions
- [ ] Task 2.3: Create Business Rules
- [ ] Task 2.4: Create Edge Cases

### Phase 3: Knowledge Layer
- [ ] Task 3.1: Create Weaviate Client
- [ ] Task 3.2: Create Knowledge Retriever
- [ ] Task 3.3: Create Knowledge Indexer

### Phase 4: Test Data Agent Integration
- [ ] Task 4.1: Create Test Data Agent Client
- [ ] Task 4.2: Create Context Builder
- [ ] Task 4.3: Create Generation Orchestrator
- [ ] Task 4.4: Update gRPC Service Implementation

### Phase 5: UI Implementation
- [ ] Task 5.1-5.15: Follow Test Data Agent UI pattern

---

## Network Configuration

Both agents must be on the same Docker network:

```yaml
# In ecommerce-domain-agent/docker-compose.yml
networks:
  qa-platform:
    external: true

# Create the network if it doesn't exist:
# docker network create qa-platform
```

Then ensure Test Data Agent is also on this network.

---

## Usage Tips

### Starting a Task

```
I'm building the eCommerce Domain Agent. Here are my specs:
- PRD: ecommerce_prd.md
- Test Data Agent PRD: PRD.md (for contract reference)

Current task:
[Paste task block here]

Implement this task.
```

### Testing Integration

```bash
# Start Test Data Agent first
cd test-data-agent && docker-compose up -d

# Then start eCommerce Agent
cd ecommerce-domain-agent && docker-compose up

# Test the integration
grpcurl -plaintext localhost:9002 ecommerce.domain.v1.EcommerceDomainService/HealthCheck
```
