# Test Cases Agent - Backend Service PRD

## Overview

The Test Cases Agent is a Python gRPC microservice that automatically generates comprehensive test case specifications from requirements. It uses LLMs to analyze user stories, acceptance criteria, and API specifications, enriching them with domain knowledge to produce thorough test coverage.

**Important:** This agent generates **test case specifications** (human-readable), NOT automation scripts.

**Scope:** Backend gRPC service only. UI will be a separate project.

---

## Project Info

| Item | Value |
|------|-------|
| Repository | `qa-platform/agents/test-cases-agent` |
| Language | Python 3.11+ |
| Framework | gRPC (grpcio) + FastAPI (health endpoints only) |
| Default LLM | Claude Sonnet 4 (`claude-sonnet-4-20250514`) |
| Alternative LLMs | OpenAI GPT-4, Google Gemini Pro |
| Knowledge Store | Weaviate |
| Issue Tracking | Beads (`bd`) |
| gRPC Port | 9003 |
| HTTP Port | 8083 (health/metrics only) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      TEST CASES AGENT (Backend)                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   gRPC Server (:9003)                                                    │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │  TestCasesService                                                 │  │
│   │  ├── GenerateTestCases()                                         │  │
│   │  ├── GetTestCase()                                               │  │
│   │  ├── ListTestCases()                                             │  │
│   │  ├── StoreTestCases()                                            │  │
│   │  ├── AnalyzeCoverage()                                           │  │
│   │  └── HealthCheck()                                               │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│   Generation Engine                                                      │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │  1. Parse Input (user story / API spec / free-form)              │  │
│   │  2. Fetch Domain Context (from Domain Agent)                     │  │
│   │  3. Analyze Coverage (equivalence, boundary, state)              │  │
│   │  4. Retrieve Patterns (from Weaviate RAG)                        │  │
│   │  5. Generate via LLM (Anthropic / OpenAI / Gemini)               │  │
│   │  6. Deduplicate (against historical cases)                       │  │
│   │  7. Add Test Data (from Test Data Agent)                         │  │
│   │  8. Format Output (Gherkin / Traditional / JSON)                 │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│   LLM Router                                                             │
│   ┌────────────┐  ┌────────────┐  ┌────────────┐                        │
│   │ Anthropic  │  │  OpenAI    │  │  Gemini    │                        │
│   │ (default)  │  │  GPT-4     │  │  Pro       │                        │
│   └────────────┘  └────────────┘  └────────────┘                        │
│                                                                          │
│   Agent Clients (gRPC)                                                   │
│   ┌─────────────────────┐  ┌─────────────────────┐                      │
│   │ Domain Agent Client │  │ Test Data Agent     │                      │
│   │ :9002               │  │ Client :9001        │                      │
│   └─────────────────────┘  └─────────────────────┘                      │
│                                                                          │
│   Knowledge Store (Weaviate)                                             │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │  TestCases │ TestPatterns │ CoveragePatterns                     │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│   HTTP Health (:8083)                                                    │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │  GET /health  │  GET /health/live  │  GET /health/ready          │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
test-cases-agent/
├── README.md
├── Dockerfile
├── pyproject.toml
├── .env.example
│
├── protos/                           # Symlink to /qa-platform/protos
│   ├── test_cases.proto
│   ├── test_data.proto
│   └── ecommerce_domain.proto
│
├── src/
│   └── test_cases_agent/
│       ├── __init__.py
│       ├── main.py                   # Entry point
│       ├── config.py                 # Settings
│       │
│       ├── proto/                    # Generated protobuf code
│       │   ├── __init__.py
│       │   ├── test_cases_pb2.py
│       │   ├── test_cases_pb2_grpc.py
│       │   ├── test_data_pb2.py
│       │   ├── test_data_pb2_grpc.py
│       │   ├── ecommerce_domain_pb2.py
│       │   └── ecommerce_domain_pb2_grpc.py
│       │
│       ├── server/
│       │   ├── __init__.py
│       │   ├── grpc_server.py        # gRPC service implementation
│       │   └── health.py             # FastAPI health endpoints
│       │
│       ├── generator/
│       │   ├── __init__.py
│       │   ├── engine.py             # Main orchestrator
│       │   ├── parser.py             # Parse requirements
│       │   ├── coverage.py           # Coverage analysis
│       │   ├── deduplicator.py       # Check duplicates
│       │   └── formatter.py          # Format output
│       │
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── base.py               # Base interface
│       │   ├── router.py             # Provider router
│       │   ├── anthropic_client.py   # Claude
│       │   ├── openai_client.py      # GPT-4
│       │   └── gemini_client.py      # Gemini
│       │
│       ├── prompts/
│       │   ├── __init__.py
│       │   ├── system.py             # System prompts
│       │   └── templates.py          # Generation templates
│       │
│       ├── knowledge/
│       │   ├── __init__.py
│       │   ├── retriever.py          # RAG retrieval
│       │   ├── indexer.py            # Index patterns
│       │   └── collections.py        # Weaviate schemas
│       │
│       ├── clients/
│       │   ├── __init__.py
│       │   ├── domain_agent.py       # Domain Agent gRPC client
│       │   ├── test_data_agent.py    # Test Data Agent gRPC client
│       │   └── weaviate_client.py    # Weaviate client
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── test_case.py          # TestCase dataclass
│       │   ├── requirement.py        # Requirement models
│       │   └── coverage.py           # Coverage models
│       │
│       └── utils/
│           ├── __init__.py
│           └── logging.py            # Structured logging
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_parser.py
│   │   ├── test_coverage.py
│   │   ├── test_formatter.py
│   │   └── test_llm_router.py
│   └── integration/
│       ├── test_generation.py
│       └── test_grpc_server.py
│
└── k8s/
    ├── deployment.yaml
    ├── service.yaml
    └── configmap.yaml
