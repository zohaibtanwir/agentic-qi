'use client';

import { useState } from 'react';

type Agent = 'requirement-analysis' | 'test-cases' | 'test-data' | 'ecommerce-domain';

interface ApiEndpoint {
  method: string;
  name: string;
  description: string;
  request?: string;
  response?: string;
}

interface RestEndpoint {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  path: string;
  description: string;
  request?: string;
  response?: string;
}

interface AgentDocs {
  name: string;
  description: string;
  grpcPort: number;
  httpPort: number;
  package: string;
  service: string;
  endpoints: ApiEndpoint[];
  restEndpoints?: RestEndpoint[];
}

const agentDocs: Record<Agent, AgentDocs> = {
  'requirement-analysis': {
    name: 'Requirement Analysis Agent',
    description: 'Analyzes requirements from multiple input formats, assesses quality, identifies gaps, and prepares structured output for test case generation.',
    grpcPort: 9004,
    httpPort: 8084,
    package: 'requirementanalysis.v1',
    service: 'RequirementAnalysisService',
    endpoints: [
      {
        method: 'rpc',
        name: 'AnalyzeRequirement',
        description: 'Analyze a requirement from any input type (Jira, free-form, transcript)',
        request: `message AnalyzeRequest {
  string request_id = 1;
  oneof input {
    JiraStoryInput jira_story = 2;
    FreeFormInput free_form = 3;
    TranscriptInput transcript = 4;
  }
  AnalysisConfig config = 5;
}`,
        response: `message AnalyzeResponse {
  string request_id = 1;
  bool success = 2;
  QualityScore quality_score = 3;
  ExtractedRequirement extracted_requirement = 4;
  repeated Gap gaps = 5;
  repeated ClarifyingQuestion questions = 6;
  repeated GeneratedAC generated_acs = 7;
  DomainValidation domain_validation = 8;
  bool ready_for_test_generation = 9;
  repeated string blockers = 10;
  AnalysisMetadata metadata = 11;
  string error = 12;
}`,
      },
      {
        method: 'rpc',
        name: 'ReanalyzeRequirement',
        description: 'Re-analyze with updates (questions answered, edits made)',
        request: `message ReanalyzeRequest {
  string request_id = 1;
  string original_request_id = 2;
  string updated_title = 3;
  string updated_description = 4;
  repeated string updated_acs = 5;
  repeated AnsweredQuestion answered_questions = 6;
  repeated ACDecision ac_decisions = 7;
  string additional_context = 8;
  AnalysisConfig config = 9;
}`,
        response: `// Returns AnalyzeResponse`,
      },
      {
        method: 'rpc',
        name: 'ExportAnalysis',
        description: 'Export analysis report in text or JSON format',
        request: `message ExportRequest {
  string request_id = 1;
  string analysis_request_id = 2;
  string format = 3;  // "text" or "json"
  bool include_recommendations = 4;
  bool include_generated_acs = 5;
}`,
        response: `message ExportResponse {
  string request_id = 1;
  bool success = 2;
  string format = 3;
  string content = 4;
  string filename = 5;
  string error = 6;
}`,
      },
      {
        method: 'rpc',
        name: 'ForwardToTestCases',
        description: 'Forward analyzed requirement to Test Cases Agent',
        request: `message ForwardRequest {
  string request_id = 1;
  string analysis_request_id = 2;
  bool include_generated_acs = 3;
  bool include_domain_context = 4;
  TestCasesConfig test_cases_config = 5;
}`,
        response: `message ForwardResponse {
  string request_id = 1;
  bool success = 2;
  string test_cases_request_id = 3;
  int32 test_cases_generated = 4;
  string structured_requirement_json = 5;
  string error = 6;
}`,
      },
      {
        method: 'rpc',
        name: 'ListHistory',
        description: 'List analysis history with pagination and filters',
        request: `message ListHistoryRequest {
  int32 limit = 1;
  int32 offset = 2;
  HistoryFilters filters = 3;
}`,
        response: `message ListHistoryResponse {
  repeated HistorySessionSummary sessions = 1;
  int32 total_count = 2;
  bool has_more = 3;
}`,
      },
      {
        method: 'rpc',
        name: 'GetHistorySession',
        description: 'Get full details of a history session',
        request: `message GetHistorySessionRequest {
  string session_id = 1;
}`,
        response: `message GetHistorySessionResponse {
  bool success = 1;
  HistorySession session = 2;
  string error = 3;
}`,
      },
      {
        method: 'rpc',
        name: 'HealthCheck',
        description: 'Health check endpoint',
        request: `message HealthCheckRequest {}`,
        response: `message HealthCheckResponse {
  string status = 1;
  map<string, string> components = 2;
}`,
      },
    ],
  },
  'test-cases': {
    name: 'Test Cases Agent',
    description: 'Generate comprehensive test cases from user stories, API specs, or free-form requirements with domain enrichment.',
    grpcPort: 9003,
    httpPort: 8083,
    package: 'testcases.v1',
    service: 'TestCasesService',
    endpoints: [
      {
        method: 'rpc',
        name: 'GenerateTestCases',
        description: 'Generate test cases from requirements',
        request: `message GenerateTestCasesRequest {
  string request_id = 1;
  oneof input {
    UserStoryInput user_story = 2;
    ApiSpecInput api_spec = 3;
    FreeFormInput free_form = 4;
  }
  DomainConfig domain_config = 5;
  GenerationConfig generation_config = 6;
  TestDataConfig test_data_config = 7;
}`,
        response: `message GenerateTestCasesResponse {
  string request_id = 1;
  bool success = 2;
  repeated TestCase test_cases = 3;
  GenerationMetadata metadata = 4;
  string error_message = 5;
}`,
      },
      {
        method: 'rpc',
        name: 'GetTestCase',
        description: 'Get a specific test case by ID',
        request: `message GetTestCaseRequest {
  string test_case_id = 1;
}`,
        response: `message GetTestCaseResponse {
  TestCase test_case = 1;
}`,
      },
      {
        method: 'rpc',
        name: 'ListTestCases',
        description: 'List historical test cases with filters',
        request: `message ListTestCasesRequest {
  string domain = 1;
  string entity = 2;
  TestType type = 3;
  string search_query = 4;
  int32 limit = 5;
  int32 offset = 6;
}`,
        response: `message ListTestCasesResponse {
  repeated TestCaseSummary test_cases = 1;
  int32 total_count = 2;
}`,
      },
      {
        method: 'rpc',
        name: 'StoreTestCases',
        description: 'Store test cases for learning',
        request: `message StoreTestCasesRequest {
  repeated TestCase test_cases = 1;
  string domain = 2;
  string entity = 3;
  string source = 4;  // manual, generated, imported
}`,
        response: `message StoreTestCasesResponse {
  bool success = 1;
  int32 stored_count = 2;
  string error = 3;
}`,
      },
      {
        method: 'rpc',
        name: 'AnalyzeCoverage',
        description: 'Get coverage analysis for requirements',
        request: `message AnalyzeCoverageRequest {
  string request_id = 1;
  oneof input {
    UserStoryInput user_story = 2;
    ApiSpecInput api_spec = 3;
  }
  repeated string existing_test_case_ids = 4;
}`,
        response: `message AnalyzeCoverageResponse {
  string request_id = 1;
  CoverageReport report = 2;
}`,
      },
      {
        method: 'rpc',
        name: 'ListHistory',
        description: 'List generation history sessions',
        request: `message ListHistoryRequest {
  int32 limit = 1;
  int32 offset = 2;
  string domain = 3;
  string status = 4;
}`,
        response: `message ListHistoryResponse {
  repeated HistorySessionSummary sessions = 1;
  int32 total_count = 2;
}`,
      },
      {
        method: 'rpc',
        name: 'HealthCheck',
        description: 'Health check endpoint',
        request: `message HealthCheckRequest {}`,
        response: `message HealthCheckResponse {
  HealthCheckStatus status = 1;
  string version = 2;
  map<string, string> components = 3;
}`,
      },
    ],
  },
  'test-data': {
    name: 'Test Data Agent',
    description: 'Generate realistic, schema-compliant test data with support for multiple output formats and generation methods.',
    grpcPort: 9091,
    httpPort: 8091,
    package: 'testdata.v1',
    service: 'TestDataService',
    endpoints: [
      {
        method: 'rpc',
        name: 'GenerateData',
        description: 'Synchronous generation for small requests (<1000 records)',
        request: `message GenerateRequest {
  string request_id = 1;
  string domain = 2;
  string entity = 3;
  Schema schema = 4;
  Constraints constraints = 5;
  repeated Scenario scenarios = 6;
  string context = 7;
  repeated string hints = 8;
  OutputFormat output_format = 9;  // JSON, CSV, SQL
  int32 count = 10;
  bool use_cache = 11;
  bool learn_from_history = 12;
  bool defect_triggering = 13;
  bool production_like = 14;
  string inline_schema = 15;
  GenerationMethod generation_method = 16;
  string custom_schema = 17;
}`,
        response: `message GenerateResponse {
  string request_id = 1;
  bool success = 2;
  string data = 3;  // JSON string
  int32 record_count = 4;
  GenerationMetadata metadata = 5;
  string error = 6;
}`,
      },
      {
        method: 'rpc',
        name: 'GenerateDataStream',
        description: 'Streaming for large requests',
        request: `// Same as GenerateRequest`,
        response: `stream DataChunk {
  string request_id = 1;
  string data = 2;
  int32 chunk_index = 3;
  bool is_final = 4;
}`,
      },
      {
        method: 'rpc',
        name: 'GetSchemas',
        description: 'List available schemas',
        request: `message GetSchemasRequest {
  string domain = 1;
}`,
        response: `message GetSchemasResponse {
  repeated SchemaInfo schemas = 1;
}`,
      },
      {
        method: 'rpc',
        name: 'HealthCheck',
        description: 'Health check endpoint',
        request: `message HealthCheckRequest {}`,
        response: `message HealthCheckResponse {
  string status = 1;
  map<string, string> components = 2;
}`,
      },
    ],
    restEndpoints: [
      {
        method: 'POST',
        path: '/generate',
        description: 'Generate test data via HTTP',
        request: `{
  "domain": "ecommerce",
  "entity": "customer",
  "count": 10,
  "context": "Premium customers",
  "scenarios": [
    { "name": "VIP", "description": "VIP customers" }
  ],
  "hints": ["use realistic names"],
  "outputFormat": "JSON",
  "inlineSchema": "optional custom schema"
}`,
        response: `{
  "success": true,
  "requestId": "http-customer-10",
  "data": [...],
  "recordCount": 10,
  "metadata": {
    "generationPath": "llm",
    "llmTokensUsed": 1500,
    "generationTimeMs": 2500,
    "coherenceScore": 0.95
  }
}`,
      },
      {
        method: 'GET',
        path: '/schemas',
        description: 'List available schemas',
        request: `Query params: ?domain=ecommerce`,
        response: `{
  "schemas": [
    {
      "name": "customer",
      "description": "Customer entity",
      "fields": [
        { "name": "id", "type": "UUID", "required": true }
      ],
      "domain": "ecommerce"
    }
  ]
}`,
      },
    ],
  },
  'ecommerce-domain': {
    name: 'eCommerce Domain Agent',
    description: 'Specialized agent with deep eCommerce domain knowledge including entities, workflows, business rules, and edge cases.',
    grpcPort: 9002,
    httpPort: 8082,
    package: 'ecommerce.domain.v1',
    service: 'EcommerceDomainService',
    endpoints: [
      {
        method: 'rpc',
        name: 'GetDomainContext',
        description: 'Get domain context for test generation',
        request: `message DomainContextRequest {
  string request_id = 1;
  string entity = 2;
  string workflow = 3;
  string scenario = 4;
  repeated string aspects = 5;
}`,
        response: `message DomainContextResponse {
  string request_id = 1;
  string context = 2;
  repeated BusinessRule rules = 3;
  repeated EntityRelationship relationships = 4;
  repeated string edge_cases = 5;
  map<string, string> metadata = 6;
}`,
      },
      {
        method: 'rpc',
        name: 'QueryKnowledge',
        description: 'Query domain knowledge base',
        request: `message KnowledgeRequest {
  string request_id = 1;
  string query = 2;
  repeated string categories = 3;
  int32 max_results = 4;
}`,
        response: `message KnowledgeResponse {
  string request_id = 1;
  repeated KnowledgeItem items = 2;
  string summary = 3;
}`,
      },
      {
        method: 'rpc',
        name: 'GetEntity',
        description: 'Get entity details with relationships and rules',
        request: `message EntityRequest {
  string entity_name = 1;
  bool include_relationships = 2;
  bool include_rules = 3;
  bool include_edge_cases = 4;
}`,
        response: `message EntityResponse {
  Entity entity = 1;
}`,
      },
      {
        method: 'rpc',
        name: 'GetWorkflow',
        description: 'Get workflow details with steps',
        request: `message WorkflowRequest {
  string workflow_name = 1;
  bool include_steps = 2;
  bool include_edge_cases = 3;
}`,
        response: `message WorkflowResponse {
  Workflow workflow = 1;
}`,
      },
      {
        method: 'rpc',
        name: 'ListEntities',
        description: 'List all available entities',
        request: `message ListEntitiesRequest {
  string category = 1;
}`,
        response: `message ListEntitiesResponse {
  repeated EntitySummary entities = 1;
}`,
      },
      {
        method: 'rpc',
        name: 'ListWorkflows',
        description: 'List all available workflows',
        request: `message ListWorkflowsRequest {}`,
        response: `message ListWorkflowsResponse {
  repeated WorkflowSummary workflows = 1;
}`,
      },
      {
        method: 'rpc',
        name: 'GetEdgeCases',
        description: 'Get edge cases for an entity/workflow',
        request: `message EdgeCasesRequest {
  string entity = 1;
  string workflow = 2;
  string category = 3;
}`,
        response: `message EdgeCasesResponse {
  repeated EdgeCase edge_cases = 1;
}`,
      },
      {
        method: 'rpc',
        name: 'GenerateTestData',
        description: 'Generate test data with domain context (proxies to Test Data Agent)',
        request: `message GenerateTestDataRequest {
  string request_id = 1;
  string entity = 2;
  int32 count = 3;
  string workflow_context = 4;
  repeated string scenarios = 5;
  string custom_context = 6;
  bool include_edge_cases = 7;
  string output_format = 8;
  map<string, int32> scenario_counts = 9;
  GenerationMethod generation_method = 10;
  bool production_like = 11;
  bool use_cache = 12;
}`,
        response: `message GenerateTestDataResponse {
  string request_id = 1;
  bool success = 2;
  string data = 3;
  int32 record_count = 4;
  GenerationMetadata metadata = 5;
  string error = 6;
}`,
      },
      {
        method: 'rpc',
        name: 'HealthCheck',
        description: 'Health check endpoint',
        request: `message HealthCheckRequest {}`,
        response: `message HealthCheckResponse {
  string status = 1;
  map<string, string> components = 2;
}`,
      },
    ],
    restEndpoints: [
      {
        method: 'POST',
        path: '/api/generate',
        description: 'Generate test data via orchestration',
        request: `{
  "entity": "order",
  "count": 10,
  "workflow": "checkout",
  "scenario": "happy_path",
  "context": "Black Friday sale",
  "output_format": "JSON",
  "include_edge_cases": true,
  "production_like": true,
  "generation_method": "HYBRID"
}`,
        response: `{
  "success": true,
  "data": "[...]",
  "metadata": {
    "request_id": "...",
    "entity": "order",
    "record_count": 10,
    "generation_method": "HYBRID"
  }
}`,
      },
      {
        method: 'GET',
        path: '/api/entities',
        description: 'List available entities',
        response: `{
  "predefined": ["customer", "product", "order"],
  "domain": ["cart", "payment", "shipment"]
}`,
      },
      {
        method: 'POST',
        path: '/api/test-cases',
        description: 'Generate test cases for an entity',
        request: `{
  "entity": "checkout",
  "workflow": "standard_checkout",
  "test_types": ["functional", "negative"],
  "generation_method": "llm",
  "count": 10,
  "include_edge_cases": true
}`,
        response: `{
  "success": true,
  "test_suite": {
    "id": "...",
    "name": "Checkout Test Suite",
    "total_cases": 10,
    "test_cases": [...]
  }
}`,
      },
      {
        method: 'POST',
        path: '/api/defect-prediction',
        description: 'Predict defects for an entity',
        request: `{
  "entity": "payment",
  "workflow": "payment_processing",
  "generation_method": "llm"
}`,
        response: `{
  "success": true,
  "analysis": {
    "total_predictions": 5,
    "high_risk_count": 2,
    "risk_score": 0.7,
    "predictions": [...]
  }
}`,
      },
      {
        method: 'POST',
        path: '/api/business-rules',
        description: 'Validate business rules for test data',
        request: `{
  "entity": "order",
  "test_data": { "total": 100, "discount": 150 },
  "workflow": "checkout"
}`,
        response: `{
  "success": true,
  "validation_report": {
    "total_rules": 10,
    "passed": 8,
    "failed": 2,
    "compliance_score": 0.8
  }
}`,
      },
      {
        method: 'POST',
        path: '/api/journey-monitoring',
        description: 'Monitor customer journey',
        request: `{
  "customer_id": "CUST-123",
  "real_time": false,
  "time_period": "24h"
}`,
        response: `{
  "success": true,
  "journey_data": {
    "journey_id": "...",
    "current_stage": "checkout",
    "health": "healthy",
    "steps": [...]
  }
}`,
      },
    ],
  },
};

