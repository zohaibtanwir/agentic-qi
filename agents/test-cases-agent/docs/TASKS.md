# Test Cases Agent - Backend Implementation Tasks

> **Scope:** Backend gRPC service only. No UI.
> 
> **Usage:** Copy individual tasks into Claude Code / Cursor / Windsurf to implement incrementally.
> 
> **Issue Tracking:** Use Beads (`bd`) - run `bd onboard` before starting.

---

## Phase 0: Project Setup

### Task 0.1: Initialize Project Structure

```
Create the Test Cases Agent project structure in the monorepo.

Location: /qa-platform/agents/test-cases-agent/

Create this structure:

test-cases-agent/
├── README.md
├── Dockerfile
├── pyproject.toml
├── .env.example
├── src/
│   └── test_cases_agent/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── proto/
│       │   └── __init__.py
│       ├── server/
│       │   └── __init__.py
│       ├── generator/
│       │   └── __init__.py
│       ├── llm/
│       │   └── __init__.py
│       ├── prompts/
│       │   └── __init__.py
│       ├── knowledge/
│       │   └── __init__.py
│       ├── clients/
│       │   └── __init__.py
│       ├── models/
│       │   └── __init__.py
│       └── utils/
│           └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   └── __init__.py
│   └── integration/
│       └── __init__.py
└── k8s/

Create pyproject.toml:
```toml
[project]
name = "test-cases-agent"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "grpcio>=1.60.0",
    "grpcio-tools>=1.60.0",
    "grpcio-health-checking>=1.60.0",
    "fastapi>=0.109.0",
    "uvicorn>=0.27.0",
    "anthropic>=0.40.0",
    "openai>=1.0.0",
    "google-generativeai>=0.3.0",
    "weaviate-client>=4.0.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.0.0",
    "structlog>=24.0.0",
    "tenacity>=8.2.0",
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
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.black]
line-length = 100
target-version = ["py311"]
```

Create .env.example:
```
GRPC_PORT=9003
HTTP_PORT=8083
LOG_LEVEL=INFO

ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GEMINI_API_KEY=

WEAVIATE_URL=http://localhost:8084

DOMAIN_AGENT_HOST=localhost
DOMAIN_AGENT_PORT=9002
TEST_DATA_AGENT_HOST=localhost
TEST_DATA_AGENT_PORT=9001
```

Create README.md with basic project info.

Acceptance Criteria:
- [ ] All directories created with __init__.py
- [ ] pyproject.toml complete with all dependencies
- [ ] .env.example has all variables
- [ ] Can run: pip install -e ".[dev]"
```

---

### Task 0.2: Generate Proto Code

```
Generate Python code from the proto files.

The proto files are in /qa-platform/protos/:
- test_cases.proto (this agent's API)
- test_data.proto (client)
- ecommerce_domain.proto (client)

Create a symlink or copy the protos:
```bash
ln -s ../../../protos ./protos
```

Generate Python code:
```bash
python -m grpc_tools.protoc \
    -I./protos \
    --python_out=./src/test_cases_agent/proto \
    --grpc_python_out=./src/test_cases_agent/proto \
    ./protos/test_cases.proto \
    ./protos/test_data.proto \
    ./protos/ecommerce_domain.proto
```

Fix imports in generated *_grpc.py files:
- Change `import X_pb2` to `from . import X_pb2`

Create src/test_cases_agent/proto/__init__.py:
```python
from .test_cases_pb2 import *
from .test_cases_pb2_grpc import *
from .test_data_pb2 import *
from .test_data_pb2_grpc import *
from .ecommerce_domain_pb2 import *
from .ecommerce_domain_pb2_grpc import *
```

Acceptance Criteria:
- [ ] All three protos generate Python code
- [ ] Imports fixed in _grpc.py files
- [ ] Can import: from test_cases_agent.proto import test_cases_pb2
```

---

### Task 0.3: Create Configuration Module

```
Create the configuration module.

Create src/test_cases_agent/config.py:

```python
from functools import lru_cache
from enum import Enum
from pydantic_settings import BaseSettings
from pydantic import Field


