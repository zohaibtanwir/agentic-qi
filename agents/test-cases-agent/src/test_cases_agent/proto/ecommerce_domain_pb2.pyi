from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DomainContextRequest(_message.Message):
    __slots__ = ("request_id", "entity", "workflow", "scenario", "aspects")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    WORKFLOW_FIELD_NUMBER: _ClassVar[int]
    SCENARIO_FIELD_NUMBER: _ClassVar[int]
    ASPECTS_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    entity: str
    workflow: str
    scenario: str
    aspects: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, request_id: _Optional[str] = ..., entity: _Optional[str] = ..., workflow: _Optional[str] = ..., scenario: _Optional[str] = ..., aspects: _Optional[_Iterable[str]] = ...) -> None: ...

class DomainContextResponse(_message.Message):
    __slots__ = ("request_id", "context", "rules", "relationships", "edge_cases", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    RULES_FIELD_NUMBER: _ClassVar[int]
    RELATIONSHIPS_FIELD_NUMBER: _ClassVar[int]
    EDGE_CASES_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    context: str
    rules: _containers.RepeatedCompositeFieldContainer[BusinessRule]
    relationships: _containers.RepeatedCompositeFieldContainer[EntityRelationship]
    edge_cases: _containers.RepeatedScalarFieldContainer[str]
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, request_id: _Optional[str] = ..., context: _Optional[str] = ..., rules: _Optional[_Iterable[_Union[BusinessRule, _Mapping]]] = ..., relationships: _Optional[_Iterable[_Union[EntityRelationship, _Mapping]]] = ..., edge_cases: _Optional[_Iterable[str]] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class BusinessRule(_message.Message):
    __slots__ = ("id", "name", "description", "entity", "condition", "constraint", "severity")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    CONSTRAINT_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    entity: str
    condition: str
    constraint: str
    severity: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., entity: _Optional[str] = ..., condition: _Optional[str] = ..., constraint: _Optional[str] = ..., severity: _Optional[str] = ...) -> None: ...

class EntityRelationship(_message.Message):
    __slots__ = ("source_entity", "target_entity", "relationship_type", "description", "required")
    SOURCE_ENTITY_FIELD_NUMBER: _ClassVar[int]
    TARGET_ENTITY_FIELD_NUMBER: _ClassVar[int]
    RELATIONSHIP_TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_FIELD_NUMBER: _ClassVar[int]
    source_entity: str
    target_entity: str
    relationship_type: str
    description: str
    required: bool
    def __init__(self, source_entity: _Optional[str] = ..., target_entity: _Optional[str] = ..., relationship_type: _Optional[str] = ..., description: _Optional[str] = ..., required: bool = ...) -> None: ...

class KnowledgeRequest(_message.Message):
    __slots__ = ("request_id", "query", "categories", "max_results")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    CATEGORIES_FIELD_NUMBER: _ClassVar[int]
    MAX_RESULTS_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    query: str
    categories: _containers.RepeatedScalarFieldContainer[str]
    max_results: int
    def __init__(self, request_id: _Optional[str] = ..., query: _Optional[str] = ..., categories: _Optional[_Iterable[str]] = ..., max_results: _Optional[int] = ...) -> None: ...

class KnowledgeResponse(_message.Message):
    __slots__ = ("request_id", "items", "summary")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    items: _containers.RepeatedCompositeFieldContainer[KnowledgeItem]
    summary: str
    def __init__(self, request_id: _Optional[str] = ..., items: _Optional[_Iterable[_Union[KnowledgeItem, _Mapping]]] = ..., summary: _Optional[str] = ...) -> None: ...

class KnowledgeItem(_message.Message):
    __slots__ = ("id", "category", "title", "content", "relevance_score", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    RELEVANCE_SCORE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    id: str
    category: str
    title: str
    content: str
    relevance_score: float
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, id: _Optional[str] = ..., category: _Optional[str] = ..., title: _Optional[str] = ..., content: _Optional[str] = ..., relevance_score: _Optional[float] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class EntityRequest(_message.Message):
    __slots__ = ("entity_name", "include_relationships", "include_rules", "include_edge_cases")
    ENTITY_NAME_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_RELATIONSHIPS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_RULES_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_EDGE_CASES_FIELD_NUMBER: _ClassVar[int]
    entity_name: str
    include_relationships: bool
    include_rules: bool
    include_edge_cases: bool
    def __init__(self, entity_name: _Optional[str] = ..., include_relationships: bool = ..., include_rules: bool = ..., include_edge_cases: bool = ...) -> None: ...

class EntityResponse(_message.Message):
    __slots__ = ("entity",)
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    entity: Entity
    def __init__(self, entity: _Optional[_Union[Entity, _Mapping]] = ...) -> None: ...

class Entity(_message.Message):
    __slots__ = ("name", "description", "fields", "rules", "relationships", "edge_cases", "test_scenarios")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    RULES_FIELD_NUMBER: _ClassVar[int]
    RELATIONSHIPS_FIELD_NUMBER: _ClassVar[int]
    EDGE_CASES_FIELD_NUMBER: _ClassVar[int]
    TEST_SCENARIOS_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    fields: _containers.RepeatedCompositeFieldContainer[EntityField]
    rules: _containers.RepeatedCompositeFieldContainer[BusinessRule]
    relationships: _containers.RepeatedCompositeFieldContainer[EntityRelationship]
    edge_cases: _containers.RepeatedScalarFieldContainer[str]
    test_scenarios: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., fields: _Optional[_Iterable[_Union[EntityField, _Mapping]]] = ..., rules: _Optional[_Iterable[_Union[BusinessRule, _Mapping]]] = ..., relationships: _Optional[_Iterable[_Union[EntityRelationship, _Mapping]]] = ..., edge_cases: _Optional[_Iterable[str]] = ..., test_scenarios: _Optional[_Iterable[str]] = ...) -> None: ...