```

---

## Dependencies

```toml
# pyproject.toml
[project]
name = "test-cases-agent"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    # gRPC
    "grpcio>=1.60.0",
    "grpcio-tools>=1.60.0",
    "grpcio-health-checking>=1.60.0",
    
    # HTTP (health endpoints only)
    "fastapi>=0.109.0",
    "uvicorn>=0.27.0",
    
    # LLM Providers
    "anthropic>=0.40.0",
    "openai>=1.0.0",
    "google-generativeai>=0.3.0",
    
    # Vector DB
    "weaviate-client>=4.0.0",
    
    # Core
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
    "grpcio-testing>=1.60.0",
]
```

---

## gRPC Service Definition

The proto is already in `/qa-platform/protos/test_cases.proto`. Key RPCs:

```protobuf
service TestCasesService {
  // Generate test cases from requirements
  rpc GenerateTestCases(GenerateTestCasesRequest) returns (GenerateTestCasesResponse);
  
  // Get a specific test case by ID
  rpc GetTestCase(GetTestCaseRequest) returns (GetTestCaseResponse);
  
  // List historical test cases
  rpc ListTestCases(ListTestCasesRequest) returns (ListTestCasesResponse);
  
  // Store test cases (for learning)
  rpc StoreTestCases(StoreTestCasesRequest) returns (StoreTestCasesResponse);
  
  // Get coverage analysis for requirements
  rpc AnalyzeCoverage(AnalyzeCoverageRequest) returns (AnalyzeCoverageResponse);
  
  // Health check
  rpc HealthCheck(HealthCheckRequest) returns (HealthCheckResponse);
}
```

### Input Types

| Type | Fields | Use Case |
|------|--------|----------|
| `UserStoryInput` | story, acceptance_criteria[], additional_context | Agile user stories |
| `ApiSpecInput` | spec, spec_format, endpoints[] | OpenAPI/GraphQL specs |
| `FreeFormInput` | requirements | Unstructured text |

### Configuration Options

| Config | Values | Default |
|--------|--------|---------|
| `output_format` | GHERKIN, TRADITIONAL, JSON | GHERKIN |
| `coverage_level` | QUICK, STANDARD, EXHAUSTIVE | STANDARD |
| `test_types` | FUNCTIONAL, NEGATIVE, BOUNDARY, EDGE_CASE, SECURITY, PERFORMANCE | [FUNCTIONAL, NEGATIVE, BOUNDARY] |
| `llm_provider` | anthropic, openai, gemini | anthropic |
| `check_duplicates` | true/false | true |

### Test Data Placement

| Option | Description |
|--------|-------------|
| EMBEDDED | Data appears inline in test steps |
| SEPARATE | Data in separate `test_data` section |
| BOTH | Both embedded and separate |

---

## Configuration

```python
# src/test_cases_agent/config.py

