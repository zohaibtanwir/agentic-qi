# eCommerce Domain Agent - Product Requirements Document

## Overview

The eCommerce Domain Agent is a Python microservice that serves as the domain expert for all eCommerce-related QA activities. It understands eCommerce business logic, workflows, entities, and edge cases, providing rich domain context to STLC agents (like Test Data Agent) for intelligent test generation.

**Repository:** `qa-platform/ecommerce-domain-agent`
**Language:** Python 3.11+
**Framework:** gRPC + FastAPI (UI BFF + health endpoints)
**Primary Model:** Claude Sonnet 4 (`claude-sonnet-4-20250514`)
**Knowledge Store:** Weaviate (domain knowledge RAG)

---

## Architecture Position

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           QA Intelligence Platform                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   DOMAIN AGENTS (Business Experts)                                       │
│   ┌───────────────┐                                                      │
│   │  eCommerce    │◄──── THIS AGENT                                     │
│   │  Domain Agent │                                                      │
│   └───────┬───────┘                                                      │
│           │                                                              │
│           │ gRPC (provides domain context)                               │
│           │                                                              │
│           ▼                                                              │
│   STLC AGENTS (Testing Activities)                                       │
│   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐               │
│   │  Test Data    │  │  Test Case    │  │   Defect      │               │
│   │  Agent        │  │  Generator    │  │   Analyzer    │               │
│   └───────────────┘  └───────────────┘  └───────────────┘               │
│         ▲                                                                │
│         │ gRPC (GenerateData)                                           │
│         │                                                                │
│   ┌─────┴─────────┐                                                      │
│   │  eCommerce    │                                                      │
│   │  Domain Agent │ (calls Test Data Agent for generation)              │
│   └───────────────┘                                                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Monorepo Structure

```
ecommerce-domain-agent/
├── README.md
├── docker-compose.yml              # Service + UI + dependencies
├── Makefile                        # Orchestrates both
│
├── service/                        # Python gRPC service
│   ├── pyproject.toml
│   ├── Dockerfile
│   ├── .env.example
│   │
│   ├── protos/
│   │   ├── ecommerce_domain.proto  # Domain Agent API
│   │   └── test_data.proto         # Test Data Agent API (client)
│   │
│   ├── src/
│   │   └── ecommerce_agent/
│   │       ├── __init__.py
│   │       ├── main.py
│   │       ├── config.py
│   │       │
│   │       ├── server/
│   │       │   ├── __init__.py
│   │       │   ├── grpc_server.py
│   │       │   └── health.py
│   │       │
│   │       ├── domain/
│   │       │   ├── __init__.py
│   │       │   ├── entities.py         # Entity definitions
│   │       │   ├── workflows.py        # Checkout, returns, etc.
│   │       │   ├── business_rules.py   # Validation rules
│   │       │   └── edge_cases.py       # Known edge cases
│   │       │
│   │       ├── knowledge/
│   │       │   ├── __init__.py
│   │       │   ├── retriever.py        # RAG retrieval
│   │       │   ├── indexer.py          # Knowledge indexing
│   │       │   └── collections.py      # Weaviate collections
│   │       │
│   │       ├── context/
│   │       │   ├── __init__.py
│   │       │   ├── builder.py          # Context builder for STLC agents
│   │       │   └── enricher.py         # Enriches requests with domain knowledge
│   │       │
│   │       ├── clients/
│   │       │   ├── __init__.py
│   │       │   ├── test_data_client.py # Test Data Agent gRPC client
│   │       │   ├── claude.py           # Anthropic API client
│   │       │   └── weaviate.py         # Vector DB client
│   │       │
│   │       ├── prompts/
│   │       │   ├── __init__.py
│   │       │   ├── system.py
│   │       │   └── templates.py
│   │       │
│   │       └── utils/
│   │           ├── __init__.py
│   │           ├── logging.py
│   │           ├── metrics.py
│   │           └── tracing.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── unit/
│   │   └── integration/
│   │
│   └── k8s/
│       ├── deployment.yaml
│       ├── service.yaml
│       └── configmap.yaml
│
└── ui/                             # Next.js dashboard
    ├── package.json
    ├── pnpm-lock.yaml
    ├── next.config.js
    ├── tailwind.config.js
    ├── tsconfig.json
    ├── Dockerfile
    ├── .env.example
    │
    ├── src/
    │   ├── app/
    │   │   ├── layout.tsx
    │   │   ├── page.tsx              # Domain explorer
    │   │   ├── globals.css
    │   │   ├── api/                  # BFF routes
    │   │   │   ├── domain/
    │   │   │   │   └── route.ts
    │   │   │   ├── generate/
    │   │   │   │   └── route.ts
    │   │   │   ├── workflows/
    │   │   │   │   └── route.ts
    │   │   │   └── health/
    │   │   │       └── route.ts
    │   │   ├── entities/
    │   │   │   └── page.tsx          # Entity browser
    │   │   ├── workflows/
    │   │   │   └── page.tsx          # Workflow explorer
    │   │   └── generate/
    │   │       └── page.tsx          # Test data generation
    │   │
    │   ├── components/
    │   │   ├── ui/                   # shadcn/ui
    │   │   ├── layout/
    │   │   ├── domain/
    │   │   │   ├── entity-explorer.tsx
    │   │   │   ├── entity-card.tsx
    │   │   │   ├── workflow-diagram.tsx
    │   │   │   └── business-rules.tsx
    │   │   ├── generator/
    │   │   │   ├── context-builder.tsx
    │   │   │   ├── scenario-picker.tsx
    │   │   │   └── generation-form.tsx
    │   │   └── preview/
    │   │       ├── data-preview.tsx
    │   │       └── json-viewer.tsx
    │   │
    │   ├── lib/
    │   │   ├── api-client.ts
    │   │   ├── grpc-client.ts
    │   │   └── utils.ts
    │   │
    │   ├── hooks/
    │   ├── stores/
    │   ├── types/
    │   └── proto/
    │
    ├── tests/
    └── k8s/
```

