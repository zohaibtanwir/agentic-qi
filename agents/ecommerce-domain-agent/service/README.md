# eCommerce Domain Agent

A domain-specific AI agent for generating intelligent test data and providing domain knowledge for e-commerce testing scenarios.

## Overview

The eCommerce Domain Agent provides:

- **Test Data Generation**: Generate realistic test data for e-commerce entities (Cart, Order, Payment, Inventory, Customer, Shipping)
- **Domain Knowledge Search**: Search business rules, edge cases, workflows, and entity definitions
- **Context Enrichment**: Enrich test scenarios with domain-specific context using RAG (Retrieval-Augmented Generation)
- **Business Rules Validation**: Validate test data against e-commerce business rules

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                           │
│                    localhost:3000                               │
└─────────────────────┬───────────────────────────────────────────┘
                      │ gRPC-Web
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Envoy Proxy                                  │
│                    localhost:8080                               │
└─────────────────────┬───────────────────────────────────────────┘
                      │ gRPC
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              eCommerce Domain Agent                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   gRPC Server   │  │   REST API      │  │   Health API    │ │
│  │   port:9002     │  │   port:8082     │  │   port:8082     │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           │                    │                    │          │
│  ┌────────▼────────────────────▼────────────────────▼────────┐ │
│  │                    Core Services                          │ │
│  │  • Generation Orchestrator                                │ │
│  │  • Knowledge Retriever                                    │ │
│  │  • Context Enricher                                       │ │
│  │  • Business Rules Validator                               │ │
│  └────────┬──────────────────────────────────────────────────┘ │
└───────────┼─────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Weaviate (Vector DB)                         │
│                    localhost:8081                               │
│  Collections:                                                   │
│  • EcommerceRule      • EcommerceEdgeCase                      │
│  • EcommerceEntity    • EcommerceWorkflow                      │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.12+
- Docker (for Weaviate)
- Node.js 18+ (for frontend)

### 1. Start Weaviate

```bash
docker run -d \
  --name weaviate \
  -p 8081:8080 \
  -p 50051:50051 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH=/var/lib/weaviate \
  semitechnologies/weaviate:latest
```

### 2. Install Dependencies

```bash
cd agents/ecommerce-domain-agent/service
pip install -e ".[dev]"
```

### 3. Seed Knowledge Base

```bash
python -m ecommerce_agent.knowledge.seed_knowledge
```

### 4. Start the Service

```bash
python -m ecommerce_agent.main
```

The service will start:
- gRPC server on port 9002
- HTTP/REST API on port 8082

### 5. Verify Health

```bash
curl http://localhost:8082/health
```

## API Documentation

### REST API

Once the service is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8082/docs
- **ReDoc**: http://localhost:8082/redoc
- **OpenAPI JSON**: http://localhost:8082/openapi.json

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health status |
| `/health/live` | GET | Kubernetes liveness probe |
| `/health/ready` | GET | Kubernetes readiness probe |
| `/api/knowledge/search` | POST | Search domain knowledge |
| `/api/knowledge/stats` | GET | Knowledge base statistics |

### gRPC API

The gRPC service is defined in `protos/ecommerce_domain.proto`. Key RPC methods:

| Method | Description |
|--------|-------------|
| `ListEntities` | List all domain entities |
| `GetEntity` | Get entity details by name |
| `ListWorkflows` | List all business workflows |
| `GetWorkflow` | Get workflow details by name |
| `GenerateTestData` | Generate test data for an entity |
| `GetDomainContext` | Get enriched domain context |
| `SearchKnowledge` | Search the knowledge base |

## Domain Entities

The agent supports the following e-commerce entities:

| Entity | Category | Description |
|--------|----------|-------------|
| Cart | Transactional | Shopping cart before checkout |
| Order | Transactional | Completed purchase |
| Payment | Financial | Payment transactions |
| Inventory | Catalog | Stock level tracking |
| Customer | Core | Customer profiles |
| Shipping | Fulfillment | Delivery information |

## Configuration

Configuration is loaded from environment variables or `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `GRPC_PORT` | 9002 | gRPC server port |
| `HTTP_PORT` | 8082 | HTTP/REST API port |
| `WEAVIATE_URL` | http://weaviate:8080 | Weaviate connection URL |
| `ANTHROPIC_API_KEY` | - | Claude API key (for LLM features) |
| `LOG_LEVEL` | INFO | Logging level |

## Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/ecommerce_agent --cov-report=html

# Run specific test file
pytest tests/test_business_rules.py -v
```

### Project Structure

```
service/
├── src/ecommerce_agent/
│   ├── clients/          # External service clients
│   │   ├── weaviate_client.py
│   │   └── test_data_client.py
│   ├── domain/           # Domain models and definitions
│   │   ├── entities.py
│   │   ├── workflows.py
│   │   └── business_rules.py
│   ├── knowledge/        # Knowledge management
│   │   ├── retriever.py
│   │   ├── indexer.py
│   │   └── collections.py
│   ├── orchestrator/     # Business logic orchestration
│   │   ├── generator.py
│   │   ├── business_rules.py
│   │   └── schema_builder.py
│   ├── server/           # Server implementations
│   │   ├── grpc_server.py
│   │   ├── health.py
│   │   └── knowledge_api.py
│   └── config.py         # Configuration management
├── tests/                # Test suite
├── protos/               # Protocol buffer definitions
└── pyproject.toml        # Project configuration
```

### Code Quality

```bash
# Format code
black src/ tests/

# Type checking
mypy src/

# Linting
ruff check src/
```

## Testing Coverage

Current test coverage: **65%** (323 tests)

Key modules with high coverage:
- `weaviate_client.py`: 100%
- `business_rules.py`: 99%
- `knowledge_api.py`: 98%
- `retriever.py`: 96%

## Troubleshooting

### Weaviate Connection Issues

```bash
# Check if Weaviate is running
curl http://localhost:8081/v1/.well-known/ready

# Check collections
curl http://localhost:8081/v1/schema
```

### Knowledge Base Empty

```bash
# Re-seed the knowledge base
python -m ecommerce_agent.knowledge.seed_knowledge --force-recreate
```

### gRPC Connection Issues

Ensure Envoy proxy is running for gRPC-Web support:
```bash
docker-compose up envoy
```

## License

Internal use only.
