from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GenerateRequest(_message.Message):
    __slots__ = ("request_id", "domain", "entity", "count", "context", "scenarios", "output_format", "scenario_counts", "include_edge_cases", "custom_context", "workflow_context", "llm_provider", "temperature", "max_tokens", "inline_schema")
    class ScenarioCountsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    SCENARIOS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FORMAT_FIELD_NUMBER: _ClassVar[int]
    SCENARIO_COUNTS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_EDGE_CASES_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    WORKFLOW_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    LLM_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    MAX_TOKENS_FIELD_NUMBER: _ClassVar[int]
    INLINE_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    domain: str
    entity: str
    count: int
    context: str
    scenarios: _containers.RepeatedScalarFieldContainer[str]
    output_format: str
    scenario_counts: _containers.ScalarMap[str, int]
    include_edge_cases: bool
    custom_context: str
    workflow_context: str
    llm_provider: str
    temperature: float
    max_tokens: int
    inline_schema: str
    def __init__(self, request_id: _Optional[str] = ..., domain: _Optional[str] = ..., entity: _Optional[str] = ..., count: _Optional[int] = ..., context: _Optional[str] = ..., scenarios: _Optional[_Iterable[str]] = ..., output_format: _Optional[str] = ..., scenario_counts: _Optional[_Mapping[str, int]] = ..., include_edge_cases: bool = ..., custom_context: _Optional[str] = ..., workflow_context: _Optional[str] = ..., llm_provider: _Optional[str] = ..., temperature: _Optional[float] = ..., max_tokens: _Optional[int] = ..., inline_schema: _Optional[str] = ...) -> None: ...

class GenerateResponse(_message.Message):
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

class GetSchemasRequest(_message.Message):
    __slots__ = ("domain",)
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    domain: str
    def __init__(self, domain: _Optional[str] = ...) -> None: ...

class GetSchemasResponse(_message.Message):
    __slots__ = ("schemas",)
    SCHEMAS_FIELD_NUMBER: _ClassVar[int]
    schemas: _containers.RepeatedCompositeFieldContainer[Schema]
    def __init__(self, schemas: _Optional[_Iterable[_Union[Schema, _Mapping]]] = ...) -> None: ...

class Schema(_message.Message):
    __slots__ = ("name", "domain", "description", "fields")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    name: str
    domain: str
    description: str
    fields: _containers.RepeatedCompositeFieldContainer[SchemaField]
    def __init__(self, name: _Optional[str] = ..., domain: _Optional[str] = ..., description: _Optional[str] = ..., fields: _Optional[_Iterable[_Union[SchemaField, _Mapping]]] = ...) -> None: ...

class SchemaField(_message.Message):
    __slots__ = ("name", "type", "description", "required", "example")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_FIELD_NUMBER: _ClassVar[int]
    EXAMPLE_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    description: str
    required: bool
    example: str
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ..., description: _Optional[str] = ..., required: bool = ..., example: _Optional[str] = ...) -> None: ...

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