class EntityField(_message.Message):
    __slots__ = ("name", "type", "description", "required", "validations", "example")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_FIELD_NUMBER: _ClassVar[int]
    VALIDATIONS_FIELD_NUMBER: _ClassVar[int]
    EXAMPLE_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    description: str
    required: bool
    validations: _containers.RepeatedScalarFieldContainer[str]
    example: str
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ..., description: _Optional[str] = ..., required: bool = ..., validations: _Optional[_Iterable[str]] = ..., example: _Optional[str] = ...) -> None: ...

class ListEntitiesRequest(_message.Message):
    __slots__ = ("category",)
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    category: str
    def __init__(self, category: _Optional[str] = ...) -> None: ...

class ListEntitiesResponse(_message.Message):
    __slots__ = ("entities",)
    ENTITIES_FIELD_NUMBER: _ClassVar[int]
    entities: _containers.RepeatedCompositeFieldContainer[EntitySummary]
    def __init__(self, entities: _Optional[_Iterable[_Union[EntitySummary, _Mapping]]] = ...) -> None: ...

class EntitySummary(_message.Message):
    __slots__ = ("name", "description", "category", "field_count")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    FIELD_COUNT_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    category: str
    field_count: int
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., category: _Optional[str] = ..., field_count: _Optional[int] = ...) -> None: ...

class WorkflowRequest(_message.Message):
    __slots__ = ("workflow_name", "include_steps", "include_edge_cases")
    WORKFLOW_NAME_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_STEPS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_EDGE_CASES_FIELD_NUMBER: _ClassVar[int]
    workflow_name: str
    include_steps: bool
    include_edge_cases: bool
    def __init__(self, workflow_name: _Optional[str] = ..., include_steps: bool = ..., include_edge_cases: bool = ...) -> None: ...

class WorkflowResponse(_message.Message):
    __slots__ = ("workflow",)
    WORKFLOW_FIELD_NUMBER: _ClassVar[int]
    workflow: Workflow
    def __init__(self, workflow: _Optional[_Union[Workflow, _Mapping]] = ...) -> None: ...

class Workflow(_message.Message):
    __slots__ = ("name", "description", "steps", "involved_entities", "rules", "edge_cases", "test_scenarios")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    STEPS_FIELD_NUMBER: _ClassVar[int]
    INVOLVED_ENTITIES_FIELD_NUMBER: _ClassVar[int]
    RULES_FIELD_NUMBER: _ClassVar[int]
    EDGE_CASES_FIELD_NUMBER: _ClassVar[int]
    TEST_SCENARIOS_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    steps: _containers.RepeatedCompositeFieldContainer[WorkflowStep]
    involved_entities: _containers.RepeatedScalarFieldContainer[str]
    rules: _containers.RepeatedCompositeFieldContainer[BusinessRule]
    edge_cases: _containers.RepeatedScalarFieldContainer[str]
    test_scenarios: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., steps: _Optional[_Iterable[_Union[WorkflowStep, _Mapping]]] = ..., involved_entities: _Optional[_Iterable[str]] = ..., rules: _Optional[_Iterable[_Union[BusinessRule, _Mapping]]] = ..., edge_cases: _Optional[_Iterable[str]] = ..., test_scenarios: _Optional[_Iterable[str]] = ...) -> None: ...

class WorkflowStep(_message.Message):
    __slots__ = ("order", "name", "description", "entity", "action", "validations", "possible_outcomes")
    ORDER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    VALIDATIONS_FIELD_NUMBER: _ClassVar[int]
    POSSIBLE_OUTCOMES_FIELD_NUMBER: _ClassVar[int]
    order: int
    name: str
    description: str
    entity: str
    action: str
    validations: _containers.RepeatedScalarFieldContainer[str]
    possible_outcomes: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, order: _Optional[int] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., entity: _Optional[str] = ..., action: _Optional[str] = ..., validations: _Optional[_Iterable[str]] = ..., possible_outcomes: _Optional[_Iterable[str]] = ...) -> None: ...

class ListWorkflowsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListWorkflowsResponse(_message.Message):
    __slots__ = ("workflows",)
    WORKFLOWS_FIELD_NUMBER: _ClassVar[int]
    workflows: _containers.RepeatedCompositeFieldContainer[WorkflowSummary]
    def __init__(self, workflows: _Optional[_Iterable[_Union[WorkflowSummary, _Mapping]]] = ...) -> None: ...