---

## Tech Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Runtime | Python | 3.11+ | Core language |
| gRPC | grpcio, grpcio-tools | 1.60+ | Service communication |
| HTTP | FastAPI | 0.109+ | BFF + health endpoints |
| LLM Client | anthropic | 0.40+ | Claude API |
| Vector DB | weaviate-client | 4.0+ | Domain knowledge RAG |
| Validation | pydantic | 2.5+ | Schema validation |
| Config | pydantic-settings | 2.0+ | Environment config |
| Logging | structlog | 24.0+ | Structured logging |
| Metrics | prometheus-client | 0.19+ | Prometheus metrics |
| Tracing | opentelemetry-* | 1.22+ | Distributed tracing |
| Testing | pytest, pytest-asyncio | 8.0+ | Test framework |
| UI Framework | Next.js | 14.x | React framework |
| UI Styling | Tailwind CSS | 3.4.x | Utility-first CSS |
| UI Components | shadcn/ui | latest | Component library |
| UI State | Zustand | 4.x | State management |

---

## gRPC Service Definition

### Domain Agent API (Server)

```protobuf
// protos/ecommerce_domain.proto
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
  string entity = 2;                      // cart, order, payment, etc.
  string workflow = 3;                    // checkout, return, refund, etc.
  string scenario = 4;                    // happy_path, edge_case, etc.
  repeated string aspects = 5;            // business_rules, validations, relationships
}

message DomainContextResponse {
  string request_id = 1;
  string context = 2;                     // Rich natural language context
  repeated BusinessRule rules = 3;        // Applicable business rules
  repeated EntityRelationship relationships = 4;
  repeated string edge_cases = 5;
  map<string, string> metadata = 6;
}

message BusinessRule {
  string id = 1;
  string name = 2;
  string description = 3;
  string entity = 4;
  string condition = 5;                   // When this rule applies
  string constraint = 6;                  // What the rule enforces
  string severity = 7;                    // error, warning, info
}

message EntityRelationship {
  string source_entity = 1;
  string target_entity = 2;
  string relationship_type = 3;           // one_to_many, many_to_many, etc.
  string description = 4;
  bool required = 5;
}

// ============ Knowledge Query ============

message KnowledgeRequest {
  string request_id = 1;
  string query = 2;                       // Natural language query
  repeated string categories = 3;         // Filter by: entities, workflows, rules, edge_cases
  int32 max_results = 4;
}

message KnowledgeResponse {
  string request_id = 1;
  repeated KnowledgeItem items = 2;
  string summary = 3;                     // LLM-generated summary
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
  string category = 1;                    // core, transactional, etc.
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
  string action = 5;                      // create, update, validate, etc.
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
  string category = 3;                    // boundary, null, concurrent, etc.
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
  string severity = 10;                   // critical, high, medium, low
}

// ============ Test Data Generation ============

message GenerateTestDataRequest {
  string request_id = 1;
  string entity = 2;
  int32 count = 3;
  string workflow_context = 4;            // Optional: checkout, return, etc.
  repeated string scenarios = 5;          // happy_path, edge_case, etc.
  string custom_context = 6;              // Additional context from user
  bool include_edge_cases = 7;
  string output_format = 8;               // JSON, CSV, SQL
  map<string, int32> scenario_counts = 9; // scenario_name -> count
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

### Test Data Agent API (Client)

The eCommerce Domain Agent is a **client** of the Test Data Agent. It uses the existing Test Data Agent proto exactly as defined - **DO NOT MODIFY**:

```protobuf
// protos/test_data.proto (imported from Test Data Agent - DO NOT MODIFY)
syntax = "proto3";

