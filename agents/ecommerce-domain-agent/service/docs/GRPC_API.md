# gRPC API Documentation

The eCommerce Domain Agent exposes a gRPC API for domain knowledge and test data generation.

## Service Definition

**Package**: `ecommerce.domain.v1`
**Service**: `EcommerceDomainService`
**Port**: 9002

## Connection

### Direct gRPC (Backend-to-Backend)

```python
import grpc
from ecommerce_agent.proto import ecommerce_domain_pb2_grpc

channel = grpc.insecure_channel('localhost:9002')
stub = ecommerce_domain_pb2_grpc.EcommerceDomainServiceStub(channel)
```

### gRPC-Web (Frontend via Envoy)

The service is exposed via Envoy proxy at `localhost:8080` for gRPC-Web clients.

```typescript
import { EcommerceDomainServiceClient } from './generated/ecommerce_domain';

const client = new EcommerceDomainServiceClient('http://localhost:8080');
```

---

## RPC Methods

### ListEntities

List all domain entities, optionally filtered by category.

**Request**: `ListEntitiesRequest`
| Field | Type | Description |
|-------|------|-------------|
| category | string | Optional filter by category (core, transactional, financial, catalog, fulfillment) |

**Response**: `ListEntitiesResponse`
| Field | Type | Description |
|-------|------|-------------|
| entities | EntitySummary[] | List of entity summaries |

**Example**:
```python
request = ListEntitiesRequest(category="transactional")
response = stub.ListEntities(request)
for entity in response.entities:
    print(f"{entity.name}: {entity.description}")
```

---

### GetEntity

Get detailed information about a specific entity.

**Request**: `EntityRequest`
| Field | Type | Description |
|-------|------|-------------|
| entity_name | string | Name of the entity (e.g., "cart", "order") |
| include_relationships | bool | Include entity relationships |
| include_rules | bool | Include business rules |
| include_edge_cases | bool | Include edge cases |

**Response**: `EntityResponse`
| Field | Type | Description |
|-------|------|-------------|
| entity | Entity | Full entity details |

**Entity Structure**:
- `name`: Entity name
- `description`: Entity description
- `fields`: List of EntityField objects
- `rules`: Business rules (if requested)
- `relationships`: Related entities (if requested)
- `edge_cases`: Edge case descriptions (if requested)
- `test_scenarios`: Available test scenarios

**Example**:
```python
request = EntityRequest(
    entity_name="cart",
    include_relationships=True,
    include_rules=True
)
response = stub.GetEntity(request)
print(f"Entity: {response.entity.name}")
print(f"Fields: {len(response.entity.fields)}")
print(f"Rules: {len(response.entity.rules)}")
```

---

### ListWorkflows

List all business workflows.

**Request**: `ListWorkflowsRequest` (empty)

**Response**: `ListWorkflowsResponse`
| Field | Type | Description |
|-------|------|-------------|
| workflows | WorkflowSummary[] | List of workflow summaries |

**Example**:
```python
response = stub.ListWorkflows(ListWorkflowsRequest())
for workflow in response.workflows:
    print(f"{workflow.name}: {workflow.step_count} steps")
```

---

### GetWorkflow

Get detailed information about a specific workflow.

**Request**: `WorkflowRequest`
| Field | Type | Description |
|-------|------|-------------|
| workflow_name | string | Name of the workflow |
| include_steps | bool | Include workflow steps |
| include_edge_cases | bool | Include edge cases |

**Response**: `WorkflowResponse`
| Field | Type | Description |
|-------|------|-------------|
| workflow | Workflow | Full workflow details |

**Workflow Structure**:
- `name`: Workflow name
- `description`: Workflow description
- `steps`: Ordered workflow steps
- `involved_entities`: Entities involved in this workflow
- `rules`: Business rules that apply
- `edge_cases`: Edge case descriptions
- `test_scenarios`: Available test scenarios

**Example**:
```python
request = WorkflowRequest(
    workflow_name="checkout",
    include_steps=True
)
response = stub.GetWorkflow(request)
for step in response.workflow.steps:
    print(f"Step {step.order}: {step.name}")
```

---

### GetDomainContext

Get enriched domain context for test generation.

**Request**: `DomainContextRequest`
| Field | Type | Description |
|-------|------|-------------|
| request_id | string | Unique request identifier |
| entity | string | Target entity name |
| workflow | string | Optional workflow context |
| scenario | string | Optional scenario name |
| aspects | string[] | Specific aspects to include |

**Response**: `DomainContextResponse`
| Field | Type | Description |
|-------|------|-------------|
| request_id | string | Original request ID |
| context | string | Enriched context text |
| rules | BusinessRule[] | Applicable business rules |
| relationships | EntityRelationship[] | Entity relationships |
| edge_cases | string[] | Relevant edge cases |
| metadata | map<string, string> | Additional metadata |

**Example**:
```python
request = DomainContextRequest(
    request_id="ctx-123",
    entity="cart",
    workflow="checkout",
    aspects=["validation", "edge_cases"]
)
response = stub.GetDomainContext(request)
print(f"Context: {response.context[:200]}...")
print(f"Rules: {len(response.rules)}")
```

---

### GetEdgeCases

Get edge cases for an entity or workflow.

**Request**: `EdgeCasesRequest`
| Field | Type | Description |
|-------|------|-------------|
| entity | string | Entity name |
| workflow | string | Workflow name |
| category | string | Edge case category |