from pydantic_settings import BaseSettings
from pydantic import Field
from enum import Enum


class LLMProvider(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GEMINI = "gemini"


class Settings(BaseSettings):
    # Service
    service_name: str = "test-cases-agent"
    grpc_port: int = 9003
    http_port: int = 8083
    log_level: str = "INFO"
    
    # LLM - Anthropic (default)
    anthropic_api_key: str = Field("", env="ANTHROPIC_API_KEY")
    anthropic_model: str = "claude-sonnet-4-20250514"
    
    # LLM - OpenAI
    openai_api_key: str = Field("", env="OPENAI_API_KEY")
    openai_model: str = "gpt-4-turbo-preview"
    
    # LLM - Gemini
    gemini_api_key: str = Field("", env="GEMINI_API_KEY")
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
```

---

## Component Specifications

### 1. LLM Router

Routes requests to configured provider with fallback support.

```python
class LLMRouter:
    """Routes LLM requests to appropriate provider."""
    
    def __init__(self):
        self.clients = {
            "anthropic": AnthropicClient(),
            "openai": OpenAIClient(),
            "gemini": GeminiClient(),
        }
    
    async def generate(
        self,
        messages: list[LLMMessage],
        provider: str | None = None,
        **kwargs,
    ) -> LLMResponse:
        """Generate using specified or default provider."""
        pass
    
    def get_available_providers(self) -> list[str]:
        """Return providers with valid API keys."""
        pass
```

### 2. Generation Engine

Orchestrates the 8-step pipeline:

```python
class GenerationEngine:
    """Main test case generation orchestrator."""
    
    async def generate(
        self,
        request: GenerateTestCasesRequest,
    ) -> GenerateTestCasesResponse:
        """
        Pipeline:
        1. Parse input
        2. Fetch domain context
        3. Analyze coverage requirements
        4. Retrieve similar patterns (RAG)
        5. Generate via LLM
        6. Deduplicate
        7. Add test data
        8. Format output
        """
        pass
```

### 3. Requirement Parser

Extracts structured information from different input types:

```python
@dataclass
class ParsedRequirement:
    input_type: str  # user_story, api_spec, free_form
    title: str
    description: str
    acceptance_criteria: list[str]
    entities: list[str]      # Extracted entities
    actions: list[str]       # Extracted actions
    validations: list[str]   # Extracted validation rules
    raw_input: str


class RequirementParser:
    def parse_user_story(self, story: str, acs: list[str]) -> ParsedRequirement: ...
    def parse_api_spec(self, spec: str, format: str) -> ParsedRequirement: ...
    def parse_free_form(self, text: str) -> ParsedRequirement: ...
```

### 4. Coverage Analyzer

Applies testing methodologies:

```python
@dataclass
class CoverageStrategy:
    scenarios: list[TestScenario]
    equivalence_classes: list[dict]
    boundary_values: list[dict]
    state_transitions: list[dict]
    error_conditions: list[str]
    edge_cases: list[str]


class CoverageAnalyzer:
    def analyze(
        self,
        requirement: ParsedRequirement,
        coverage_level: str,
        test_types: list[str],
        domain_edge_cases: list[str],
    ) -> CoverageStrategy:
        """
        Applies:
        - Equivalence partitioning
        - Boundary value analysis
        - State transition testing
        - Error guessing
        - Domain edge cases
        """
        pass
```

### 5. Knowledge Retriever (RAG)

Retrieves similar test cases and patterns from Weaviate:

```python
class KnowledgeRetriever:
    async def find_similar_test_cases(
        self,
        requirement_text: str,
        limit: int = 10,
    ) -> list[SimilarTestCase]: ...
    
    async def find_patterns(
        self,
        requirement_text: str,
        pattern_type: str | None = None,
    ) -> list[TestPattern]: ...
    
    async def check_duplicates(
        self,
        test_case_title: str,
        threshold: float = 0.85,
    ) -> list[SimilarTestCase]: ...
```

### 6. Output Formatter

Formats test cases to requested format:

```python
class TestCaseFormatter:
    def format(
        self,
        test_cases: list[TestCase],
        output_format: str,  # gherkin, traditional, json
    ) -> list[TestCase]:
        """Add formatted output to each test case."""
        pass
    
    def to_gherkin(self, tc: TestCase) -> str: ...
    def to_traditional(self, tc: TestCase) -> str: ...
```

---

## Weaviate Collections

```python
COLLECTIONS = {
    "TestCases": {
        "description": "Historical test cases for learning and deduplication",
        "properties": [
            {"name": "test_case_id", "type": "text"},
            {"name": "title", "type": "text"},
            {"name": "description", "type": "text"},
            {"name": "requirement_text", "type": "text"},
            {"name": "domain", "type": "keyword"},
            {"name": "entity", "type": "keyword"},
            {"name": "test_type", "type": "keyword"},
            {"name": "format", "type": "keyword"},
            {"name": "priority", "type": "keyword"},
            {"name": "content_json", "type": "text"},
            {"name": "tags", "type": "text[]"},
            {"name": "source", "type": "keyword"},
            {"name": "quality_score", "type": "number"},
            {"name": "created_at", "type": "date"},
        ],
    },
    "TestPatterns": {
        "description": "High-quality test patterns and templates",
        "properties": [
            {"name": "pattern_id", "type": "text"},
            {"name": "pattern_type", "type": "keyword"},
            {"name": "domain", "type": "keyword"},
            {"name": "entity", "type": "keyword"},
            {"name": "template", "type": "text"},
            {"name": "example", "type": "text"},
            {"name": "effectiveness_score", "type": "number"},
        ],
    },
}
```

---

## Agent Integrations

### Domain Agent Client

```python
class DomainAgentClient:
    """gRPC client for eCommerce Domain Agent."""
    
    async def get_domain_context(
        self,
        entity: str,
        workflow: str = "",
    ) -> dict:
        """Get business rules, relationships, edge cases."""
        pass
    
    async def get_entity(self, entity_name: str) -> dict:
        """Get entity details with fields, validations."""
        pass
    
    async def get_edge_cases(
        self,
        entity: str = "",
        workflow: str = "",
    ) -> list[dict]:
        """Get edge cases for testing."""
        pass
```

### Test Data Agent Client

```python
class TestDataAgentClient:
    """gRPC client for Test Data Agent."""
    
    async def generate_data(
        self,
        entity: str,
        count: int,
        context: str,
        scenarios: list[str] | None = None,
    ) -> dict:
        """Generate test data for a scenario."""
        pass
```

---

## HTTP Health Endpoints

Minimal FastAPI app for health checks (no business logic):

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Overall service health |
| `GET /health/live` | Kubernetes liveness probe |
| `GET /health/ready` | Kubernetes readiness probe |
| `GET /metrics` | Prometheus metrics (optional) |

```python
# Health response
{
    "status": "healthy",  # healthy, degraded, unhealthy
    "components": {
        "grpc": "healthy",
        "weaviate": "healthy",
        "domain_agent": "healthy",
        "test_data_agent": "healthy",
        "llm_anthropic": "healthy",
        "llm_openai": "not_configured",
        "llm_gemini": "not_configured"
    }
}
```

---

## Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy source
COPY src/ src/

# Generate proto (or copy pre-generated)
COPY protos/ protos/
RUN python -m grpc_tools.protoc \
    -I./protos \
    --python_out=./src/test_cases_agent/proto \
    --grpc_python_out=./src/test_cases_agent/proto \
    ./protos/*.proto

# Run
EXPOSE 9003 8083
CMD ["python", "-m", "test_cases_agent.main"]
```

---

## Environment Variables

```bash
# .env.example

# Service
GRPC_PORT=9003
HTTP_PORT=8083
LOG_LEVEL=INFO

# LLM Providers
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Weaviate
WEAVIATE_URL=http://localhost:8084

# Agent connections
DOMAIN_AGENT_HOST=localhost
DOMAIN_AGENT_PORT=9002
TEST_DATA_AGENT_HOST=localhost
TEST_DATA_AGENT_PORT=9001
```

---

## Testing Strategy

### Unit Tests

| Component | Test Focus |
|-----------|------------|
| `RequirementParser` | Parse different input types correctly |
| `CoverageAnalyzer` | Apply coverage techniques, respect levels |
| `TestCaseFormatter` | Generate valid Gherkin/Traditional/JSON |
| `LLMRouter` | Route to correct provider, handle missing keys |
| `Deduplicator` | Detect similar test cases above threshold |

### Integration Tests

| Test | Description |
|------|-------------|
| `test_generate_from_user_story` | Full pipeline with user story input |
| `test_generate_from_api_spec` | Full pipeline with OpenAPI spec |
| `test_domain_agent_integration` | Fetch context from Domain Agent |
| `test_test_data_integration` | Get test data from Test Data Agent |
| `test_weaviate_storage` | Store and retrieve test cases |

### Test Fixtures

```python
# conftest.py

@pytest.fixture
def sample_user_story():
    return {
        "story": "As a customer, I want to add items to my cart so that I can purchase them later",
        "acceptance_criteria": [
            "Customer can add any available product to cart",
            "Cart shows updated total after adding item",
            "Customer cannot add out-of-stock items",
        ]
    }

@pytest.fixture
def mock_domain_agent():
    """Mock Domain Agent responses."""
    pass

@pytest.fixture
def mock_llm_response():
    """Mock LLM generation response."""
    pass
```

---

## Beads Integration

This project uses Beads for issue tracking. See `/qa-platform/AGENTS.md` for full instructions.

```bash
# Find ready work
bd ready

# Create issue during work
bd create "Implement LLM router" -t task -p 1

# Update status
bd update <id> --status in_progress

# Complete work
bd close <id> --reason "Implemented"

# Sync before ending session
bd sync
```

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Generation latency | < 30s for 10 test cases |
| gRPC request latency (p99) | < 100ms for health check |
| Coverage completeness | > 90% of ACs covered |
| Duplicate detection accuracy | > 95% |
| Test pass rate | > 90% unit, > 80% integration |

---

## Out of Scope (This PRD)

| Item | Notes |
|------|-------|
| UI | Separate PRD |
| REST API / BFF | UI will have its own BFF |
| Jira integration | V2 |
| Batch processing | V2 |
| Test automation scripts | Different agent |

---

## Ports Summary

| Service | gRPC | HTTP |
|---------|------|------|
| Test Data Agent | 9001 | 8081 |
| eCommerce Domain Agent | 9002 | 8082 |
| **Test Cases Agent** | **9003** | **8083** |