package testdata.v1;

service TestDataService {
  // Synchronous generation for small requests (<1000 records)
  rpc GenerateData(GenerateRequest) returns (GenerateResponse);

  // Streaming for large requests
  rpc GenerateDataStream(GenerateRequest) returns (stream DataChunk);

  // List available schemas
  rpc GetSchemas(GetSchemasRequest) returns (GetSchemasResponse);

  // Health check
  rpc HealthCheck(HealthCheckRequest) returns (HealthCheckResponse);
}

message GenerateRequest {
  string request_id = 1;                    // Unique ID for tracing
  string domain = 2;                        // ecommerce, supply_chain, loyalty, etc.
  string entity = 3;                        // cart, order, payment, user, review
  Schema schema = 4;                        // Field definitions (or use pre-defined)
  Constraints constraints = 5;              // Validation rules
  repeated Scenario scenarios = 6;          // Generation scenarios
  string context = 7;                       // Natural language context for LLM
  repeated string hints = 8;                // Routing hints: realistic, edge_case, defect_triggering
  OutputFormat output_format = 9;           // JSON, CSV, SQL
  int32 count = 10;                         // Total records to generate
  bool use_cache = 11;                      // Use cached data pools
  bool learn_from_history = 12;             // Use RAG patterns
  bool defect_triggering = 13;              // Generate bug-finding data
  bool production_like = 14;                // Mimic production distributions
  string inline_schema = 15;                // JSON string of complete schema definition
}

message Schema {
  repeated Field fields = 1;
  string predefined_schema = 2;             // Use pre-defined: "cart", "order", etc.
}

message Field {
  string name = 1;
  FieldType type = 2;
  bool required = 3;
  string description = 4;                   // For LLM context
  repeated Field nested_fields = 5;         // For object/array types
}

enum FieldType {
  STRING = 0;
  INTEGER = 1;
  FLOAT = 2;
  BOOLEAN = 3;
  DATE = 4;
  DATETIME = 5;
  EMAIL = 6;
  PHONE = 7;
  ADDRESS = 8;
  UUID = 9;
  ENUM = 10;
  OBJECT = 11;
  ARRAY = 12;
}

message Constraints {
  map<string, FieldConstraint> field_constraints = 1;
}