class WorkflowSummary(_message.Message):
    __slots__ = ("name", "description", "step_count", "involved_entities")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    STEP_COUNT_FIELD_NUMBER: _ClassVar[int]
    INVOLVED_ENTITIES_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    step_count: int
    involved_entities: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., step_count: _Optional[int] = ..., involved_entities: _Optional[_Iterable[str]] = ...) -> None: ...

class EdgeCasesRequest(_message.Message):
    __slots__ = ("entity", "workflow", "category")
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    WORKFLOW_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    entity: str
    workflow: str
    category: str
    def __init__(self, entity: _Optional[str] = ..., workflow: _Optional[str] = ..., category: _Optional[str] = ...) -> None: ...

class EdgeCasesResponse(_message.Message):
    __slots__ = ("edge_cases",)
    EDGE_CASES_FIELD_NUMBER: _ClassVar[int]
    edge_cases: _containers.RepeatedCompositeFieldContainer[EdgeCase]
    def __init__(self, edge_cases: _Optional[_Iterable[_Union[EdgeCase, _Mapping]]] = ...) -> None: ...

class EdgeCase(_message.Message):
    __slots__ = ("id", "name", "description", "category", "entity", "workflow", "test_approach", "example_data", "expected_behavior", "severity")
    class ExampleDataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    WORKFLOW_FIELD_NUMBER: _ClassVar[int]
    TEST_APPROACH_FIELD_NUMBER: _ClassVar[int]
    EXAMPLE_DATA_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_BEHAVIOR_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    category: str
    entity: str
    workflow: str
    test_approach: str
    example_data: _containers.ScalarMap[str, str]
    expected_behavior: str
    severity: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., category: _Optional[str] = ..., entity: _Optional[str] = ..., workflow: _Optional[str] = ..., test_approach: _Optional[str] = ..., example_data: _Optional[_Mapping[str, str]] = ..., expected_behavior: _Optional[str] = ..., severity: _Optional[str] = ...) -> None: ...

class GenerateTestDataRequest(_message.Message):
    __slots__ = ("request_id", "entity", "count", "workflow_context", "scenarios", "custom_context", "include_edge_cases", "output_format", "scenario_counts")
    class ScenarioCountsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    WORKFLOW_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    SCENARIOS_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_EDGE_CASES_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FORMAT_FIELD_NUMBER: _ClassVar[int]
    SCENARIO_COUNTS_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    entity: str
    count: int
    workflow_context: str
    scenarios: _containers.RepeatedScalarFieldContainer[str]
    custom_context: str
    include_edge_cases: bool
    output_format: str
    scenario_counts: _containers.ScalarMap[str, int]
    def __init__(self, request_id: _Optional[str] = ..., entity: _Optional[str] = ..., count: _Optional[int] = ..., workflow_context: _Optional[str] = ..., scenarios: _Optional[_Iterable[str]] = ..., custom_context: _Optional[str] = ..., include_edge_cases: bool = ..., output_format: _Optional[str] = ..., scenario_counts: _Optional[_Mapping[str, int]] = ...) -> None: ...

class GenerateTestDataResponse(_message.Message):
    __slots__ = ("request_id", "success", "data", "record_count", "metadata", "error")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    RECORD_COUNT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    success: bool
    data: str
    record_count: int
    metadata: GenerationMetadata
    error: str
    def __init__(self, request_id: _Optional[str] = ..., success: bool = ..., data: _Optional[str] = ..., record_count: _Optional[int] = ..., metadata: _Optional[_Union[GenerationMetadata, _Mapping]] = ..., error: _Optional[str] = ...) -> None: ...

class GenerationMetadata(_message.Message):
    __slots__ = ("generation_path", "llm_tokens_used", "generation_time_ms", "coherence_score", "domain_context_used", "scenario_counts")
    class ScenarioCountsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    GENERATION_PATH_FIELD_NUMBER: _ClassVar[int]
    LLM_TOKENS_USED_FIELD_NUMBER: _ClassVar[int]
    GENERATION_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    COHERENCE_SCORE_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_CONTEXT_USED_FIELD_NUMBER: _ClassVar[int]
    SCENARIO_COUNTS_FIELD_NUMBER: _ClassVar[int]
    generation_path: str
    llm_tokens_used: int
    generation_time_ms: float
    coherence_score: float
    domain_context_used: str
    scenario_counts: _containers.ScalarMap[str, int]
    def __init__(self, generation_path: _Optional[str] = ..., llm_tokens_used: _Optional[int] = ..., generation_time_ms: _Optional[float] = ..., coherence_score: _Optional[float] = ..., domain_context_used: _Optional[str] = ..., scenario_counts: _Optional[_Mapping[str, int]] = ...) -> None: ...

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ("status", "components")
    class ComponentsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    STATUS_FIELD_NUMBER: _ClassVar[int]
    COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    status: str
    components: _containers.ScalarMap[str, str]
    def __init__(self, status: _Optional[str] = ..., components: _Optional[_Mapping[str, str]] = ...) -> None: ...
