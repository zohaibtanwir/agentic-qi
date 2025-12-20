# eCommerce Domain Agent

eCommerce Domain Agent for QA Intelligence Platform - A Python microservice that serves as the domain expert for all eCommerce-related QA activities.

## Overview

The eCommerce Domain Agent understands eCommerce business logic, workflows, entities, and edge cases, providing rich domain context to STLC agents (like Test Data Agent) for intelligent test generation.

## Tech Stack

- **Language:** Python 3.11+
- **Framework:** gRPC + FastAPI
- **LLM:** Claude Sonnet 4
- **Knowledge Store:** Weaviate (RAG)

## Quick Start

1. Copy `.env.example` to `.env` and configure:
```bash
cp service/.env.example service/.env
```

2. Start services with Docker Compose:
```bash
docker-compose up
```

3. Service will be available at:
- gRPC: `localhost:9002`
- Health endpoints: `http://localhost:8082/health`

## Development

Install dependencies:
```bash
cd service
pip install -e ".[dev]"
```

Generate protobuf code:
```bash
make proto
```

Run tests:
```bash
make test
```

## Architecture

The agent provides domain expertise through:
- Entity definitions (cart, order, payment, etc.)
- Workflow knowledge (checkout, returns, etc.)
- Business rules and validations
- Edge case scenarios
- Test data generation context

## API

The service exposes gRPC endpoints for:
- Domain context retrieval
- Entity and workflow queries
- Knowledge search
- Test data generation with domain enrichment