class LLMProvider(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GEMINI = "gemini"


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # Service
    service_name: str = "test-cases-agent"
    grpc_port: int = 9003
    http_port: int = 8083
    log_level: str = "INFO"
    
    # LLM - Anthropic (default)
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    anthropic_model: str = "claude-sonnet-4-20250514"
    
    # LLM - OpenAI
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = "gpt-4-turbo-preview"
    
    # LLM - Gemini
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_model: str = "gemini-pro"
    
    # LLM defaults
    default_llm_provider: LLMProvider = LLMProvider.ANTHROPIC
    llm_max_tokens: int = 4096
    llm_temperature: float = 0.7
    
    # Weaviate
    weaviate_url: str = "http://localhost:8084"
    weaviate_api_key: str = ""
    
    # Domain Agent
    domain_agent_host: str = "localhost"
    domain_agent_port: int = 9002
    domain_agent_timeout: float = 30.0
    
    # Test Data Agent
    test_data_agent_host: str = "localhost"
    test_data_agent_port: int = 9001
    test_data_agent_timeout: float = 30.0
    
    # Generation
    default_coverage_level: str = "standard"
    default_output_format: str = "gherkin"
    max_test_cases_per_request: int = 50
    deduplication_threshold: float = 0.85

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

Acceptance Criteria:
- [ ] Settings loads from environment
- [ ] All LLM providers configurable
- [ ] get_settings() returns cached instance
- [ ] Test: settings = get_settings() works
```

---

### Task 0.4: Create Logging Utility

```
Create structured logging using structlog.

Create src/test_cases_agent/utils/logging.py:

```python
import logging
import structlog
from test_cases_agent.config import get_settings


def setup_logging() -> None:
    """Configure structured logging."""
    settings = get_settings()
    
    # Set log level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if settings.log_level == "DEBUG"
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a logger instance."""
    return structlog.get_logger(name)


def bind_context(**kwargs) -> None:
    """Bind context variables for logging."""
    structlog.contextvars.bind_contextvars(**kwargs)


def clear_context() -> None:
    """Clear context variables."""
    structlog.contextvars.clear_contextvars()
```

Acceptance Criteria:
- [ ] setup_logging() configures structlog
- [ ] get_logger() returns bound logger
- [ ] Logs are JSON in production, pretty in debug
- [ ] Context binding works (request_id, etc.)
```

---

## Phase 1: gRPC Server Foundation

### Task 1.1: Create Health Endpoints (HTTP)

```
Create FastAPI health endpoints.

Create src/test_cases_agent/server/health.py:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Test Cases Agent Health")


class HealthResponse(BaseModel):
    status: str  # healthy, degraded, unhealthy
    components: dict[str, str]


class ComponentHealth:
    """Tracks health of service components."""
    
    def __init__(self):
        self._components: dict[str, str] = {
            "grpc": "unknown",
            "weaviate": "unknown",
            "domain_agent": "unknown",
            "test_data_agent": "unknown",
            "llm_anthropic": "unknown",
            "llm_openai": "unknown",
            "llm_gemini": "unknown",
        }
    
    def set(self, component: str, status: str) -> None:
        self._components[component] = status
    
    def get_all(self) -> dict[str, str]:
        return self._components.copy()
    
    def overall_status(self) -> str:
        statuses = self._components.values()
        if all(s == "healthy" or s == "not_configured" for s in statuses):
            return "healthy"
        if any(s == "unhealthy" for s in statuses):
            return "unhealthy"
        return "degraded"


health_tracker = ComponentHealth()


@app.get("/health", response_model=HealthResponse)
async def health():
    """Overall service health."""
    return HealthResponse(
        status=health_tracker.overall_status(),
        components=health_tracker.get_all(),
    )


@app.get("/health/live")
async def liveness():
    """Kubernetes liveness probe."""
    return {"status": "ok"}


@app.get("/health/ready")
async def readiness():
    """Kubernetes readiness probe."""
    # Check critical components
    components = health_tracker.get_all()
    if components.get("grpc") != "healthy":
        return {"status": "not_ready", "reason": "gRPC not healthy"}, 503
    return {"status": "ready"}
```

Acceptance Criteria:
- [ ] GET /health returns status and components
- [ ] GET /health/live always returns ok
- [ ] GET /health/ready checks critical components
- [ ] ComponentHealth tracks all services
```

---

### Task 1.2: Create gRPC Server Skeleton

```
Create the gRPC server with stub implementations.

Create src/test_cases_agent/server/grpc_server.py:

```python
import grpc
from concurrent import futures

from test_cases_agent.proto import test_cases_pb2 as pb2
from test_cases_agent.proto import test_cases_pb2_grpc as pb2_grpc
from test_cases_agent.utils.logging import get_logger, bind_context, clear_context
from test_cases_agent.server.health import health_tracker

logger = get_logger(__name__)


class TestCasesServicer(pb2_grpc.TestCasesServiceServicer):
    """gRPC service implementation."""
    
    def __init__(self):
        # Dependencies will be injected later
        self.generation_engine = None
        self.knowledge_retriever = None
    
    async def GenerateTestCases(
        self,
        request: pb2.GenerateTestCasesRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.GenerateTestCasesResponse:
        """Generate test cases from requirements."""
        bind_context(request_id=request.request_id, method="GenerateTestCases")
        logger.info("Generating test cases")
        
        try:
            # TODO: Implement with generation engine
            return pb2.GenerateTestCasesResponse(
                request_id=request.request_id,
                success=False,
                error="Not implemented yet",
            )
        except Exception as e:
            logger.exception("Generation failed")
            return pb2.GenerateTestCasesResponse(
                request_id=request.request_id,
                success=False,
                error=str(e),
            )
        finally:
            clear_context()
    
    async def GetTestCase(
        self,
        request: pb2.GetTestCaseRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.GetTestCaseResponse:
        """Get a specific test case."""
        logger.info("Getting test case", test_case_id=request.test_case_id)
        # TODO: Implement
        return pb2.GetTestCaseResponse()
    
    async def ListTestCases(
        self,
        request: pb2.ListTestCasesRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.ListTestCasesResponse:
        """List historical test cases."""
        logger.info("Listing test cases")
        # TODO: Implement
        return pb2.ListTestCasesResponse(test_cases=[], total_count=0)
    
    async def StoreTestCases(
        self,
        request: pb2.StoreTestCasesRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.StoreTestCasesResponse:
        """Store test cases for learning."""
        logger.info("Storing test cases", count=len(request.test_cases))
        # TODO: Implement
        return pb2.StoreTestCasesResponse(success=True, stored_count=0)
    
    async def AnalyzeCoverage(
        self,
        request: pb2.AnalyzeCoverageRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.AnalyzeCoverageResponse:
        """Analyze coverage for requirements."""
        bind_context(request_id=request.request_id, method="AnalyzeCoverage")
        logger.info("Analyzing coverage")
        # TODO: Implement
        return pb2.AnalyzeCoverageResponse(request_id=request.request_id)
    
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
    """Create and configure gRPC server."""
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ("grpc.max_receive_message_length", 50 * 1024 * 1024),
            ("grpc.max_send_message_length", 50 * 1024 * 1024),
        ],
    )
    
    servicer = TestCasesServicer()
    pb2_grpc.add_TestCasesServiceServicer_to_server(servicer, server)
    
    server.add_insecure_port(f"[::]:{port}")
    health_tracker.set("grpc", "healthy")
    
    logger.info("gRPC server created", port=port)
    return server
```

Acceptance Criteria:
- [ ] All RPC methods have stub implementations
- [ ] HealthCheck returns healthy
- [ ] Logging with request_id context
- [ ] Health tracker updated
```

---

### Task 1.3: Create Main Entry Point

```
Create the main entry point that starts both servers.

Create src/test_cases_agent/main.py:

```python
import asyncio
import signal
import uvicorn

from test_cases_agent.config import get_settings
from test_cases_agent.utils.logging import setup_logging, get_logger
from test_cases_agent.server.grpc_server import create_server
from test_cases_agent.server.health import app as health_app

logger = get_logger(__name__)


async def main():
    """Main entry point."""
    setup_logging()
    settings = get_settings()
    
    logger.info(
        "Starting Test Cases Agent",
        grpc_port=settings.grpc_port,
        http_port=settings.http_port,
    )
    
    # Create gRPC server
    grpc_server = await create_server(settings.grpc_port)
    await grpc_server.start()
    logger.info("gRPC server started", port=settings.grpc_port)
    
    # Create HTTP server for health
    config = uvicorn.Config(
        health_app,
        host="0.0.0.0",
        port=settings.http_port,
        log_level="warning",
    )
    http_server = uvicorn.Server(config)
    
    # Handle shutdown
    shutdown_event = asyncio.Event()
    
    def handle_signal(sig):
        logger.info("Shutdown signal received", signal=sig)
        shutdown_event.set()
    
    for sig in (signal.SIGTERM, signal.SIGINT):
        asyncio.get_event_loop().add_signal_handler(
            sig, lambda s=sig: handle_signal(s)
        )
    
    # Run both servers
    try:
        await asyncio.gather(
            http_server.serve(),
            shutdown_event.wait(),
        )
    finally:
        logger.info("Shutting down")
        await grpc_server.stop(grace=5)
        logger.info("Shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
```

Also create src/test_cases_agent/__main__.py:
```python
from test_cases_agent.main import main
import asyncio

asyncio.run(main())
```

Acceptance Criteria:
- [ ] python -m test_cases_agent starts both servers
- [ ] gRPC on port 9003, HTTP on 8083
- [ ] Graceful shutdown on SIGTERM/SIGINT
- [ ] Logs show startup info
```

---

### Task 1.4: Create Dockerfile

```
Create Dockerfile for the service.

Create Dockerfile:

```dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir build && \
    pip install --no-cache-dir .

# Copy source
COPY src/ src/
COPY protos/ protos/

# Generate proto
RUN python -m grpc_tools.protoc \
    -I./protos \
    --python_out=./src/test_cases_agent/proto \
    --grpc_python_out=./src/test_cases_agent/proto \
    ./protos/test_cases.proto \
    ./protos/test_data.proto \
    ./protos/ecommerce_domain.proto

# Fix imports
RUN sed -i 's/^import \(.*\)_pb2/from . import \1_pb2/' \
    src/test_cases_agent/proto/*_grpc.py

# Production image
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app/src /app/src

# Set ownership
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 9003 8083

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8083/health/live || exit 1

CMD ["python", "-m", "test_cases_agent"]
```

Acceptance Criteria:
- [ ] docker build succeeds
- [ ] docker run starts the service
- [ ] Health check passes
- [ ] Runs as non-root user
```

---

## Phase 2: LLM Layer

### Task 2.1: Create Base LLM Interface

```
Create the base LLM client interface.

Create src/test_cases_agent/llm/base.py:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class LLMMessage:
    """Message for LLM conversation."""
    role: str  # system, user, assistant
    content: str


@dataclass
class LLMResponse:
    """Response from LLM."""
    content: str
    model: str
    provider: str
    tokens_used: int
    finish_reason: str
    raw_response: Any = None


class BaseLLMClient(ABC):
    """Base class for LLM clients."""
    
    provider: str
    
    @abstractmethod
    async def generate(
        self,
        messages: list[LLMMessage],
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate completion."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is available."""
        pass
    
    @property
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if API key is set."""
        pass
```

Acceptance Criteria:
- [ ] LLMMessage and LLMResponse defined
- [ ] BaseLLMClient abstract class defined
- [ ] All abstract methods declared
```

---

### Task 2.2: Create Anthropic Client

```
Create the Anthropic Claude client.

Create src/test_cases_agent/llm/anthropic_client.py:

```python
import anthropic
from test_cases_agent.llm.base import BaseLLMClient, LLMMessage, LLMResponse
from test_cases_agent.config import get_settings
from test_cases_agent.utils.logging import get_logger

logger = get_logger(__name__)


class AnthropicClient(BaseLLMClient):
    """Anthropic Claude client."""
    
    provider = "anthropic"
    
    def __init__(self):
        settings = get_settings()
        self._api_key = settings.anthropic_api_key
        self._model = settings.anthropic_model
        self._client = None
        
        if self.is_configured:
            self._client = anthropic.AsyncAnthropic(api_key=self._api_key)
    
    @property
    def is_configured(self) -> bool:
        return bool(self._api_key)
    
    async def generate(
        self,
        messages: list[LLMMessage],
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        if not self._client:
            raise RuntimeError("Anthropic client not configured (missing API key)")
        
        # Separate system message
        system = ""
        conversation = []
        for msg in messages:
            if msg.role == "system":
                system = msg.content
            else:
                conversation.append({"role": msg.role, "content": msg.content})
        
        logger.debug("Calling Anthropic API", model=self._model, messages=len(conversation))
        
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=conversation,
        )
        
        return LLMResponse(
            content=response.content[0].text,
            model=self._model,
            provider=self.provider,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            finish_reason=response.stop_reason,
            raw_response=response,
        )
    
    async def health_check(self) -> bool:
        if not self.is_configured:
            return False
        try:
            await self._client.messages.create(
                model=self._model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}],
            )
            return True
        except Exception as e:
            logger.warning("Anthropic health check failed", error=str(e))
            return False
```

Acceptance Criteria:
- [ ] Client initializes with API key
- [ ] generate() calls Claude API
- [ ] System message handled separately
- [ ] Token usage tracked
- [ ] health_check() works
```

---

### Task 2.3: Create OpenAI Client

```
Create the OpenAI GPT client.

Create src/test_cases_agent/llm/openai_client.py:

Same pattern as Anthropic:
- Use openai.AsyncOpenAI
- Convert messages to OpenAI format
- Track token usage from response.usage.total_tokens
- Implement health_check()

Acceptance Criteria:
- [ ] Client initializes with API key
- [ ] generate() calls OpenAI API
- [ ] Token usage tracked
- [ ] health_check() works
```

---

### Task 2.4: Create Gemini Client

```
Create the Google Gemini client.

Create src/test_cases_agent/llm/gemini_client.py:

- Use google.generativeai
- Convert messages to Gemini format (concatenate with role prefixes)
- Estimate tokens from word count
- Implement health_check()

Acceptance Criteria:
- [ ] Client initializes with API key
- [ ] generate() calls Gemini API
- [ ] Message format conversion works
- [ ] health_check() works
```

---

### Task 2.5: Create LLM Router

```
Create the router that dispatches to providers.

Create src/test_cases_agent/llm/router.py:

```python
from test_cases_agent.llm.base import BaseLLMClient, LLMMessage, LLMResponse
from test_cases_agent.llm.anthropic_client import AnthropicClient
from test_cases_agent.llm.openai_client import OpenAIClient
from test_cases_agent.llm.gemini_client import GeminiClient
from test_cases_agent.config import get_settings, LLMProvider
from test_cases_agent.utils.logging import get_logger
from test_cases_agent.server.health import health_tracker

logger = get_logger(__name__)


class LLMRouter:
    """Routes requests to LLM providers."""
    
    def __init__(self):
        settings = get_settings()
        self._clients: dict[str, BaseLLMClient] = {
            LLMProvider.ANTHROPIC: AnthropicClient(),
            LLMProvider.OPENAI: OpenAIClient(),
            LLMProvider.GEMINI: GeminiClient(),
        }
        self._default = settings.default_llm_provider
        self._settings = settings
        
        # Update health tracker
        for name, client in self._clients.items():
            status = "healthy" if client.is_configured else "not_configured"
            health_tracker.set(f"llm_{name}", status)
    
    def get_client(self, provider: str | None = None) -> BaseLLMClient:
        """Get client for provider."""
        provider = provider or self._default
        client = self._clients.get(provider)
        
        if not client:
            raise ValueError(f"Unknown provider: {provider}")
        if not client.is_configured:
            raise RuntimeError(f"Provider {provider} not configured")
        
        return client
    
    async def generate(
        self,
        messages: list[LLMMessage],
        provider: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> LLMResponse:
        """Generate using specified or default provider."""
        client = self.get_client(provider)
        
        return await client.generate(
            messages=messages,
            max_tokens=max_tokens or self._settings.llm_max_tokens,
            temperature=temperature or self._settings.llm_temperature,
        )
    
    def get_available_providers(self) -> list[str]:
        """Get providers with valid configuration."""
        return [
            name for name, client in self._clients.items()
            if client.is_configured
        ]
    
    async def health_check_all(self) -> dict[str, bool]:
        """Check health of all configured providers."""
        results = {}
        for name, client in self._clients.items():
            if client.is_configured:
                healthy = await client.health_check()
                results[name] = healthy
                health_tracker.set(f"llm_{name}", "healthy" if healthy else "unhealthy")
        return results
```

Also create src/test_cases_agent/llm/__init__.py:
```python
from .base import LLMMessage, LLMResponse, BaseLLMClient
from .router import LLMRouter
from .anthropic_client import AnthropicClient
from .openai_client import OpenAIClient
from .gemini_client import GeminiClient

__all__ = [
    "LLMMessage",
    "LLMResponse", 
    "BaseLLMClient",
    "LLMRouter",
    "AnthropicClient",
    "OpenAIClient",
    "GeminiClient",
]
```

Acceptance Criteria:
- [ ] Router initializes all clients
- [ ] get_client() returns correct client
- [ ] generate() delegates to provider
- [ ] get_available_providers() works
- [ ] Health tracker updated
```

---

## Phase 3: Agent Clients

### Task 3.1: Create Domain Agent Client

```
Create gRPC client for eCommerce Domain Agent.

Create src/test_cases_agent/clients/domain_agent.py:

```python
import grpc
from typing import Any

from test_cases_agent.proto import ecommerce_domain_pb2 as pb2
from test_cases_agent.proto import ecommerce_domain_pb2_grpc as pb2_grpc
from test_cases_agent.config import get_settings
from test_cases_agent.utils.logging import get_logger
from test_cases_agent.server.health import health_tracker

logger = get_logger(__name__)


class DomainAgentClient:
    """gRPC client for Domain Agent."""
    
    def __init__(self):
        settings = get_settings()
        self._host = settings.domain_agent_host
        self._port = settings.domain_agent_port
        self._timeout = settings.domain_agent_timeout
        self._channel = None
        self._stub = None
    
    async def _ensure_connected(self):
        if self._channel is None:
            target = f"{self._host}:{self._port}"
            self._channel = grpc.aio.insecure_channel(target)
            self._stub = pb2_grpc.EcommerceDomainServiceStub(self._channel)
            logger.info("Connected to Domain Agent", target=target)
    
    async def get_domain_context(
        self,
        request_id: str,
        entity: str,
        workflow: str = "",
        scenario: str = "",
        aspects: list[str] | None = None,
    ) -> dict[str, Any]:
        """Get domain context for test generation."""
        await self._ensure_connected()
        
        request = pb2.DomainContextRequest(
            request_id=request_id,
            entity=entity,
            workflow=workflow,
            scenario=scenario,
            aspects=aspects or [],
        )
        
        response = await self._stub.GetDomainContext(
            request, timeout=self._timeout
        )
        
        return {
            "context": response.context,
            "rules": [
                {
                    "id": r.id,
                    "name": r.name,
                    "description": r.description,
                    "constraint": r.constraint,
                    "severity": r.severity,
                }
                for r in response.rules
            ],
            "relationships": [
                {
                    "source": r.source_entity,
                    "target": r.target_entity,
                    "type": r.relationship_type,
                }
                for r in response.relationships
            ],
            "edge_cases": list(response.edge_cases),
        }
    
    async def get_entity(
        self,
        entity_name: str,
        include_rules: bool = True,
        include_edge_cases: bool = True,
    ) -> dict[str, Any]:
        """Get entity details."""
        await self._ensure_connected()
        
        request = pb2.EntityRequest(
            entity_name=entity_name,
            include_relationships=True,
            include_rules=include_rules,
            include_edge_cases=include_edge_cases,
        )
        
        response = await self._stub.GetEntity(request, timeout=self._timeout)
        entity = response.entity
        
        return {
            "name": entity.name,
            "description": entity.description,
            "fields": [
                {"name": f.name, "type": f.type, "required": f.required}
                for f in entity.fields
            ],
            "rules": [
                {"id": r.id, "constraint": r.constraint}
                for r in entity.rules
            ],
            "edge_cases": list(entity.edge_cases),
            "test_scenarios": list(entity.test_scenarios),
        }
    
    async def get_edge_cases(
        self,
        entity: str = "",
        workflow: str = "",
    ) -> list[dict[str, Any]]:
        """Get edge cases."""
        await self._ensure_connected()
        
        request = pb2.EdgeCasesRequest(entity=entity, workflow=workflow)
        response = await self._stub.GetEdgeCases(request, timeout=self._timeout)
        
        return [
            {
                "id": ec.id,
                "name": ec.name,
                "description": ec.description,
                "test_approach": ec.test_approach,
                "expected_behavior": ec.expected_behavior,
                "severity": ec.severity,
            }
            for ec in response.edge_cases
        ]
    
    async def health_check(self) -> bool:
        """Check Domain Agent health."""
        try:
            await self._ensure_connected()
            response = await self._stub.HealthCheck(
                pb2.HealthCheckRequest(), timeout=5
            )
            healthy = response.status == "healthy"
            health_tracker.set("domain_agent", "healthy" if healthy else "unhealthy")
            return healthy
        except Exception as e:
            logger.warning("Domain Agent health check failed", error=str(e))
            health_tracker.set("domain_agent", "unhealthy")
            return False
    
    async def close(self):
        if self._channel:
            await self._channel.close()
            self._channel = None
```

Acceptance Criteria:
- [ ] Client connects to Domain Agent
- [ ] get_domain_context() works
- [ ] get_entity() works
- [ ] get_edge_cases() works
- [ ] health_check() updates tracker
```

---

### Task 3.2: Create Test Data Agent Client

```
Create gRPC client for Test Data Agent.

Create src/test_cases_agent/clients/test_data_agent.py:

Same pattern as Domain Agent:
- Connect to Test Data Agent on port 9001
- Implement generate_data(entity, count, context, scenarios)
- Implement health_check()
- Update health_tracker

Use test_data.proto messages.

Acceptance Criteria:
- [ ] Client connects to Test Data Agent
- [ ] generate_data() returns test data
- [ ] health_check() works
```

---

## Phase 4: Knowledge Layer

### Task 4.1: Create Weaviate Client

```
Create the Weaviate vector database client.

Create src/test_cases_agent/clients/weaviate_client.py:

```python
import weaviate
from weaviate.classes.config import Configure, Property, DataType
from typing import Any

from test_cases_agent.config import get_settings
from test_cases_agent.utils.logging import get_logger
from test_cases_agent.server.health import health_tracker

logger = get_logger(__name__)


class WeaviateClient:
    """Weaviate vector database client."""
    
    COLLECTIONS = {
        "TestCases": [
            Property(name="test_case_id", data_type=DataType.TEXT),
            Property(name="title", data_type=DataType.TEXT),
            Property(name="description", data_type=DataType.TEXT),
            Property(name="requirement_text", data_type=DataType.TEXT),
            Property(name="domain", data_type=DataType.TEXT),
            Property(name="entity", data_type=DataType.TEXT),
            Property(name="test_type", data_type=DataType.TEXT),
            Property(name="format", data_type=DataType.TEXT),
            Property(name="priority", data_type=DataType.TEXT),
            Property(name="content_json", data_type=DataType.TEXT),
            Property(name="source", data_type=DataType.TEXT),
            Property(name="quality_score", data_type=DataType.NUMBER),
        ],
        "TestPatterns": [
            Property(name="pattern_id", data_type=DataType.TEXT),
            Property(name="pattern_type", data_type=DataType.TEXT),
            Property(name="domain", data_type=DataType.TEXT),
            Property(name="entity", data_type=DataType.TEXT),
            Property(name="template", data_type=DataType.TEXT),
            Property(name="example", data_type=DataType.TEXT),
            Property(name="effectiveness_score", data_type=DataType.NUMBER),
        ],
    }
    
    def __init__(self):
        settings = get_settings()
        self._url = settings.weaviate_url
        self._client = None
    
    async def connect(self):
        """Connect to Weaviate."""
        if self._client is None:
            self._client = weaviate.connect_to_local(
                host=self._url.replace("http://", "").split(":")[0],
                port=int(self._url.split(":")[-1]),
            )
            await self._ensure_collections()
            logger.info("Connected to Weaviate", url=self._url)
    
    async def _ensure_collections(self):
        """Create collections if they don't exist."""
        for name, properties in self.COLLECTIONS.items():
            if not self._client.collections.exists(name):
                self._client.collections.create(
                    name=name,
                    properties=properties,
                    vectorizer_config=Configure.Vectorizer.text2vec_transformers(),
                )
                logger.info("Created collection", name=name)
    
    async def search(
        self,
        collection: str,
        query: str,
        limit: int = 10,
        filters: dict | None = None,
    ) -> list[dict[str, Any]]:
        """Semantic search."""
        await self.connect()
        coll = self._client.collections.get(collection)
        
        response = coll.query.near_text(
            query=query,
            limit=limit,
        )
        
        return [
            {**obj.properties, "_distance": obj.metadata.distance}
            for obj in response.objects
        ]
    
    async def insert(
        self,
        collection: str,
        data: dict[str, Any],
    ) -> str:
        """Insert document."""
        await self.connect()
        coll = self._client.collections.get(collection)
        uuid = coll.data.insert(data)
        return str(uuid)
    
    async def health_check(self) -> bool:
        """Check Weaviate health."""
        try:
            await self.connect()
            healthy = self._client.is_ready()
            health_tracker.set("weaviate", "healthy" if healthy else "unhealthy")
            return healthy
        except Exception as e:
            logger.warning("Weaviate health check failed", error=str(e))
            health_tracker.set("weaviate", "unhealthy")
            return False
    
    def close(self):
        if self._client:
            self._client.close()
            self._client = None
```

Acceptance Criteria:
- [ ] Client connects to Weaviate
- [ ] Collections created on startup
- [ ] search() returns results
- [ ] insert() stores documents
- [ ] health_check() works
```

---

### Task 4.2: Create Knowledge Retriever

```
Create the RAG retriever for test case patterns.

Create src/test_cases_agent/knowledge/retriever.py:

```python
from dataclasses import dataclass
from typing import Any

from test_cases_agent.clients.weaviate_client import WeaviateClient
from test_cases_agent.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class SimilarTestCase:
    id: str
    title: str
    description: str
    test_type: str
    similarity_score: float
    content: dict[str, Any]


@dataclass
class TestPattern:
    id: str
    pattern_type: str
    template: str
    example: str
    effectiveness_score: float


class KnowledgeRetriever:
    """Retrieves test case knowledge from Weaviate."""
    
    def __init__(self, weaviate: WeaviateClient):
        self._weaviate = weaviate
    
    async def find_similar_test_cases(
        self,
        requirement_text: str,
        domain: str | None = None,
        entity: str | None = None,
        limit: int = 10,
    ) -> list[SimilarTestCase]:
        """Find similar historical test cases."""
        results = await self._weaviate.search(
            collection="TestCases",
            query=requirement_text,
            limit=limit,
        )
        
        return [
            SimilarTestCase(
                id=r.get("test_case_id", ""),
                title=r.get("title", ""),
                description=r.get("description", ""),
                test_type=r.get("test_type", ""),
                similarity_score=1 - r.get("_distance", 1),
                content=r,
            )
            for r in results
        ]
    
    async def find_patterns(
        self,
        requirement_text: str,
        pattern_type: str | None = None,
        limit: int = 5,
    ) -> list[TestPattern]:
        """Find relevant test patterns."""
        results = await self._weaviate.search(
            collection="TestPatterns",
            query=requirement_text,
            limit=limit,
        )
        
        return [
            TestPattern(
                id=r.get("pattern_id", ""),
                pattern_type=r.get("pattern_type", ""),
                template=r.get("template", ""),
                example=r.get("example", ""),
                effectiveness_score=r.get("effectiveness_score", 0),
            )
            for r in results
        ]
    
    async def check_duplicates(
        self,
        test_case_title: str,
        threshold: float = 0.85,
    ) -> list[SimilarTestCase]:
        """Check for duplicate test cases."""
        similar = await self.find_similar_test_cases(
            requirement_text=test_case_title,
            limit=5,
        )
        return [tc for tc in similar if tc.similarity_score >= threshold]
    
    async def store_test_case(
        self,
        test_case: dict[str, Any],
        domain: str,
        entity: str,
        source: str = "generated",
    ) -> str:
        """Store test case for future learning."""
        data = {
            **test_case,
            "domain": domain,
            "entity": entity,
            "source": source,
        }
        return await self._weaviate.insert("TestCases", data)
```

Acceptance Criteria:
- [ ] find_similar_test_cases() works
- [ ] find_patterns() works  
- [ ] check_duplicates() filters by threshold
- [ ] store_test_case() saves to Weaviate
```

---

## Phase 5: Generation Engine

### Task 5.1: Create Data Models

```
Create dataclasses for test cases and requirements.

Create src/test_cases_agent/models/test_case.py:

```python
from dataclasses import dataclass, field
from typing import Any
import json


@dataclass
class TestStep:
    order: int
    action: str
    expected_result: str
    test_data: str = ""


@dataclass
class TestDataItem:
    field: str
    value: str
    description: str = ""


@dataclass
class TestCase:
    id: str
    title: str
    description: str
    type: str  # functional, negative, boundary, edge_case
    priority: str  # high, medium, low
    preconditions: list[str] = field(default_factory=list)
    steps: list[TestStep] = field(default_factory=list)
    expected_result: str = ""
    postconditions: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    requirement_id: str = ""
    gherkin: str = ""
    test_data: list[TestDataItem] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "type": self.type,
            "priority": self.priority,
            "preconditions": self.preconditions,
            "steps": [
                {"order": s.order, "action": s.action, "expected_result": s.expected_result, "test_data": s.test_data}
                for s in self.steps
            ],
            "expected_result": self.expected_result,
            "postconditions": self.postconditions,
            "tags": self.tags,
            "requirement_id": self.requirement_id,
            "gherkin": self.gherkin,
            "test_data": [
                {"field": d.field, "value": d.value, "description": d.description}
                for d in self.test_data
            ],
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TestCase":
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            type=data.get("type", "functional"),
            priority=data.get("priority", "medium"),
            preconditions=data.get("preconditions", []),
            steps=[
                TestStep(**s) for s in data.get("steps", [])
            ],
            expected_result=data.get("expected_result", ""),
            postconditions=data.get("postconditions", []),
            tags=data.get("tags", []),
            requirement_id=data.get("requirement_id", ""),
            gherkin=data.get("gherkin", ""),
            test_data=[
                TestDataItem(**d) for d in data.get("test_data", [])
            ],
        )
```

Create src/test_cases_agent/models/requirement.py:

```python
from dataclasses import dataclass, field


@dataclass
class ParsedRequirement:
    input_type: str  # user_story, api_spec, free_form
    title: str
    description: str
    acceptance_criteria: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    validations: list[str] = field(default_factory=list)
    raw_input: str = ""
```

Acceptance Criteria:
- [ ] TestCase dataclass complete
- [ ] to_dict() and from_dict() work
- [ ] ParsedRequirement dataclass complete
```

---

### Task 5.2: Create Requirement Parser

```
Create the parser for different input types.

Create src/test_cases_agent/generator/parser.py:

```python
import re
from test_cases_agent.models.requirement import ParsedRequirement
from test_cases_agent.utils.logging import get_logger

logger = get_logger(__name__)


class RequirementParser:
    """Parses different input types into structured format."""
    
    def parse_user_story(
        self,
        story: str,
        acceptance_criteria: list[str],
        additional_context: str = "",
    ) -> ParsedRequirement:
        """Parse user story input."""
        # Extract title from story
        title = story[:100] if len(story) > 100 else story
        
        # Build description
        description = story
        if additional_context:
            description += f"\n\nContext: {additional_context}"
        
        # Extract entities (nouns after "a/an/the")
        entities = self._extract_entities(story)
        
        # Extract actions (verbs after "want to", "can", "should")
        actions = self._extract_actions(story)
        
        # Extract validations from ACs
        validations = self._extract_validations(acceptance_criteria)
        
        return ParsedRequirement(
            input_type="user_story",
            title=title,
            description=description,
            acceptance_criteria=acceptance_criteria,
            entities=entities,
            actions=actions,
            validations=validations,
            raw_input=story,
        )
    
    def parse_api_spec(
        self,
        spec: str,
        spec_format: str,
        endpoints: list[str] | None = None,
    ) -> ParsedRequirement:
        """Parse API specification."""
        import json
        import yaml
        
        # Parse spec
        if spec_format == "openapi":
            try:
                parsed = json.loads(spec)
            except json.JSONDecodeError:
                parsed = yaml.safe_load(spec)
            
            title = parsed.get("info", {}).get("title", "API Test Cases")
            description = parsed.get("info", {}).get("description", "")
            
            # Extract endpoints as ACs
            acs = []
            paths = parsed.get("paths", {})
            for path, methods in paths.items():
                if endpoints and path not in endpoints:
                    continue
                for method, details in methods.items():
                    if method in ("get", "post", "put", "delete", "patch"):
                        summary = details.get("summary", f"{method.upper()} {path}")
                        acs.append(summary)
        else:
            title = "GraphQL API Test Cases"
            description = spec[:500]
            acs = []
        
        return ParsedRequirement(
            input_type="api_spec",
            title=title,
            description=description,
            acceptance_criteria=acs,
            entities=[],
            actions=[],
            validations=[],
            raw_input=spec,
        )
    
    def parse_free_form(self, requirements: str) -> ParsedRequirement:
        """Parse free-form requirements."""
        lines = requirements.strip().split("\n")
        title = lines[0][:100] if lines else "Requirements"
        
        return ParsedRequirement(
            input_type="free_form",
            title=title,
            description=requirements,
            acceptance_criteria=[],
            entities=self._extract_entities(requirements),
            actions=self._extract_actions(requirements),
            validations=[],
            raw_input=requirements,
        )
    
    def _extract_entities(self, text: str) -> list[str]:
        """Extract potential entities from text."""
        # Simple extraction - look for nouns after articles
        pattern = r'\b(?:a|an|the)\s+(\w+)'
        matches = re.findall(pattern, text.lower())
        return list(set(matches))
    
    def _extract_actions(self, text: str) -> list[str]:
        """Extract potential actions from text."""
        # Look for verbs after common patterns
        pattern = r'(?:want to|can|should|must|will)\s+(\w+)'
        matches = re.findall(pattern, text.lower())
        return list(set(matches))
    
    def _extract_validations(self, acs: list[str]) -> list[str]:
        """Extract validation rules from acceptance criteria."""
        validations = []
        validation_keywords = ["must", "should", "cannot", "valid", "invalid", "required"]
        for ac in acs:
            if any(kw in ac.lower() for kw in validation_keywords):
                validations.append(ac)
        return validations
```

Acceptance Criteria:
- [ ] parse_user_story() extracts entities, actions
- [ ] parse_api_spec() parses OpenAPI JSON/YAML
- [ ] parse_free_form() handles unstructured text
- [ ] All return ParsedRequirement
```

---

### Task 5.3: Create Coverage Analyzer

```
Create the coverage analyzer.

Create src/test_cases_agent/generator/coverage.py:

```python
from dataclasses import dataclass, field
from test_cases_agent.models.requirement import ParsedRequirement
from test_cases_agent.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class TestScenario:
    name: str
    type: str  # functional, negative, boundary, edge_case
    description: str
    priority: str
    inputs: dict = field(default_factory=dict)
    expected_outcome: str = ""


@dataclass
class CoverageStrategy:
    scenarios: list[TestScenario]
    equivalence_classes: list[dict] = field(default_factory=list)
    boundary_values: list[dict] = field(default_factory=list)
    state_transitions: list[dict] = field(default_factory=list)
    error_conditions: list[str] = field(default_factory=list)
    edge_cases: list[str] = field(default_factory=list)


class CoverageAnalyzer:
    """Analyzes requirements for test coverage."""
    
    def analyze(
        self,
        requirement: ParsedRequirement,
        coverage_level: str,
        test_types: list[str],
        domain_edge_cases: list[str] | None = None,
    ) -> CoverageStrategy:
        """Analyze requirement and create coverage strategy."""
        scenarios = []
        
        # Always include happy path
        scenarios.append(TestScenario(
            name="happy_path",
            type="functional",
            description="Verify successful execution with valid inputs",
            priority="high",
        ))
        
        # Add functional scenarios for each AC
        if "functional" in test_types:
            for i, ac in enumerate(requirement.acceptance_criteria):
                scenarios.append(TestScenario(
                    name=f"ac_{i+1}_positive",
                    type="functional",
                    description=f"Verify: {ac}",
                    priority="high",
                ))
        
        # Add negative scenarios
        if "negative" in test_types:
            scenarios.extend(self._generate_negative_scenarios(requirement))
        
        # Add boundary scenarios
        if "boundary" in test_types:
            scenarios.extend(self._generate_boundary_scenarios(requirement))
        
        # Add edge cases from domain
        if "edge_case" in test_types and domain_edge_cases:
            for ec in domain_edge_cases:
                scenarios.append(TestScenario(
                    name=f"edge_{len(scenarios)}",
                    type="edge_case",
                    description=ec,
                    priority="medium",
                ))
        
        # Filter by coverage level
        if coverage_level == "quick":
            scenarios = [s for s in scenarios if s.priority == "high"][:5]
        elif coverage_level == "standard":
            scenarios = scenarios[:15]
        # exhaustive: keep all
        
        return CoverageStrategy(
            scenarios=scenarios,
            equivalence_classes=self._identify_equivalence_classes(requirement),
            boundary_values=self._identify_boundaries(requirement),
            state_transitions=[],
            error_conditions=self._identify_errors(requirement),
            edge_cases=domain_edge_cases or [],
        )
    
    def _generate_negative_scenarios(self, req: ParsedRequirement) -> list[TestScenario]:
        """Generate negative test scenarios."""
        scenarios = []
        
        # Missing required fields
        scenarios.append(TestScenario(
            name="missing_required",
            type="negative",
            description="Verify error when required fields are missing",
            priority="high",
        ))
        
        # Invalid input format
        scenarios.append(TestScenario(
            name="invalid_format",
            type="negative",
            description="Verify error handling for invalid input formats",
            priority="medium",
        ))
        
        return scenarios
    
    def _generate_boundary_scenarios(self, req: ParsedRequirement) -> list[TestScenario]:
        """Generate boundary value scenarios."""
        scenarios = []
        
        scenarios.append(TestScenario(
            name="min_boundary",
            type="boundary",
            description="Test minimum valid values",
            priority="medium",
        ))
        
        scenarios.append(TestScenario(
            name="max_boundary",
            type="boundary",
            description="Test maximum valid values",
            priority="medium",
        ))
        
        return scenarios
    
    def _identify_equivalence_classes(self, req: ParsedRequirement) -> list[dict]:
        """Identify equivalence classes."""
        return [
            {"name": "valid_inputs", "description": "All valid input combinations"},
            {"name": "invalid_inputs", "description": "All invalid input combinations"},
        ]
    
    def _identify_boundaries(self, req: ParsedRequirement) -> list[dict]:
        """Identify boundary values."""
        return []
    
    def _identify_errors(self, req: ParsedRequirement) -> list[str]:
        """Identify error conditions."""
        return [
            "Network failure",
            "Timeout",
            "Authentication failure",
            "Authorization failure",
        ]
```

Acceptance Criteria:
- [ ] analyze() returns CoverageStrategy
- [ ] Coverage level filters scenarios
- [ ] Test types filter what's generated
- [ ] Domain edge cases included
```

---

### Task 5.4: Create Output Formatter

```
Create the test case formatter.

Create src/test_cases_agent/generator/formatter.py:

```python
from test_cases_agent.models.test_case import TestCase
from test_cases_agent.utils.logging import get_logger

logger = get_logger(__name__)


class TestCaseFormatter:
    """Formats test cases to different output formats."""
    
    def format(
        self,
        test_cases: list[TestCase],
        output_format: str,
    ) -> list[TestCase]:
        """Format test cases to requested format."""
        if output_format == "gherkin":
            return [self._add_gherkin(tc) for tc in test_cases]
        elif output_format == "traditional":
            return test_cases  # Already in traditional format
        else:  # json
            return test_cases
    
    def _add_gherkin(self, tc: TestCase) -> TestCase:
        """Add Gherkin format to test case."""
        lines = []
        
        # Feature
        lines.append(f"Feature: {tc.title}")
        if tc.description:
            lines.append(f"  {tc.description}")
        lines.append("")
        
        # Tags
        tags = " ".join(f"@{tag}" for tag in tc.tags)
        if tags:
            lines.append(f"  {tags}")
        
        # Scenario
        lines.append(f"  Scenario: {tc.title}")
        
        # Given (preconditions)
        for i, precond in enumerate(tc.preconditions):
            keyword = "Given" if i == 0 else "And"
            lines.append(f"    {keyword} {precond}")
        
        # When (steps)
        for i, step in enumerate(tc.steps):
            keyword = "When" if i == 0 else "And"
            lines.append(f"    {keyword} {step.action}")
        
        # Then (expected result)
        lines.append(f"    Then {tc.expected_result}")
        
        tc.gherkin = "\n".join(lines)
        return tc
    
    def format_traditional(self, tc: TestCase) -> str:
        """Format as traditional test case document."""
        lines = [
            f"# {tc.id}: {tc.title}",
            "",
            f"**Type:** {tc.type}",
            f"**Priority:** {tc.priority}",
            "",
            "## Preconditions",
        ]
        
        for p in tc.preconditions:
            lines.append(f"- {p}")
        
        lines.extend(["", "## Steps", ""])
        
        for step in tc.steps:
            lines.append(f"{step.order}. **Action:** {step.action}")
            lines.append(f"   **Expected:** {step.expected_result}")
            if step.test_data:
                lines.append(f"   **Data:** {step.test_data}")
            lines.append("")
        
        lines.extend(["## Expected Result", tc.expected_result])
        
        return "\n".join(lines)
```

Acceptance Criteria:
- [ ] format() handles gherkin, traditional, json
- [ ] Gherkin output is valid .feature syntax
- [ ] Traditional format has clear structure
```

---

### Task 5.5: Create Prompts

```
Create the LLM prompts.

Create src/test_cases_agent/prompts/system.py:

```python
SYSTEM_PROMPT = """You are an expert QA engineer specializing in test case design. Generate comprehensive test cases from requirements.

Your expertise includes:
- Equivalence partitioning
- Boundary value analysis  
- State transition testing
- Error guessing
- Risk-based testing

For each test case, provide:
1. Clear, descriptive title
2. Type (functional/negative/boundary/edge_case)
3. Priority (high/medium/low)
4. Preconditions
5. Step-by-step actions with expected results
6. Overall expected outcome

Output as JSON array:
[
  {
    "id": "TC-001",
    "title": "Descriptive title",
    "description": "What this tests",
    "type": "functional",
    "priority": "high",
    "tags": ["tag1"],
    "preconditions": ["User is logged in"],
    "steps": [
      {"order": 1, "action": "Do something", "expected_result": "Something happens"}
    ],
    "expected_result": "Overall outcome",
    "postconditions": []
  }
]

Generate thorough coverage. Be specific and actionable."""
```

Create src/test_cases_agent/prompts/templates.py:

```python
from test_cases_agent.models.requirement import ParsedRequirement
from test_cases_agent.generator.coverage import CoverageStrategy


def build_generation_prompt(
    requirement: ParsedRequirement,
    strategy: CoverageStrategy,
    domain_context: dict | None = None,
    patterns: list | None = None,
) -> str:
    """Build the generation prompt."""
    parts = []
    
    # Requirement
    parts.append("# Requirement")
    parts.append(requirement.description)
    parts.append("")
    
    # Acceptance Criteria
    if requirement.acceptance_criteria:
        parts.append("# Acceptance Criteria")
        for i, ac in enumerate(requirement.acceptance_criteria, 1):
            parts.append(f"{i}. {ac}")
        parts.append("")
    
    # Domain Context
    if domain_context:
        parts.append("# Domain Context")
        if domain_context.get("context"):
            parts.append(domain_context["context"])
        
        if domain_context.get("rules"):
            parts.append("\n## Business Rules")
            for rule in domain_context["rules"]:
                parts.append(f"- {rule.get('constraint', rule.get('description', ''))}")
        
        if domain_context.get("edge_cases"):
            parts.append("\n## Edge Cases to Cover")
            for ec in domain_context["edge_cases"]:
                parts.append(f"- {ec}")
        parts.append("")
    
    # Coverage Requirements
    parts.append("# Coverage Requirements")
    parts.append(f"Generate {len(strategy.scenarios)} test cases covering:")
    for scenario in strategy.scenarios:
        parts.append(f"- {scenario.type}: {scenario.description}")
    parts.append("")
    
    # Patterns (few-shot examples)
    if patterns:
        parts.append("# Reference Patterns")
        for p in patterns[:2]:
            parts.append(f"## {p.pattern_type}")
            parts.append(p.example)
        parts.append("")
    
    parts.append("Generate comprehensive test cases as JSON array.")
    
    return "\n".join(parts)
```

Acceptance Criteria:
- [ ] SYSTEM_PROMPT defines output format
- [ ] build_generation_prompt() includes all context
- [ ] Domain context and patterns integrated
```

---

### Task 5.6: Create Generation Engine

```
Create the main generation orchestrator.

Create src/test_cases_agent/generator/engine.py:

```python
import json
import time
import uuid
from typing import Any

from test_cases_agent.llm import LLMRouter, LLMMessage
from test_cases_agent.generator.parser import RequirementParser
from test_cases_agent.generator.coverage import CoverageAnalyzer
from test_cases_agent.generator.formatter import TestCaseFormatter
from test_cases_agent.knowledge.retriever import KnowledgeRetriever
from test_cases_agent.clients.domain_agent import DomainAgentClient
from test_cases_agent.clients.test_data_agent import TestDataAgentClient
from test_cases_agent.prompts.system import SYSTEM_PROMPT
from test_cases_agent.prompts.templates import build_generation_prompt
from test_cases_agent.models.test_case import TestCase
from test_cases_agent.utils.logging import get_logger, bind_context

logger = get_logger(__name__)


class GenerationEngine:
    """Main test case generation orchestrator."""
    
    def __init__(
        self,
        llm_router: LLMRouter,
        parser: RequirementParser,
        coverage_analyzer: CoverageAnalyzer,
        formatter: TestCaseFormatter,
        knowledge_retriever: KnowledgeRetriever,
        domain_agent: DomainAgentClient,
        test_data_agent: TestDataAgentClient,
    ):
        self.llm = llm_router
        self.parser = parser
        self.coverage = coverage_analyzer
        self.formatter = formatter
        self.knowledge = knowledge_retriever
        self.domain_agent = domain_agent
        self.test_data_agent = test_data_agent
    
    async def generate(
        self,
        request_id: str,
        input_type: str,
        input_data: dict[str, Any],
        domain_config: dict[str, Any] | None = None,
        generation_config: dict[str, Any] | None = None,
        test_data_config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Generate test cases.
        
        Pipeline:
        1. Parse input
        2. Fetch domain context
        3. Analyze coverage
        4. Retrieve patterns (RAG)
        5. Generate via LLM
        6. Deduplicate
        7. Add test data
        8. Format output
        """
        bind_context(request_id=request_id)
        start_time = time.time()
        
        config = generation_config or {}
        llm_provider = config.get("llm_provider")
        output_format = config.get("output_format", "gherkin")
        coverage_level = config.get("coverage_level", "standard")
        test_types = config.get("test_types", ["functional", "negative", "boundary"])
        check_duplicates = config.get("check_duplicates", True)
        
        try:
            # 1. Parse input
            logger.info("Parsing input", input_type=input_type)
            requirement = self._parse_input(input_type, input_data)
            
            # 2. Fetch domain context
            domain_context = None
            edge_cases = []
            if domain_config and domain_config.get("entity"):
                logger.info("Fetching domain context")
                try:
                    domain_context = await self.domain_agent.get_domain_context(
                        request_id=request_id,
                        entity=domain_config.get("entity", ""),
                        workflow=domain_config.get("workflow", ""),
                    )
                    if domain_config.get("include_edge_cases"):
                        edge_cases = domain_context.get("edge_cases", [])
                except Exception as e:
                    logger.warning("Failed to fetch domain context", error=str(e))
            
            # 3. Analyze coverage
            logger.info("Analyzing coverage", level=coverage_level)
            strategy = self.coverage.analyze(
                requirement=requirement,
                coverage_level=coverage_level,
                test_types=test_types,
                domain_edge_cases=edge_cases,
            )
            
            # 4. Retrieve patterns
            logger.info("Retrieving patterns")
            patterns = await self.knowledge.find_patterns(
                requirement_text=requirement.description,
                limit=3,
            )
            
            # 5. Generate via LLM
            logger.info("Generating via LLM", provider=llm_provider)
            prompt = build_generation_prompt(
                requirement=requirement,
                strategy=strategy,
                domain_context=domain_context,
                patterns=patterns,
            )
            
            messages = [
                LLMMessage(role="system", content=SYSTEM_PROMPT),
                LLMMessage(role="user", content=prompt),
            ]
            
            response = await self.llm.generate(messages=messages, provider=llm_provider)
            test_cases = self._parse_llm_response(response.content)
            
            # 6. Deduplicate
            duplicates_found = 0
            if check_duplicates and test_cases:
                logger.info("Checking duplicates")
                unique_cases = []
                for tc in test_cases:
                    dups = await self.knowledge.check_duplicates(tc.title)
                    if not dups:
                        unique_cases.append(tc)
                    else:
                        duplicates_found += 1
                test_cases = unique_cases
            
            # 7. Add test data (optional)
            if test_data_config and test_data_config.get("generate_test_data"):
                logger.info("Adding test data")
                test_cases = await self._add_test_data(
                    test_cases, domain_config, test_data_config
                )
            
            # 8. Format output
            logger.info("Formatting output", format=output_format)
            test_cases = self.formatter.format(test_cases, output_format)
            
            generation_time = (time.time() - start_time) * 1000
            
            return {
                "request_id": request_id,
                "success": True,
                "test_cases": test_cases,
                "metadata": {
                    "llm_provider": response.provider,
                    "llm_model": response.model,
                    "llm_tokens_used": response.tokens_used,
                    "generation_time_ms": generation_time,
                    "test_cases_generated": len(test_cases),
                    "duplicates_found": duplicates_found,
                    "domain_context_used": bool(domain_context),
                },
            }
            
        except Exception as e:
            logger.exception("Generation failed")
            return {
                "request_id": request_id,
                "success": False,
                "test_cases": [],
                "metadata": {},
                "error": str(e),
            }
    
    def _parse_input(self, input_type: str, data: dict) -> Any:
        """Parse input based on type."""
        if input_type == "user_story":
            return self.parser.parse_user_story(
                story=data.get("story", ""),
                acceptance_criteria=data.get("acceptance_criteria", []),
                additional_context=data.get("additional_context", ""),
            )
        elif input_type == "api_spec":
            return self.parser.parse_api_spec(
                spec=data.get("spec", ""),
                spec_format=data.get("spec_format", "openapi"),
                endpoints=data.get("endpoints"),
            )
        else:
            return self.parser.parse_free_form(data.get("requirements", ""))
    
    def _parse_llm_response(self, content: str) -> list[TestCase]:
        """Parse LLM JSON response into TestCase objects."""
        try:
            # Handle markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            data = json.loads(content.strip())
            
            if isinstance(data, list):
                return [TestCase.from_dict(tc) for tc in data]
            return []
        except json.JSONDecodeError as e:
            logger.error("Failed to parse LLM response", error=str(e))
            return []
    
    async def _add_test_data(
        self,
        test_cases: list[TestCase],
        domain_config: dict | None,
        test_data_config: dict,
    ) -> list[TestCase]:
        """Add test data to test cases."""
        # Implementation depends on test_data_config.placement
        # For now, just return as-is
        return test_cases
```

Acceptance Criteria:
- [ ] Full 8-step pipeline works
- [ ] All steps logged
- [ ] Domain context fetched when configured
- [ ] LLM generates test cases
- [ ] Deduplication works
- [ ] Returns proper response structure
```

---

## Phase 6: Wire Everything Together

### Task 6.1: Update gRPC Server with Dependencies

```
Wire all components into the gRPC server.

Update src/test_cases_agent/server/grpc_server.py:

Add initialization of all dependencies:
- LLMRouter
- RequirementParser
- CoverageAnalyzer
- TestCaseFormatter
- WeaviateClient
- KnowledgeRetriever
- DomainAgentClient
- TestDataAgentClient
- GenerationEngine

Implement GenerateTestCases RPC using GenerationEngine.

Update HealthCheck to include all components.

Acceptance Criteria:
- [ ] All dependencies initialized
- [ ] GenerateTestCases fully implemented
- [ ] HealthCheck returns all component status
- [ ] Error handling in all RPCs
```

---

### Task 6.2: Write Unit Tests

```
Write unit tests for core components.

Create tests for:
- tests/unit/test_parser.py - RequirementParser
- tests/unit/test_coverage.py - CoverageAnalyzer
- tests/unit/test_formatter.py - TestCaseFormatter
- tests/unit/test_llm_router.py - LLMRouter (with mocks)
- tests/unit/test_models.py - TestCase, ParsedRequirement

Use pytest fixtures for common test data.

Acceptance Criteria:
- [ ] >80% coverage on core components
- [ ] Parser tests cover all input types
- [ ] Formatter tests verify output formats
- [ ] LLM router tests use mocks
```

---

### Task 6.3: Write Integration Tests

```
Write integration tests.

Create:
- tests/integration/test_grpc_server.py - Test gRPC endpoints
- tests/integration/test_generation.py - Full pipeline test

Use grpcio-testing for gRPC tests.
Mock external services (Domain Agent, Test Data Agent, LLMs).

Acceptance Criteria:
- [ ] gRPC server starts and responds
- [ ] GenerateTestCases returns valid response
- [ ] HealthCheck works
```

---

## Task Checklist

### Phase 0: Project Setup
- [ ] Task 0.1: Initialize Project Structure
- [ ] Task 0.2: Generate Proto Code
- [ ] Task 0.3: Create Configuration Module
- [ ] Task 0.4: Create Logging Utility

### Phase 1: gRPC Server Foundation
- [ ] Task 1.1: Create Health Endpoints
- [ ] Task 1.2: Create gRPC Server Skeleton
- [ ] Task 1.3: Create Main Entry Point
- [ ] Task 1.4: Create Dockerfile

### Phase 2: LLM Layer
- [ ] Task 2.1: Create Base LLM Interface
- [ ] Task 2.2: Create Anthropic Client
- [ ] Task 2.3: Create OpenAI Client
- [ ] Task 2.4: Create Gemini Client
- [ ] Task 2.5: Create LLM Router

### Phase 3: Agent Clients
- [ ] Task 3.1: Create Domain Agent Client
- [ ] Task 3.2: Create Test Data Agent Client

### Phase 4: Knowledge Layer
- [ ] Task 4.1: Create Weaviate Client
- [ ] Task 4.2: Create Knowledge Retriever

### Phase 5: Generation Engine
- [ ] Task 5.1: Create Data Models
- [ ] Task 5.2: Create Requirement Parser
- [ ] Task 5.3: Create Coverage Analyzer
- [ ] Task 5.4: Create Output Formatter
- [ ] Task 5.5: Create Prompts
- [ ] Task 5.6: Create Generation Engine

### Phase 6: Wire & Test
- [ ] Task 6.1: Update gRPC Server with Dependencies
- [ ] Task 6.2: Write Unit Tests
- [ ] Task 6.3: Write Integration Tests

---

## Ports Summary

| Service | gRPC | HTTP |
|---------|------|------|
| Test Data Agent | 9001 | 8081 |
| eCommerce Domain Agent | 9002 | 8082 |
| **Test Cases Agent** | **9003** | **8083** |