message FieldConstraint {
  optional double min = 1;
  optional double max = 2;
  repeated string enum_values = 3;
  optional string regex = 4;
  optional int32 min_length = 5;
  optional int32 max_length = 6;
  optional string format = 7;               // date format, etc.
}

message Scenario {
  string name = 1;                          // happy_path, expired_token, etc.
  int32 count = 2;                          // Records for this scenario
  map<string, string> overrides = 3;        // Field value overrides
  string description = 4;                   // For LLM context
}

enum OutputFormat {
  JSON = 0;
  CSV = 1;
  SQL = 2;
}

message GenerateResponse {
  string request_id = 1;
  bool success = 2;
  string data = 3;                          // JSON string of generated data
  int32 record_count = 4;
  GenerationMetadata metadata = 5;
  string error = 6;
}

message GenerationMetadata {
  string generation_path = 1;               // traditional, llm, rag, hybrid
  int32 llm_tokens_used = 2;
  float generation_time_ms = 3;
  float coherence_score = 4;
  map<string, int32> scenario_counts = 5;
}

message DataChunk {
  string request_id = 1;
  string data = 2;                          // Partial JSON array
  int32 chunk_index = 3;
  bool is_final = 4;
}

message GetSchemasRequest {
  string domain = 1;                        // Filter by domain (optional)
}

message GetSchemasResponse {
  repeated SchemaInfo schemas = 1;
}

message SchemaInfo {
  string name = 1;
  string domain = 2;
  string description = 3;
  repeated string fields = 4;
}

message HealthCheckRequest {}

message HealthCheckResponse {
  string status = 1;                        // healthy, degraded, unhealthy
  map<string, string> components = 2;       // Component health status
}
```

---

## Domain Knowledge Model

### eCommerce Entities

```python
# Core entities the agent understands

