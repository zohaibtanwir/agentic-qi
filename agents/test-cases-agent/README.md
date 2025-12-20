# Test Cases Agent

The Test Cases Agent is a Python gRPC microservice that generates comprehensive test case specifications using LLMs. It's part of the QA Platform monorepo and integrates with the Test Data Agent and eCommerce Domain Agent.

## Features

- 🤖 Multi-LLM support (Anthropic Claude, OpenAI GPT-4, Google Gemini)
- 📝 Generate test cases from user stories, API specs, or free-form requirements
- 🔗 Integration with Domain Agent for domain expertise
- 📊 Integration with Test Data Agent for realistic test data
- 🧠 Knowledge base using Weaviate for learning from past test cases
- 📈 Coverage analysis to ensure comprehensive testing
- 🎯 Smart test case prioritization

## Architecture

```
Test Cases Agent (:9003)
    ├── gRPC Server (test_cases.proto)
    ├── LLM Router (Anthropic, OpenAI, Gemini)
    ├── Domain Agent Client (:9002)
    ├── Test Data Agent Client (:9001)
    └── Weaviate Knowledge Base (:8084)
```

## Installation

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Weaviate instance
- API keys for LLM providers

### Setup

1. Clone the repository and navigate to the agent:
```bash
cd agents/test-cases-agent
```

2. Install dependencies:
```bash
pip install -e ".[dev]"
```

3. Copy environment template and configure:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

4. Generate proto files:
```bash
python -m grpc_tools.protoc \
    -I./protos \
    --python_out=./src/test_cases_agent/proto \
    --grpc_python_out=./src/test_cases_agent/proto \
    ./protos/test_cases.proto \
    ./protos/test_data.proto \
    ./protos/ecommerce_domain.proto
```

5. Run the service:
```bash
python -m test_cases_agent
```

## Usage

### gRPC API

The agent exposes the following gRPC methods:

- `GenerateTestCases` - Generate test cases from requirements
- `GetTestCase` - Retrieve a specific test case
- `ListTestCases` - List test cases with filters
- `StoreTestCases` - Store test cases for learning
- `AnalyzeCoverage` - Analyze requirement coverage

### Example Request

```python
import grpc
from test_cases_agent.proto import test_cases_pb2, test_cases_pb2_grpc

channel = grpc.insecure_channel('localhost:9003')
stub = test_cases_pb2_grpc.TestCasesServiceStub(channel)

request = test_cases_pb2.GenerateTestCasesRequest(
    user_story={
        "id": "US-123",
        "title": "User can add items to cart",
        "description": "As a customer, I want to add items to my shopping cart",
        "acceptance_criteria": [
            "User can add single item",
            "User can add multiple items",
            "Cart updates correctly"
        ]
    },
    test_types=["FUNCTIONAL", "EDGE_CASE"],
    count=5
)

response = stub.GenerateTestCases(request)
for test_case in response.test_cases:
    print(f"Test: {test_case.title}")
```

## Testing

Run the test suite:
```bash
# All tests with coverage
pytest tests/ -v --cov=src/test_cases_agent --cov-report=html

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v
```

## Configuration

Configuration is managed through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `GRPC_PORT` | gRPC server port | 9003 |
| `HTTP_PORT` | HTTP health check port | 8083 |
| `LOG_LEVEL` | Logging level | INFO |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `GEMINI_API_KEY` | Google Gemini API key | - |
| `WEAVIATE_URL` | Weaviate instance URL | http://localhost:8084 |
| `DOMAIN_AGENT_HOST` | Domain Agent host | localhost |
| `DOMAIN_AGENT_PORT` | Domain Agent port | 9002 |
| `TEST_DATA_AGENT_HOST` | Test Data Agent host | localhost |
| `TEST_DATA_AGENT_PORT` | Test Data Agent port | 9001 |

## Development

### Code Style

We use Black for formatting and Ruff for linting:
```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

### Project Structure

```
test-cases-agent/
├── src/test_cases_agent/
│   ├── proto/        # Generated proto files
│   ├── server/       # gRPC server implementation
│   ├── generator/    # Test case generation engine
│   ├── llm/          # LLM provider clients
│   ├── prompts/      # Prompt templates
│   ├── knowledge/    # Weaviate knowledge base
│   ├── clients/      # External service clients
│   ├── models/       # Data models
│   └── utils/        # Utility functions
├── tests/
│   ├── unit/         # Unit tests
│   └── integration/  # Integration tests
└── docs/
    ├── PRD.md        # Product Requirements
    └── TASKS.md      # Implementation tasks
```

## Docker

Build and run with Docker:
```bash
# Build image
docker build -t test-cases-agent:latest .

# Run container
docker run -p 9003:9003 -p 8083:8083 \
    -e ANTHROPIC_API_KEY=your_key \
    test-cases-agent:latest
```

## Health Check

The service exposes health endpoints:

- gRPC: Use the standard gRPC health check protocol
- HTTP: `GET http://localhost:8083/health`

## License

MIT