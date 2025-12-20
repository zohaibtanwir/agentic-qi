"""Pytest configuration and shared fixtures."""

import asyncio
import os
from pathlib import Path
from typing import Any, AsyncGenerator, Generator

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, Mock

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["LOG_LEVEL"] = "DEBUG"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    from test_cases_agent.config import Settings

    return Settings(
        service_name="test-cases-agent-test",
        environment="test",
        grpc_port=9003,
        http_port=8083,
        log_level="DEBUG",
        anthropic_api_key="test_anthropic_key",
        openai_api_key="test_openai_key",
        gemini_api_key="test_gemini_key",
        default_llm_provider="anthropic",
        weaviate_url="http://localhost:8084",
        domain_agent_host="localhost",
        domain_agent_port=9002,
        test_data_agent_host="localhost",
        test_data_agent_port=9001,
    )


@pytest.fixture
def sample_user_story():
    """Sample user story for testing."""
    return {
        "id": "US-123",
        "title": "User can add items to cart",
        "description": "As a customer, I want to add items to my shopping cart so that I can purchase them",
        "acceptance_criteria": [
            "User can add a single item to cart",
            "User can add multiple items to cart",
            "Cart total updates correctly",
            "User receives confirmation when item is added",
        ],
        "priority": "HIGH",
    }


@pytest.fixture
def sample_api_spec():
    """Sample API specification for testing."""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Shopping Cart API",
            "version": "1.0.0",
        },
        "paths": {
            "/cart/items": {
                "post": {
                    "summary": "Add item to cart",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "product_id": {"type": "string"},
                                        "quantity": {"type": "integer"},
                                    },
                                    "required": ["product_id", "quantity"],
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Item added successfully",
                        },
                        "400": {
                            "description": "Invalid request",
                        },
                    },
                }
            }
        },
    }


@pytest.fixture
def sample_test_case():
    """Sample test case for testing."""
    return {
        "id": "TC-001",
        "title": "Add single item to empty cart",
        "description": "Verify that a user can add a single item to an empty cart",
        "test_type": "FUNCTIONAL",
        "priority": "HIGH",
        "preconditions": ["User is logged in", "Cart is empty", "Product exists"],
        "steps": [
            {
                "step_number": 1,
                "action": "Navigate to product page",
                "expected_result": "Product page is displayed",
            },
            {
                "step_number": 2,
                "action": "Click 'Add to Cart' button",
                "expected_result": "Item is added to cart",
            },
            {
                "step_number": 3,
                "action": "Verify cart count",
                "expected_result": "Cart shows 1 item",
            },
        ],
        "postconditions": ["Cart contains the added item"],
        "test_data": {
            "product_id": "PROD-123",
            "product_name": "Test Product",
            "price": 29.99,
            "quantity": 1,
        },
        "tags": ["cart", "e2e", "smoke"],
    }


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "content": "Generated test case content",
        "tokens_used": 150,
        "model": "claude-3-sonnet",
        "provider": "anthropic",
    }


@pytest.fixture
def mock_domain_context():
    """Mock domain context from Domain Agent."""
    return {
        "entity": "shopping_cart",
        "business_rules": [
            "Cart maximum is 100 items",
            "Cart expires after 24 hours",
            "Minimum order value is $10",
        ],
        "relationships": ["customer", "product", "order"],
        "edge_cases": [
            "Adding item when cart is full",
            "Adding out-of-stock item",
            "Adding item with invalid quantity",
        ],
    }


@pytest.fixture
def mock_test_data():
    """Mock test data from Test Data Agent."""
    return {
        "success": True,
        "data": [
            {
                "product_id": "PROD-001",
                "product_name": "Laptop",
                "price": 999.99,
                "stock": 10,
            },
            {
                "product_id": "PROD-002",
                "product_name": "Mouse",
                "price": 29.99,
                "stock": 100,
            },
        ],
        "record_count": 2,
        "metadata": {
            "generation_path": "llm",
            "tokens_used": 100,
            "coherence_score": 0.95,
        },
    }


@pytest.fixture
def mock_grpc_context():
    """Mock gRPC context for testing."""
    context = MagicMock()
    context.is_active.return_value = True
    context.time_remaining.return_value = 30.0
    context.peer.return_value = "ipv4:127.0.0.1:50051"
    context.invocation_metadata.return_value = [
        ("user-agent", "grpc-python/1.60.0"),
    ]
    return context


@pytest_asyncio.fixture
async def mock_llm_client():
    """Mock LLM client for testing."""
    client = AsyncMock()
    client.generate.return_value = {
        "content": "Generated content",
        "tokens_used": 100,
        "model": "test-model",
    }
    client.is_available.return_value = True
    return client


@pytest_asyncio.fixture
async def mock_domain_agent_client():
    """Mock Domain Agent client for testing."""
    client = AsyncMock()
    client.get_domain_context.return_value = {
        "entity": "test_entity",
        "business_rules": ["rule1", "rule2"],
        "relationships": ["rel1", "rel2"],
    }
    client.get_edge_cases.return_value = {
        "edge_cases": ["edge1", "edge2"],
    }
    return client


@pytest_asyncio.fixture
async def mock_test_data_agent_client():
    """Mock Test Data Agent client for testing."""
    client = AsyncMock()
    client.generate_data.return_value = {
        "success": True,
        "data": [{"id": 1, "name": "test"}],
        "record_count": 1,
    }
    return client


@pytest_asyncio.fixture
async def mock_weaviate_client():
    """Mock Weaviate client for testing."""
    client = AsyncMock()
    client.is_ready.return_value = True
    client.query.return_value = []
    client.add.return_value = True
    return client


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    return tmp_path


@pytest.fixture
def sample_prompt_template():
    """Sample prompt template for testing."""
    return """
    Generate test cases for the following requirement:

    Title: {{ title }}
    Description: {{ description }}

    Acceptance Criteria:
    {% for criterion in acceptance_criteria %}
    - {{ criterion }}
    {% endfor %}

    Please generate {{ count }} test cases.
    """


# Markers for test categories
pytest.mark.unit = pytest.mark.mark("unit")
pytest.mark.integration = pytest.mark.mark("integration")
pytest.mark.slow = pytest.mark.mark("slow")
pytest.mark.llm = pytest.mark.mark("llm")
pytest.mark.grpc = pytest.mark.mark("grpc")