ENTITIES = {
    "cart": {
        "description": "Shopping cart containing items before checkout",
        "category": "transactional",
        "fields": [
            {"name": "cart_id", "type": "string", "description": "Unique cart identifier"},
            {"name": "customer_id", "type": "string", "description": "Customer who owns the cart"},
            {"name": "items", "type": "array", "description": "List of cart items"},
            {"name": "subtotal", "type": "decimal", "description": "Sum of item prices"},
            {"name": "tax", "type": "decimal", "description": "Calculated tax amount"},
            {"name": "total", "type": "decimal", "description": "Final cart total"},
            {"name": "currency", "type": "string", "description": "Currency code (USD, EUR)"},
            {"name": "status", "type": "enum", "description": "active, abandoned, converted"},
            {"name": "created_at", "type": "datetime", "description": "Cart creation time"},
            {"name": "updated_at", "type": "datetime", "description": "Last modification time"},
        ],
        "relationships": [
            {"target": "customer", "type": "belongs_to"},
            {"target": "cart_item", "type": "has_many"},
            {"target": "order", "type": "converts_to"},
        ],
    },
    "order": {
        "description": "Completed purchase after checkout",
        "category": "transactional",
        "fields": [...],
        "relationships": [...],
    },
    "payment": {
        "description": "Payment transaction for an order",
        "category": "financial",
        "fields": [...],
        "relationships": [...],
    },
    "customer": {
        "description": "Registered or guest customer",
        "category": "core",
        "fields": [...],
        "relationships": [...],
    },
    "product": {
        "description": "Sellable product in catalog",
        "category": "catalog",
        "fields": [...],
        "relationships": [...],
    },
    "shipment": {
        "description": "Shipment of order items",
        "category": "fulfillment",
        "fields": [...],
        "relationships": [...],
    },
    "return": {
        "description": "Return request for order items",
        "category": "post-purchase",
        "fields": [...],
        "relationships": [...],
    },
    "refund": {
        "description": "Refund transaction for returns",
        "category": "financial",
        "fields": [...],
        "relationships": [...],
    },
    "review": {
        "description": "Customer product review",
        "category": "engagement",
        "fields": [...],
        "relationships": [...],
    },
    "promotion": {
        "description": "Discount or promotional offer",
        "category": "pricing",
        "fields": [...],
        "relationships": [...],
    },
}
```

### eCommerce Workflows

```python
WORKFLOWS = {
    "checkout": {
        "description": "Complete purchase flow from cart to order confirmation",
        "steps": [
            {"order": 1, "name": "cart_validation", "entity": "cart", "action": "validate"},
            {"order": 2, "name": "inventory_check", "entity": "product", "action": "validate"},
            {"order": 3, "name": "pricing_calculation", "entity": "cart", "action": "calculate"},
            {"order": 4, "name": "shipping_selection", "entity": "shipment", "action": "create"},
            {"order": 5, "name": "payment_processing", "entity": "payment", "action": "create"},
            {"order": 6, "name": "order_creation", "entity": "order", "action": "create"},
            {"order": 7, "name": "confirmation", "entity": "order", "action": "notify"},
        ],
        "involved_entities": ["cart", "customer", "product", "payment", "order", "shipment"],
    },
    "return_flow": {
        "description": "Customer return and refund process",
        "steps": [...],
        "involved_entities": ["order", "return", "refund", "shipment"],
    },
    "cart_abandonment": {
        "description": "Abandoned cart recovery flow",
        "steps": [...],
        "involved_entities": ["cart", "customer", "promotion"],
    },
    "inventory_sync": {
        "description": "Inventory synchronization with warehouse",
        "steps": [...],
        "involved_entities": ["product", "inventory"],
    },
    "price_update": {
        "description": "Product price update propagation",
        "steps": [...],
        "involved_entities": ["product", "cart", "promotion"],
    },
}
```

### Business Rules

```python
BUSINESS_RULES = [
    {
        "id": "BR001",
        "name": "cart_item_quantity_limit",
        "entity": "cart_item",
        "condition": "Always",
        "constraint": "Quantity per item must be between 1 and 99",
        "severity": "error",
    },
    {
        "id": "BR002",
        "name": "cart_total_minimum",
        "entity": "cart",
        "condition": "At checkout",
        "constraint": "Cart total must be >= $1.00 for payment processing",
        "severity": "error",
    },
    {
        "id": "BR003",
        "name": "payment_amount_match",
        "entity": "payment",
        "condition": "At payment creation",
        "constraint": "Payment amount must match order total exactly",
        "severity": "error",
    },
    {
        "id": "BR004",
        "name": "return_window",
        "entity": "return",
        "condition": "At return request",
        "constraint": "Return must be within 30 days of delivery",
        "severity": "error",
    },
    # ... more rules
]
```

### Edge Cases

```python
EDGE_CASES = [
    {
        "id": "EC001",
        "name": "concurrent_cart_update",
        "category": "concurrency",
        "entity": "cart",
        "description": "Two sessions update the same cart simultaneously",
        "test_approach": "Race condition testing with parallel requests",
        "expected_behavior": "Last write wins or optimistic locking prevents conflict",
        "severity": "high",
    },
    {
        "id": "EC002",
        "name": "payment_timeout_after_success",
        "category": "network",
        "entity": "payment",
        "description": "Payment succeeds but response times out",
        "test_approach": "Inject network delay after payment gateway success",
        "expected_behavior": "Idempotent retry or reconciliation job resolves",
        "severity": "critical",
    },
    {
        "id": "EC003",
        "name": "inventory_oversell",
        "category": "concurrency",
        "entity": "order",
        "description": "Multiple orders for last item in stock",
        "test_approach": "Parallel checkout requests for low-stock item",
        "expected_behavior": "Only one order succeeds, others fail gracefully",
        "severity": "critical",
    },
    # ... more edge cases
]
```

---

## RAG Collections (Weaviate)

```python
COLLECTIONS = {
    "ecommerce_entities": {
        "description": "Entity definitions with fields and relationships",
        "properties": [
            {"name": "entity_name", "type": "text"},
            {"name": "description", "type": "text"},
            {"name": "category", "type": "keyword"},
            {"name": "fields_json", "type": "text"},
            {"name": "relationships_json", "type": "text"},
        ],
    },
    "ecommerce_workflows": {
        "description": "Workflow definitions with steps",
        "properties": [
            {"name": "workflow_name", "type": "text"},
            {"name": "description", "type": "text"},
            {"name": "steps_json", "type": "text"},
            {"name": "involved_entities", "type": "text[]"},
        ],
    },
    "ecommerce_rules": {
        "description": "Business rules and validations",
        "properties": [
            {"name": "rule_id", "type": "keyword"},
            {"name": "name", "type": "text"},
            {"name": "entity", "type": "keyword"},
            {"name": "description", "type": "text"},
            {"name": "constraint", "type": "text"},
            {"name": "severity", "type": "keyword"},
        ],
    },
    "ecommerce_edge_cases": {
        "description": "Known edge cases and test scenarios",
        "properties": [
            {"name": "edge_case_id", "type": "keyword"},
            {"name": "name", "type": "text"},
            {"name": "category", "type": "keyword"},
            {"name": "entity", "type": "keyword"},
            {"name": "workflow", "type": "keyword"},
            {"name": "description", "type": "text"},
            {"name": "test_approach", "type": "text"},
            {"name": "expected_behavior", "type": "text"},
            {"name": "severity", "type": "keyword"},
        ],
    },
    "ecommerce_test_patterns": {
        "description": "Successful test data patterns from past generations",
        "properties": [
            {"name": "entity", "type": "keyword"},
            {"name": "scenario", "type": "keyword"},
            {"name": "context", "type": "text"},
            {"name": "data_json", "type": "text"},
            {"name": "quality_score", "type": "number"},
        ],
    },
}
```

---

## Configuration

```python
# src/ecommerce_agent/config.py
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
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
    
    # Knowledge
    knowledge_refresh_interval: int = 3600  # seconds
    
    # Observability
    prometheus_port: int = 9092
    otlp_endpoint: str = "http://otel-collector:4317"
    
    class Config:
        env_file = ".env"
