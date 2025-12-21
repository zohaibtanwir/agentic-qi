from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OutputFormat(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OUTPUT_FORMAT_UNSPECIFIED: _ClassVar[OutputFormat]
    GHERKIN: _ClassVar[OutputFormat]
    TRADITIONAL: _ClassVar[OutputFormat]
    JSON: _ClassVar[OutputFormat]

class CoverageLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COVERAGE_LEVEL_UNSPECIFIED: _ClassVar[CoverageLevel]
    QUICK: _ClassVar[CoverageLevel]
    STANDARD: _ClassVar[CoverageLevel]
    EXHAUSTIVE: _ClassVar[CoverageLevel]

class TestType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TEST_TYPE_UNSPECIFIED: _ClassVar[TestType]
    FUNCTIONAL: _ClassVar[TestType]
    NEGATIVE: _ClassVar[TestType]
    BOUNDARY: _ClassVar[TestType]
    EDGE_CASE: _ClassVar[TestType]
    SECURITY: _ClassVar[TestType]
    PERFORMANCE: _ClassVar[TestType]

class Priority(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRIORITY_UNSPECIFIED: _ClassVar[Priority]
    CRITICAL: _ClassVar[Priority]
    HIGH: _ClassVar[Priority]
    MEDIUM: _ClassVar[Priority]
    LOW: _ClassVar[Priority]

class TestCaseStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TEST_CASE_STATUS_UNSPECIFIED: _ClassVar[TestCaseStatus]
    DRAFT: _ClassVar[TestCaseStatus]
    READY: _ClassVar[TestCaseStatus]
    IN_PROGRESS: _ClassVar[TestCaseStatus]
    PASSED: _ClassVar[TestCaseStatus]
    FAILED: _ClassVar[TestCaseStatus]
    BLOCKED: _ClassVar[TestCaseStatus]
    SKIPPED: _ClassVar[TestCaseStatus]

class TestDataPlacement(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TEST_DATA_PLACEMENT_UNSPECIFIED: _ClassVar[TestDataPlacement]
    EMBEDDED: _ClassVar[TestDataPlacement]
    SEPARATE: _ClassVar[TestDataPlacement]
    BOTH: _ClassVar[TestDataPlacement]

class HealthCheckStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    HEALTH_CHECK_STATUS_UNSPECIFIED: _ClassVar[HealthCheckStatus]
    SERVING: _ClassVar[HealthCheckStatus]
    NOT_SERVING: _ClassVar[HealthCheckStatus]
    SERVICE_UNKNOWN: _ClassVar[HealthCheckStatus]
OUTPUT_FORMAT_UNSPECIFIED: OutputFormat
GHERKIN: OutputFormat
TRADITIONAL: OutputFormat
JSON: OutputFormat
COVERAGE_LEVEL_UNSPECIFIED: CoverageLevel
QUICK: CoverageLevel
STANDARD: CoverageLevel
EXHAUSTIVE: CoverageLevel
TEST_TYPE_UNSPECIFIED: TestType
FUNCTIONAL: TestType
NEGATIVE: TestType
BOUNDARY: TestType
EDGE_CASE: TestType
SECURITY: TestType
PERFORMANCE: TestType
PRIORITY_UNSPECIFIED: Priority
CRITICAL: Priority
HIGH: Priority
MEDIUM: Priority
LOW: Priority
TEST_CASE_STATUS_UNSPECIFIED: TestCaseStatus
DRAFT: TestCaseStatus
READY: TestCaseStatus
IN_PROGRESS: TestCaseStatus
PASSED: TestCaseStatus
FAILED: TestCaseStatus
BLOCKED: TestCaseStatus
SKIPPED: TestCaseStatus
TEST_DATA_PLACEMENT_UNSPECIFIED: TestDataPlacement
EMBEDDED: TestDataPlacement
SEPARATE: TestDataPlacement
BOTH: TestDataPlacement
HEALTH_CHECK_STATUS_UNSPECIFIED: HealthCheckStatus
SERVING: HealthCheckStatus
NOT_SERVING: HealthCheckStatus
SERVICE_UNKNOWN: HealthCheckStatus

class GenerateTestCasesRequest(_message.Message):
    __slots__ = ("request_id", "user_story", "api_spec", "free_form", "domain_config", "generation_config", "test_data_config")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    USER_STORY_FIELD_NUMBER: _ClassVar[int]
    API_SPEC_FIELD_NUMBER: _ClassVar[int]
    FREE_FORM_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_CONFIG_FIELD_NUMBER: _ClassVar[int]
    GENERATION_CONFIG_FIELD_NUMBER: _ClassVar[int]
    TEST_DATA_CONFIG_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    user_story: UserStoryInput
    api_spec: ApiSpecInput
    free_form: FreeFormInput
    domain_config: DomainConfig
    generation_config: GenerationConfig
    test_data_config: TestDataConfig
    def __init__(self, request_id: _Optional[str] = ..., user_story: _Optional[_Union[UserStoryInput, _Mapping]] = ..., api_spec: _Optional[_Union[ApiSpecInput, _Mapping]] = ..., free_form: _Optional[_Union[FreeFormInput, _Mapping]] = ..., domain_config: _Optional[_Union[DomainConfig, _Mapping]] = ..., generation_config: _Optional[_Union[GenerationConfig, _Mapping]] = ..., test_data_config: _Optional[_Union[TestDataConfig, _Mapping]] = ...) -> None: ...

class UserStoryInput(_message.Message):
    __slots__ = ("story", "acceptance_criteria", "additional_context")
    STORY_FIELD_NUMBER: _ClassVar[int]
    ACCEPTANCE_CRITERIA_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    story: str
    acceptance_criteria: _containers.RepeatedScalarFieldContainer[str]
    additional_context: str
    def __init__(self, story: _Optional[str] = ..., acceptance_criteria: _Optional[_Iterable[str]] = ..., additional_context: _Optional[str] = ...) -> None: ...

class ApiSpecInput(_message.Message):
    __slots__ = ("spec", "spec_format", "endpoints")
    SPEC_FIELD_NUMBER: _ClassVar[int]
    SPEC_FORMAT_FIELD_NUMBER: _ClassVar[int]
    ENDPOINTS_FIELD_NUMBER: _ClassVar[int]
    spec: str
    spec_format: str
    endpoints: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, spec: _Optional[str] = ..., spec_format: _Optional[str] = ..., endpoints: _Optional[_Iterable[str]] = ...) -> None: ...

class FreeFormInput(_message.Message):
    __slots__ = ("requirement", "context")
    class ContextEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    REQUIREMENT_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    requirement: str
    context: _containers.ScalarMap[str, str]
    def __init__(self, requirement: _Optional[str] = ..., context: _Optional[_Mapping[str, str]] = ...) -> None: ...

class FreeFormRequirement(_message.Message):
    __slots__ = ("requirement_text", "context_info")
    class ContextInfoEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    REQUIREMENT_TEXT_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_INFO_FIELD_NUMBER: _ClassVar[int]
    requirement_text: str
    context_info: _containers.ScalarMap[str, str]
    def __init__(self, requirement_text: _Optional[str] = ..., context_info: _Optional[_Mapping[str, str]] = ...) -> None: ...

class DomainConfig(_message.Message):
    __slots__ = ("domain", "entity", "workflow", "include_business_rules", "include_edge_cases")
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    WORKFLOW_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_BUSINESS_RULES_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_EDGE_CASES_FIELD_NUMBER: _ClassVar[int]
    domain: str
    entity: str
    workflow: str
    include_business_rules: bool
    include_edge_cases: bool
    def __init__(self, domain: _Optional[str] = ..., entity: _Optional[str] = ..., workflow: _Optional[str] = ..., include_business_rules: bool = ..., include_edge_cases: bool = ...) -> None: ...

class GenerationConfig(_message.Message):
    __slots__ = ("output_format", "coverage_level", "test_types", "llm_provider", "check_duplicates", "max_test_cases", "priority_focus", "count", "include_edge_cases", "include_negative_tests", "detail_level")
    OUTPUT_FORMAT_FIELD_NUMBER: _ClassVar[int]
    COVERAGE_LEVEL_FIELD_NUMBER: _ClassVar[int]
    TEST_TYPES_FIELD_NUMBER: _ClassVar[int]
    LLM_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    CHECK_DUPLICATES_FIELD_NUMBER: _ClassVar[int]
    MAX_TEST_CASES_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FOCUS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_EDGE_CASES_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_NEGATIVE_TESTS_FIELD_NUMBER: _ClassVar[int]
    DETAIL_LEVEL_FIELD_NUMBER: _ClassVar[int]
    output_format: OutputFormat
    coverage_level: CoverageLevel
    test_types: _containers.RepeatedScalarFieldContainer[TestType]
    llm_provider: str
    check_duplicates: bool
    max_test_cases: int
    priority_focus: str
    count: int
    include_edge_cases: bool
    include_negative_tests: bool
    detail_level: str
    def __init__(self, output_format: _Optional[_Union[OutputFormat, str]] = ..., coverage_level: _Optional[_Union[CoverageLevel, str]] = ..., test_types: _Optional[_Iterable[_Union[TestType, str]]] = ..., llm_provider: _Optional[str] = ..., check_duplicates: bool = ..., max_test_cases: _Optional[int] = ..., priority_focus: _Optional[str] = ..., count: _Optional[int] = ..., include_edge_cases: bool = ..., include_negative_tests: bool = ..., detail_level: _Optional[str] = ...) -> None: ...

class TestDataConfig(_message.Message):
    __slots__ = ("generate_test_data", "placement", "samples_per_case")
    GENERATE_TEST_DATA_FIELD_NUMBER: _ClassVar[int]
    PLACEMENT_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_PER_CASE_FIELD_NUMBER: _ClassVar[int]
    generate_test_data: bool
    placement: TestDataPlacement
    samples_per_case: int
    def __init__(self, generate_test_data: bool = ..., placement: _Optional[_Union[TestDataPlacement, str]] = ..., samples_per_case: _Optional[int] = ...) -> None: ...

class GenerateTestCasesResponse(_message.Message):
    __slots__ = ("request_id", "success", "test_cases", "metadata", "error_message")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    TEST_CASES_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    success: bool
    test_cases: _containers.RepeatedCompositeFieldContainer[TestCase]
    metadata: GenerationMetadata
    error_message: str
    def __init__(self, request_id: _Optional[str] = ..., success: bool = ..., test_cases: _Optional[_Iterable[_Union[TestCase, _Mapping]]] = ..., metadata: _Optional[_Union[GenerationMetadata, _Mapping]] = ..., error_message: _Optional[str] = ...) -> None: ...

class TestCase(_message.Message):
    __slots__ = ("id", "title", "description", "type", "priority", "tags", "requirement_id", "preconditions", "steps", "gherkin", "test_data", "expected_result", "postconditions", "status")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    REQUIREMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PRECONDITIONS_FIELD_NUMBER: _ClassVar[int]
    STEPS_FIELD_NUMBER: _ClassVar[int]
    GHERKIN_FIELD_NUMBER: _ClassVar[int]
    TEST_DATA_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_RESULT_FIELD_NUMBER: _ClassVar[int]
    POSTCONDITIONS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: str
    title: str
    description: str
    type: TestType
    priority: Priority
    tags: _containers.RepeatedScalarFieldContainer[str]
    requirement_id: str
    preconditions: _containers.RepeatedScalarFieldContainer[str]
    steps: _containers.RepeatedCompositeFieldContainer[TestStep]
    gherkin: str
    test_data: TestData
    expected_result: str
    postconditions: _containers.RepeatedScalarFieldContainer[str]
    status: TestCaseStatus
    def __init__(self, id: _Optional[str] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[TestType, str]] = ..., priority: _Optional[_Union[Priority, str]] = ..., tags: _Optional[_Iterable[str]] = ..., requirement_id: _Optional[str] = ..., preconditions: _Optional[_Iterable[str]] = ..., steps: _Optional[_Iterable[_Union[TestStep, _Mapping]]] = ..., gherkin: _Optional[str] = ..., test_data: _Optional[_Union[TestData, _Mapping]] = ..., expected_result: _Optional[str] = ..., postconditions: _Optional[_Iterable[str]] = ..., status: _Optional[_Union[TestCaseStatus, str]] = ...) -> None: ...

class TestStep(_message.Message):
    __slots__ = ("order", "action", "expected_result", "test_data")
    ORDER_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_RESULT_FIELD_NUMBER: _ClassVar[int]
    TEST_DATA_FIELD_NUMBER: _ClassVar[int]
    order: int
    action: str
    expected_result: str
    test_data: str
    def __init__(self, order: _Optional[int] = ..., action: _Optional[str] = ..., expected_result: _Optional[str] = ..., test_data: _Optional[str] = ...) -> None: ...

class TestData(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[TestDataItem]
    def __init__(self, items: _Optional[_Iterable[_Union[TestDataItem, _Mapping]]] = ...) -> None: ...

class TestDataItem(_message.Message):
    __slots__ = ("field", "value", "description")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    field: str
    value: str
    description: str
    def __init__(self, field: _Optional[str] = ..., value: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class GenerationMetadata(_message.Message):
    __slots__ = ("llm_provider", "llm_model", "llm_tokens_used", "generation_time_ms", "test_cases_generated", "duplicates_found", "coverage", "domain_context_used")
    LLM_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    LLM_MODEL_FIELD_NUMBER: _ClassVar[int]
    LLM_TOKENS_USED_FIELD_NUMBER: _ClassVar[int]
    GENERATION_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    TEST_CASES_GENERATED_FIELD_NUMBER: _ClassVar[int]
    DUPLICATES_FOUND_FIELD_NUMBER: _ClassVar[int]
    COVERAGE_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_CONTEXT_USED_FIELD_NUMBER: _ClassVar[int]
    llm_provider: str
    llm_model: str
    llm_tokens_used: int
    generation_time_ms: float
    test_cases_generated: int
    duplicates_found: int
    coverage: CoverageAnalysis
    domain_context_used: str
    def __init__(self, llm_provider: _Optional[str] = ..., llm_model: _Optional[str] = ..., llm_tokens_used: _Optional[int] = ..., generation_time_ms: _Optional[float] = ..., test_cases_generated: _Optional[int] = ..., duplicates_found: _Optional[int] = ..., coverage: _Optional[_Union[CoverageAnalysis, _Mapping]] = ..., domain_context_used: _Optional[str] = ...) -> None: ...

class CoverageAnalysis(_message.Message):
    __slots__ = ("functional_count", "negative_count", "boundary_count", "edge_case_count", "uncovered_areas")
    FUNCTIONAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    NEGATIVE_COUNT_FIELD_NUMBER: _ClassVar[int]
    BOUNDARY_COUNT_FIELD_NUMBER: _ClassVar[int]
    EDGE_CASE_COUNT_FIELD_NUMBER: _ClassVar[int]
    UNCOVERED_AREAS_FIELD_NUMBER: _ClassVar[int]
    functional_count: int
    negative_count: int
    boundary_count: int
    edge_case_count: int
    uncovered_areas: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, functional_count: _Optional[int] = ..., negative_count: _Optional[int] = ..., boundary_count: _Optional[int] = ..., edge_case_count: _Optional[int] = ..., uncovered_areas: _Optional[_Iterable[str]] = ...) -> None: ...

class GetTestCaseRequest(_message.Message):
    __slots__ = ("test_case_id",)
    TEST_CASE_ID_FIELD_NUMBER: _ClassVar[int]
    test_case_id: str
    def __init__(self, test_case_id: _Optional[str] = ...) -> None: ...

class GetTestCaseResponse(_message.Message):
    __slots__ = ("test_case",)
    TEST_CASE_FIELD_NUMBER: _ClassVar[int]
    test_case: TestCase
    def __init__(self, test_case: _Optional[_Union[TestCase, _Mapping]] = ...) -> None: ...

class ListTestCasesRequest(_message.Message):
    __slots__ = ("domain", "entity", "type", "search_query", "limit", "offset")
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SEARCH_QUERY_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    domain: str
    entity: str
    type: TestType
    search_query: str
    limit: int
    offset: int
    def __init__(self, domain: _Optional[str] = ..., entity: _Optional[str] = ..., type: _Optional[_Union[TestType, str]] = ..., search_query: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class ListTestCasesResponse(_message.Message):
    __slots__ = ("test_cases", "total_count")
    TEST_CASES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    test_cases: _containers.RepeatedCompositeFieldContainer[TestCaseSummary]
    total_count: int
    def __init__(self, test_cases: _Optional[_Iterable[_Union[TestCaseSummary, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class TestCaseSummary(_message.Message):
    __slots__ = ("id", "title", "type", "priority", "domain", "entity", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    title: str
    type: TestType
    priority: Priority
    domain: str
    entity: str
    created_at: str
    def __init__(self, id: _Optional[str] = ..., title: _Optional[str] = ..., type: _Optional[_Union[TestType, str]] = ..., priority: _Optional[_Union[Priority, str]] = ..., domain: _Optional[str] = ..., entity: _Optional[str] = ..., created_at: _Optional[str] = ...) -> None: ...

class StoreTestCasesRequest(_message.Message):
    __slots__ = ("test_cases", "domain", "entity", "source")
    TEST_CASES_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    test_cases: _containers.RepeatedCompositeFieldContainer[TestCase]
    domain: str
    entity: str
    source: str
    def __init__(self, test_cases: _Optional[_Iterable[_Union[TestCase, _Mapping]]] = ..., domain: _Optional[str] = ..., entity: _Optional[str] = ..., source: _Optional[str] = ...) -> None: ...

class StoreTestCasesResponse(_message.Message):
    __slots__ = ("success", "stored_count", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    STORED_COUNT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    stored_count: int
    error: str
    def __init__(self, success: bool = ..., stored_count: _Optional[int] = ..., error: _Optional[str] = ...) -> None: ...

class AnalyzeCoverageRequest(_message.Message):
    __slots__ = ("request_id", "user_story", "api_spec", "existing_test_case_ids")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    USER_STORY_FIELD_NUMBER: _ClassVar[int]
    API_SPEC_FIELD_NUMBER: _ClassVar[int]
    EXISTING_TEST_CASE_IDS_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    user_story: UserStoryInput
    api_spec: ApiSpecInput
    existing_test_case_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, request_id: _Optional[str] = ..., user_story: _Optional[_Union[UserStoryInput, _Mapping]] = ..., api_spec: _Optional[_Union[ApiSpecInput, _Mapping]] = ..., existing_test_case_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class AnalyzeCoverageResponse(_message.Message):
    __slots__ = ("request_id", "report")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    REPORT_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    report: CoverageReport
    def __init__(self, request_id: _Optional[str] = ..., report: _Optional[_Union[CoverageReport, _Mapping]] = ...) -> None: ...

class CoverageReport(_message.Message):
    __slots__ = ("overall_coverage", "gaps", "recommendations")
    OVERALL_COVERAGE_FIELD_NUMBER: _ClassVar[int]
    GAPS_FIELD_NUMBER: _ClassVar[int]
    RECOMMENDATIONS_FIELD_NUMBER: _ClassVar[int]
    overall_coverage: float
    gaps: _containers.RepeatedCompositeFieldContainer[CoverageGap]
    recommendations: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, overall_coverage: _Optional[float] = ..., gaps: _Optional[_Iterable[_Union[CoverageGap, _Mapping]]] = ..., recommendations: _Optional[_Iterable[str]] = ...) -> None: ...

class CoverageGap(_message.Message):
    __slots__ = ("area", "type", "severity", "suggestion")
    AREA_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    SUGGESTION_FIELD_NUMBER: _ClassVar[int]
    area: str
    type: str
    severity: str
    suggestion: str
    def __init__(self, area: _Optional[str] = ..., type: _Optional[str] = ..., severity: _Optional[str] = ..., suggestion: _Optional[str] = ...) -> None: ...

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ("status", "version", "components")
    class ComponentsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    status: HealthCheckStatus
    version: str
    components: _containers.ScalarMap[str, str]
    def __init__(self, status: _Optional[_Union[HealthCheckStatus, str]] = ..., version: _Optional[str] = ..., components: _Optional[_Mapping[str, str]] = ...) -> None: ...