**Response**: `EdgeCasesResponse`
| Field | Type | Description |
|-------|------|-------------|
| edge_cases | EdgeCase[] | List of edge cases |

**EdgeCase Structure**:
- `id`: Unique identifier
- `name`: Edge case name
- `description`: Detailed description
- `category`: Category (concurrency, boundary, error, etc.)
- `entity`: Related entity
- `workflow`: Related workflow
- `test_approach`: How to test this case
- `example_data`: Sample data for testing
- `expected_behavior`: Expected system behavior
- `severity`: Impact severity (low, medium, high, critical)

**Example**:
```python
request = EdgeCasesRequest(entity="cart")
response = stub.GetEdgeCases(request)
for edge_case in response.edge_cases:
    print(f"[{edge_case.severity}] {edge_case.name}")
```

---

### GenerateTestData

Generate test data for an entity with domain context enrichment.

**Request**: `GenerateTestDataRequest`
| Field | Type | Description |
|-------|------|-------------|
| request_id | string | Unique request identifier |
| entity | string | Target entity name |
| count | int32 | Number of records to generate |
| workflow_context | string | Optional workflow context |
| scenarios | string[] | Test scenarios to include |
| custom_context | string | Custom context text |
| include_edge_cases | bool | Include edge case data |
| output_format | string | Output format (JSON, CSV, SQL) |
| scenario_counts | map<string, int32> | Records per scenario |
| generation_method | GenerationMethod | Generation approach |
| production_like | bool | Generate production-like data |
| use_cache | bool | Use cached patterns |

**GenerationMethod Enum**:
- `GENERATION_METHOD_TRADITIONAL` (1): Rule-based generation
- `GENERATION_METHOD_LLM` (2): LLM-based generation
- `GENERATION_METHOD_RAG` (3): RAG-based generation
- `GENERATION_METHOD_HYBRID` (4): Combined approach (default)

**Response**: `GenerateTestDataResponse`
| Field | Type | Description |
|-------|------|-------------|
| request_id | string | Original request ID |
| success | bool | Whether generation succeeded |
| data | string | Generated data (JSON string) |
| record_count | int32 | Number of records generated |
| metadata | GenerationMetadata | Generation details |
| error | string | Error message if failed |

**Example**:
```python
request = GenerateTestDataRequest(
    request_id="gen-456",
    entity="cart",
    count=10,
    workflow_context="checkout",
    scenarios=["happy_path", "high_value"],
    include_edge_cases=True,
    output_format="JSON",
    generation_method=GenerationMethod.GENERATION_METHOD_HYBRID,
    production_like=True
)
response = stub.GenerateTestData(request)
if response.success:
    data = json.loads(response.data)
    print(f"Generated {response.record_count} records")
```

---

### QueryKnowledge

Search the domain knowledge base.

**Request**: `KnowledgeRequest`
| Field | Type | Description |
|-------|------|-------------|
| request_id | string | Unique request identifier |
| query | string | Search query |
| categories | string[] | Categories to search |
| max_results | int32 | Maximum results |

**Response**: `KnowledgeResponse`
| Field | Type | Description |
|-------|------|-------------|
| request_id | string | Original request ID |
| items | KnowledgeItem[] | Matching knowledge items |
| summary | string | AI-generated summary |

**KnowledgeItem Structure**:
- `id`: Document ID
- `category`: Knowledge category
- `title`: Item title
- `content`: Full content
- `relevance_score`: Search relevance (0.0 to 1.0)
- `metadata`: Additional metadata

**Example**:
```python
request = KnowledgeRequest(
    request_id="know-789",
    query="cart validation rules",
    categories=["business_rules", "edge_cases"],
    max_results=10
)
response = stub.QueryKnowledge(request)
for item in response.items:
    print(f"[{item.relevance_score:.2f}] {item.title}")
```

---

### HealthCheck

Check service health status.

**Request**: `HealthCheckRequest` (empty)

**Response**: `HealthCheckResponse`
| Field | Type | Description |
|-------|------|-------------|
| status | string | Overall status (healthy, degraded, unhealthy) |
| components | map<string, string> | Component health statuses |

**Example**:
```python
response = stub.HealthCheck(HealthCheckRequest())
print(f"Status: {response.status}")
for component, status in response.components.items():
    print(f"  {component}: {status}")
```

---

## Error Handling

gRPC errors are returned with appropriate status codes:

| Code | Description |
|------|-------------|
| `NOT_FOUND` | Entity or workflow not found |
| `INVALID_ARGUMENT` | Invalid request parameters |
| `UNAVAILABLE` | Service or dependency unavailable |
| `INTERNAL` | Internal server error |

**Example Error Handling**:
```python
try:
    response = stub.GetEntity(request)
except grpc.RpcError as e:
    if e.code() == grpc.StatusCode.NOT_FOUND:
        print(f"Entity not found: {e.details()}")
    else:
        print(f"Error: {e.code()} - {e.details()}")
```

---

## Best Practices

1. **Request IDs**: Always include unique request IDs for tracing
2. **Batching**: Use `count` parameter for bulk generation instead of multiple calls
3. **Caching**: Enable `use_cache=True` for repeated similar requests
4. **Context**: Provide workflow context for better test data generation
5. **Timeouts**: Set appropriate deadlines for long-running operations

```python
response = stub.GenerateTestData(
    request,
    timeout=30.0  # 30 second timeout
)
```