```

---

## Core Components

### 1. Domain Context Builder

Builds rich context for STLC agents:

```python
class DomainContextBuilder:
    """Builds comprehensive domain context for test generation."""
    
    async def build_context(
        self,
        entity: str,
        workflow: str | None = None,
        scenario: str | None = None,
        aspects: list[str] | None = None,
    ) -> DomainContext:
        """
        Build rich domain context combining:
        1. Entity schema and relationships
        2. Applicable business rules
        3. Workflow context if provided
        4. Relevant edge cases
        5. RAG-retrieved patterns
        """
        pass
    
    async def enrich_generation_request(
        self,
        request: GenerateTestDataRequest,
    ) -> EnrichedRequest:
        """
        Enrich a test data generation request with domain knowledge:
        1. Add business rules as constraints
        2. Add relationship context
        3. Add edge case scenarios
        4. Generate natural language context for LLM
        """
        pass
```

### 2. Knowledge Retriever

RAG-based knowledge retrieval:

```python
class KnowledgeRetriever:
    """Retrieves domain knowledge from Weaviate."""
    
    async def query(
        self,
        query: str,
        categories: list[str] | None = None,
        max_results: int = 10,
    ) -> list[KnowledgeItem]:
        """Semantic search across domain knowledge."""
        pass
    
    async def get_entity_context(self, entity: str) -> EntityContext:
        """Get all context for an entity."""
        pass
    
    async def get_workflow_context(self, workflow: str) -> WorkflowContext:
        """Get all context for a workflow."""
        pass
    
    async def get_edge_cases(
        self,
        entity: str | None = None,
        workflow: str | None = None,
        category: str | None = None,
    ) -> list[EdgeCase]:
        """Get relevant edge cases."""
        pass