function CodeBlock({ code }: { code: string }) {
  return (
    <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm font-mono">
      <code>{code}</code>
    </pre>
  );
}

function EndpointCard({ endpoint, isRest = false }: { endpoint: ApiEndpoint | RestEndpoint; isRest?: boolean }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const methodColors: Record<string, string> = {
    rpc: 'bg-blue-100 text-blue-800',
    GET: 'bg-green-100 text-green-800',
    POST: 'bg-yellow-100 text-yellow-800',
    PUT: 'bg-orange-100 text-orange-800',
    DELETE: 'bg-red-100 text-red-800',
  };

  const method = isRest ? (endpoint as RestEndpoint).method : 'rpc';
  const name = isRest ? (endpoint as RestEndpoint).path : (endpoint as ApiEndpoint).name;

  return (
    <div className="border border-[var(--border-default)] rounded-lg mb-4">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className={`px-2 py-1 rounded text-xs font-mono font-bold ${methodColors[method]}`}>
            {method}
          </span>
          <span className="font-mono font-medium text-[var(--text-primary)]">{name}</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-[var(--text-muted)]">{endpoint.description}</span>
          <svg
            className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {isExpanded && (
        <div className="border-t border-[var(--border-default)] p-4 space-y-4">
          {endpoint.request && (
            <div>
              <h4 className="text-sm font-semibold text-[var(--text-secondary)] mb-2">Request</h4>
              <CodeBlock code={endpoint.request} />
            </div>
          )}
          {endpoint.response && (
            <div>
              <h4 className="text-sm font-semibold text-[var(--text-secondary)] mb-2">Response</h4>
              <CodeBlock code={endpoint.response} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function AgentSection({ agent, docs }: { agent: Agent; docs: AgentDocs }) {
  return (
    <div id={agent} className="mb-12 scroll-mt-24">
      <div className="bg-white rounded-lg border border-[var(--border-default)] p-6 mb-6">
        <h2 className="text-2xl font-bold text-[var(--text-primary)] mb-2">{docs.name}</h2>
        <p className="text-[var(--text-secondary)] mb-4">{docs.description}</p>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-xs text-[var(--text-muted)] mb-1">gRPC Port</div>
            <div className="font-mono font-bold text-[var(--text-primary)]">{docs.grpcPort}</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-xs text-[var(--text-muted)] mb-1">HTTP Port</div>
            <div className="font-mono font-bold text-[var(--text-primary)]">{docs.httpPort}</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-xs text-[var(--text-muted)] mb-1">Package</div>
            <div className="font-mono text-sm text-[var(--text-primary)]">{docs.package}</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-xs text-[var(--text-muted)] mb-1">Service</div>
            <div className="font-mono text-sm text-[var(--text-primary)]">{docs.service}</div>
          </div>
        </div>
      </div>

      {/* gRPC Endpoints */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
          <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-mono">gRPC</span>
          Endpoints
        </h3>
        {docs.endpoints.map((endpoint, index) => (
          <EndpointCard key={index} endpoint={endpoint} />
        ))}
      </div>

      {/* REST Endpoints */}
      {docs.restEndpoints && docs.restEndpoints.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
            <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-mono">REST</span>
            Endpoints
          </h3>
          {docs.restEndpoints.map((endpoint, index) => (
            <EndpointCard key={index} endpoint={endpoint} isRest />
          ))}
        </div>
      )}
    </div>
  );
}

export default function DevelopersPage() {
  const [activeAgent, setActiveAgent] = useState<Agent | null>(null);

  const agents: { id: Agent; label: string }[] = [
    { id: 'requirement-analysis', label: 'Requirement Analysis' },
    { id: 'test-cases', label: 'Test Cases' },
    { id: 'test-data', label: 'Test Data' },
    { id: 'ecommerce-domain', label: 'eCommerce Domain' },
  ];

  return (
    <main className="min-h-screen bg-[var(--bg-secondary)]">
      {/* Hero Section */}
      <div className="bg-white border-b border-[var(--border-default)]">
        <div className="max-w-7xl mx-auto px-6 py-12">
          <h1 className="text-3xl font-bold text-[var(--text-primary)] mb-2">
            Developers API Reference
          </h1>
          <p className="text-[var(--text-secondary)]">
            Complete API documentation for all QA Platform agents including gRPC and REST endpoints.
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Quick Links */}
        <div className="bg-white rounded-lg border border-[var(--border-default)] p-6 mb-8">
          <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Quick Navigation</h2>
          <div className="flex flex-wrap gap-3">
            {agents.map((agent) => (
              <a
                key={agent.id}
                href={`#${agent.id}`}
                onClick={() => setActiveAgent(agent.id)}
                className={`px-4 py-2 rounded-lg border transition-colors ${
                  activeAgent === agent.id
                    ? 'bg-red-50 border-red-200 text-red-700'
                    : 'border-[var(--border-default)] hover:bg-gray-50 text-[var(--text-secondary)]'
                }`}
              >
                {agent.label}
              </a>
            ))}
          </div>
        </div>

        {/* Service Overview */}
        <div className="bg-white rounded-lg border border-[var(--border-default)] p-6 mb-8">
          <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Service Overview</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border-default)]">
                  <th className="text-left py-3 px-4 font-semibold text-[var(--text-primary)]">Agent</th>
                  <th className="text-left py-3 px-4 font-semibold text-[var(--text-primary)]">gRPC Port</th>
                  <th className="text-left py-3 px-4 font-semibold text-[var(--text-primary)]">HTTP Port</th>
                  <th className="text-left py-3 px-4 font-semibold text-[var(--text-primary)]">Envoy Proxy</th>
                  <th className="text-left py-3 px-4 font-semibold text-[var(--text-primary)]">Proto Package</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-[var(--border-default)]">
                  <td className="py-3 px-4">Requirement Analysis</td>
                  <td className="py-3 px-4 font-mono">9004</td>
                  <td className="py-3 px-4 font-mono">8084</td>
                  <td className="py-3 px-4 font-mono">8085</td>
                  <td className="py-3 px-4 font-mono text-xs">requirementanalysis.v1</td>
                </tr>
                <tr className="border-b border-[var(--border-default)]">
                  <td className="py-3 px-4">Test Cases</td>
                  <td className="py-3 px-4 font-mono">9003</td>
                  <td className="py-3 px-4 font-mono">8083</td>
                  <td className="py-3 px-4 font-mono">8085</td>
                  <td className="py-3 px-4 font-mono text-xs">testcases.v1</td>
                </tr>
                <tr className="border-b border-[var(--border-default)]">
                  <td className="py-3 px-4">Test Data</td>
                  <td className="py-3 px-4 font-mono">9091</td>
                  <td className="py-3 px-4 font-mono">8091</td>
                  <td className="py-3 px-4 font-mono">8085</td>
                  <td className="py-3 px-4 font-mono text-xs">testdata.v1</td>
                </tr>
                <tr>
                  <td className="py-3 px-4">eCommerce Domain</td>
                  <td className="py-3 px-4 font-mono">9002</td>
                  <td className="py-3 px-4 font-mono">8082</td>
                  <td className="py-3 px-4 font-mono">8085</td>
                  <td className="py-3 px-4 font-mono text-xs">ecommerce.domain.v1</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Connection Examples */}
        <div className="bg-white rounded-lg border border-[var(--border-default)] p-6 mb-8">
          <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Connection Examples</h2>

          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-semibold text-[var(--text-secondary)] mb-2">gRPC-Web (Browser)</h3>
              <CodeBlock
                code={`import { GrpcWebFetchTransport } from '@protobuf-ts/grpcweb-transport';

const transport = new GrpcWebFetchTransport({
  baseUrl: 'http://localhost:8085',  // Envoy proxy
});

const client = new TestCasesServiceClient(transport);
const response = await client.generateTestCases(request);`}
              />
            </div>

            <div>
              <h3 className="text-sm font-semibold text-[var(--text-secondary)] mb-2">Python gRPC</h3>
              <CodeBlock
                code={`import grpc
from test_cases_pb2_grpc import TestCasesServiceStub

channel = grpc.insecure_channel('localhost:9003')
stub = TestCasesServiceStub(channel)
response = stub.GenerateTestCases(request)`}
              />
            </div>

            <div>
              <h3 className="text-sm font-semibold text-[var(--text-secondary)] mb-2">REST API (cURL)</h3>
              <CodeBlock
                code={`# Test Data Agent
curl -X POST http://localhost:8091/generate \\
  -H "Content-Type: application/json" \\
  -d '{"domain": "ecommerce", "entity": "customer", "count": 5}'

# eCommerce Domain Agent
curl -X POST http://localhost:8082/api/generate \\
  -H "Content-Type: application/json" \\
  -d '{"entity": "order", "count": 10, "generation_method": "HYBRID"}'`}
              />
            </div>
          </div>
        </div>

        {/* Agent Documentation */}
        {agents.map((agent) => (
          <AgentSection key={agent.id} agent={agent.id} docs={agentDocs[agent.id]} />
        ))}
      </div>
    </main>
  );
}