```

### 3. Test Data Agent Client

gRPC client for Test Data Agent:

```python
class TestDataAgentClient:
    """Client for Test Data Agent service."""
    
    async def generate_data(
        self,
        request: GenerateRequest,
    ) -> GenerateResponse:
        """Generate test data via Test Data Agent."""
        pass
    
    async def get_schemas(
        self,
        domain: str | None = None,
    ) -> list[SchemaInfo]:
        """Get available schemas from Test Data Agent."""
        pass
    
    async def health_check(self) -> HealthStatus:
        """Check Test Data Agent health."""
        pass
```

### 4. Generation Orchestrator

Orchestrates domain-aware test data generation:

```python
class GenerationOrchestrator:
    """Orchestrates test data generation with domain context."""
    
    async def generate(
        self,
        request: GenerateTestDataRequest,
    ) -> GenerateTestDataResponse:
        """
        1. Build domain context
        2. Enrich request with business rules and edge cases
        3. Call Test Data Agent with enriched request
        4. Validate and score results
        5. Store successful patterns
        """
        pass
```

---

## UI Features

### Main Pages

1. **Domain Explorer (Home)**
   - Overview of eCommerce domain
   - Quick stats: entities, workflows, rules, edge cases
   - Search across all domain knowledge
   - Recent generations

2. **Entity Browser**
   - List all entities with categories
   - Entity details: fields, relationships, rules
   - Visual entity relationship diagram
   - Quick generate button per entity

3. **Workflow Explorer**
   - List all workflows
   - Interactive workflow diagram (steps visualization)
   - Workflow details: steps, entities involved, rules
   - Edge cases per workflow step

4. **Test Data Generator**
   - Entity selector
   - Workflow context selector
   - Scenario builder with domain-suggested scenarios
   - Custom context editor
   - Edge case toggle
   - Preview and download

5. **Knowledge Query**
   - Natural language query interface
   - Results with relevance scores
   - LLM-generated summaries

---

## REST API (BFF Layer)

### GET /api/domain/entities

List all entities.

**Response:**
```typescript
interface EntitiesResponse {
  entities: Array<{
    name: string;
    description: string;
    category: string;
    fieldCount: number;
  }>;
}
```

### GET /api/domain/entities/:name

Get entity details.

**Response:**
```typescript
interface EntityResponse {
  entity: {
    name: string;
    description: string;
    fields: Array<{
      name: string;
      type: string;
      description: string;
      required: boolean;
    }>;
    relationships: Array<{
      target: string;
      type: string;
      description: string;
    }>;
    rules: Array<BusinessRule>;
    edgeCases: string[];
  };
}
```

### GET /api/domain/workflows

List all workflows.

### GET /api/domain/workflows/:name

Get workflow details.

### POST /api/domain/query

Query domain knowledge.

**Request:**
```typescript
interface QueryRequest {
  query: string;
  categories?: string[];
  maxResults?: number;
}
```

### POST /api/generate

Generate test data with domain context.

**Request:**
```typescript
interface GenerateRequest {
  entity: string;
  count: number;
  workflowContext?: string;
  scenarios?: string[];
  customContext?: string;
  includeEdgeCases?: boolean;
  outputFormat?: 'JSON' | 'CSV' | 'SQL';
  scenarioCounts?: Record<string, number>;
}
```

**Response:**
```typescript
interface GenerateResponse {
  success: boolean;
  requestId: string;
  data: string;
  recordCount: number;
  metadata: {
    generationPath: string;
    llmTokensUsed?: number;
    generationTimeMs: number;
    coherenceScore?: number;
    domainContextUsed: string;
    scenarioCounts: Record<string, number>;
  };
  error?: string;
}
```

### GET /api/health

Health check.

---

## Docker Configuration

### docker-compose.yml

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
    depends_on:
      - weaviate
    networks:
      - qa-platform

  ui:
    build: ./ui
    ports:
      - "3001:3000"
    environment:
      - GRPC_SERVICE_HOST=service
      - GRPC_SERVICE_PORT=9002
    depends_on:
      - service
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
    external: true

volumes:
  weaviate_data:
```

**Note:** This connects to the same `qa-platform` network as the Test Data Agent, allowing gRPC communication.

---

## Integration with Test Data Agent

### Communication Flow

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   UI (Next.js)  │         │ eCommerce Agent │         │ Test Data Agent │
│    Port 3001    │         │   Port 9002     │         │   Port 9001     │
└────────┬────────┘         └────────┬────────┘         └────────┬────────┘
         │                           │                           │
         │ POST /api/generate        │                           │
         │ {entity: "cart",          │                           │
         │  count: 50,               │                           │
         │  workflowContext:         │                           │
         │    "checkout"}            │                           │
         ├──────────────────────────►│                           │
         │                           │                           │
         │                           │ Build domain context:     │
         │                           │ - Business rules          │
         │                           │ - Entity relationships    │
         │                           │ - Edge cases              │
         │                           │ - RAG patterns            │
         │                           │                           │
         │                           │ gRPC: GenerateData        │
         │                           │ {domain: "ecommerce",     │
         │                           │  entity: "cart",          │
         │                           │  context: "Generate       │
         │                           │    checkout carts with    │
         │                           │    business rules...",    │
         │                           │  hints: ["realistic"]}    │
         │                           ├──────────────────────────►│
         │                           │                           │
         │                           │         Response          │
         │                           │◄──────────────────────────┤
         │                           │                           │
         │      Response             │                           │
         │◄──────────────────────────┤                           │
         │                           │                           │
```

### Context Enrichment Example

When user requests: "Generate 50 carts for checkout testing"

eCommerce Agent enriches the request:

```python
# Original request
{
    "entity": "cart",
    "count": 50,
    "workflow_context": "checkout",
}

# Enriched context sent to Test Data Agent
{
    "domain": "ecommerce",
    "entity": "cart",
    "count": 50,
    "context": """
    Generate shopping carts for checkout flow testing.
    
    Business Rules to Honor:
    - Cart must have at least 1 item
    - Item quantity must be 1-99
    - Cart total must be >= $1.00
    - Each item must have valid SKU format
    - Prices must be positive decimals
    
    Entity Relationships:
    - Cart belongs to Customer (customer_id required)
    - Cart has many CartItems
    - Cart converts to Order at checkout
    
    Checkout Workflow Context:
    - Cart validation happens first
    - Inventory check follows
    - Pricing calculation includes tax
    
    Generate coherent carts where:
    - Items make sense together (e.g., outfit, electronics bundle)
    - Prices are realistic for product types
    - Customer IDs follow USR-XXXXXXX pattern
    """,
    "hints": ["realistic", "checkout_flow"],
    "scenarios": [
        {"name": "happy_path", "count": 30},
        {"name": "high_value", "count": 10, "description": "Cart total > $500"},
        {"name": "edge_case", "count": 10, "description": "Single item, boundary quantities"},
    ],
}
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
- Project setup (monorepo structure)
- gRPC server skeleton
- Configuration management
- Health endpoints
- Docker setup

### Phase 2: Domain Model (Week 1-2)
- Entity definitions
- Workflow definitions
- Business rules
- Edge cases
- Weaviate collections

### Phase 3: Knowledge Layer (Week 2)
- RAG retriever
- Knowledge indexer
- Seed domain knowledge

### Phase 4: Test Data Integration (Week 2-3)
- Test Data Agent client
- Context builder
- Request enrichment
- Generation orchestrator

### Phase 5: UI (Week 3-4)
- Next.js setup
- BFF API routes
- Domain explorer
- Entity browser
- Workflow explorer
- Test data generator

### Phase 6: Polish (Week 4)
- Testing
- Documentation
- Kubernetes manifests
- CI/CD

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Domain context accuracy | >90% relevant rules included |
| Generation quality improvement | 30% higher coherence vs direct calls |
| Knowledge query relevance | >0.8 avg relevance score |
| UI response time | <200ms for domain queries |
| Test Data Agent integration | <500ms overhead |

---

## Future Enhancements

- Multi-tenant domain configurations
- Domain knowledge versioning
- A/B testing domain contexts
- Integration with Test Case Generator
- Defect pattern learning from production bugs
