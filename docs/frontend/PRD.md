# Product Requirements Document: QA Platform Frontend UI with gRPC-Web

**Version**: 2.0 (gRPC-Web)
**Date**: December 21, 2025
**Status**: Draft
**Backend Communication**: gRPC-Web via Envoy Proxy

---

## 1. Executive Summary

### 1.1 Product Overview
The QA Platform Frontend UI is a web-based interface that enables QA engineers, developers, and product managers to generate, view, and manage AI-powered test cases. The frontend communicates directly with backend gRPC services through gRPC-Web protocol via an Envoy proxy.

### 1.2 Architecture Decision
**Selected Approach**: **gRPC-Web (Direct Protocol Communication)**

```
Browser
  ↓ grpc-web library (binary protocol)
Envoy Proxy (port 8080)
  ↓ gRPC protocol translation
Test Cases Agent (port 9003)
  ↓ gRPC calls
Anthropic Claude API
```

**Key Benefits**:
- End-to-end type safety with proto-generated TypeScript
- Binary protocol (smaller payloads than JSON)
- Streaming support ready for future enhancements
- Direct mapping from proto definitions to UI
- No manual JSON/proto conversion needed

### 1.3 Success Metrics
- Successfully generate test cases from all 3 input types
- Proto compilation pipeline integrated into build
- Envoy proxy configured and operational
- Form-to-proto conversion working correctly
- Proto responses properly displayed in UI

---

## 2. Target Users

### 2.1 Primary Personas

**QA Engineer** (Primary)
- Generates test cases from user stories
- Values comprehensive test coverage
- Familiar with Gherkin and traditional formats

**Developer** (Secondary)
- Generates test cases from OpenAPI specs
- Prefers structured, type-safe interfaces
- Integrates with CI/CD pipelines

**Product Manager** (Tertiary)
- Reviews test coverage
- Validates requirements
- Focuses on acceptance criteria

---

## 3. Technical Architecture

### 3.1 gRPC-Web Communication Stack

**Client Side** (Browser):
```
React Component
  ↓ Form Data
Custom Hook (useGenerateTestCases)
  ↓ Build Proto Message
gRPC-Web Client (auto-generated from .proto)
  ↓ Binary gRPC-Web Protocol
HTTP/2 or HTTP/1.1
```

**Server Side**:
```
Envoy Proxy (localhost:8080)
  ↓ Protocol Translation (gRPC-Web → gRPC)
Test Cases Agent (localhost:9003)
  ↓ gRPC
LLM Provider (Anthropic)
```

### 3.2 Proto File Contract
Source: `/protos/test_cases.proto`

**Key Services** (Phase 1):
1. `GenerateTestCases` - Primary generation endpoint
2. `GetTestCase` - Fetch individual test case by ID
3. `HealthCheck` - Service status for landing page

**Future Services** (Phase 2):
4. `ListTestCases` - Historical test cases with filtering/search
5. `StoreTestCases` - Persist to vector DB for learning
6. `AnalyzeCoverage` - Coverage gap analysis

**Key Messages**:
- `GenerateTestCasesRequest` (input, config)
- `GenerateTestCasesResponse` (test cases, metadata)
- `TestCase` (id, title, steps, test data)
- `GenerationConfig` (format, coverage, test types)

**Configuration Messages**:
- `DomainConfig` (Phase 2) - Domain enrichment from eCommerce Agent
- `TestDataConfig` (Phase 2) - Test data generation from Test Data Agent

**Enums**:
- `OutputFormat`: TRADITIONAL, GHERKIN, JSON
- `CoverageLevel`: QUICK, STANDARD, EXHAUSTIVE
- `TestType`: 20 types total:
  - **Functional**: FUNCTIONAL, ACCEPTANCE, SMOKE, REGRESSION
  - **Non-Functional**: PERFORMANCE, LOAD, STRESS, RECOVERY
  - **Quality**: SECURITY, USABILITY, ACCESSIBILITY, LOCALIZATION
  - **Technical**: UNIT, INTEGRATION, API, DATABASE
  - **Risk-Based**: NEGATIVE, BOUNDARY, EDGE_CASE
  - **Compatibility**: COMPATIBILITY
- `Priority`: CRITICAL, HIGH, MEDIUM, LOW
- `TestCaseStatus`: DRAFT, READY, IN_PROGRESS, PASSED, FAILED, BLOCKED, SKIPPED
- `TestDataPlacement`: EMBEDDED, SEPARATE, BOTH

---

## 4. Envoy Proxy Setup

### 4.1 Configuration File

**Location**: `/envoy/envoy.yaml`

```yaml
static_resources:
  listeners:
    - name: listener_0
      address:
        socket_address:
          address: 0.0.0.0
          port_value: 8080
      filter_chains:
        - filters:
            - name: envoy.filters.network.http_connection_manager
              typed_config:
                "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
                codec_type: auto
                stat_prefix: ingress_http
                route_config:
                  name: local_route
                  virtual_hosts:
                    - name: local_service
                      domains: ["*"]
                      routes:
                        - match:
                            prefix: "/testcases.v1.TestCasesService"
                          route:
                            cluster: test_cases_service
                            timeout: 0s
                            max_stream_duration:
                              grpc_timeout_header_max: 60s
                      cors:
                        allow_origin_string_match:
                          - prefix: "*"
                        allow_methods: GET, PUT, DELETE, POST, OPTIONS
                        allow_headers: keep-alive,user-agent,cache-control,content-type,content-transfer-encoding,x-user-agent,x-grpc-web,grpc-timeout
                        max_age: "1728000"
                        expose_headers: grpc-status,grpc-message
                http_filters:
                  - name: envoy.filters.http.grpc_web
                    typed_config:
                      "@type": type.googleapis.com/envoy.extensions.filters.http.grpc_web.v3.GrpcWeb
                  - name: envoy.filters.http.cors
                    typed_config:
                      "@type": type.googleapis.com/envoy.extensions.filters.http.cors.v3.Cors
                  - name: envoy.filters.http.router
                    typed_config:
                      "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router
  clusters:
    - name: test_cases_service
      connect_timeout: 0.25s
      type: logical_dns
      http2_protocol_options: {}
      lb_policy: round_robin
      load_assignment:
        cluster_name: test_cases_service
        endpoints:
          - lb_endpoints:
              - endpoint:
                  address:
                    socket_address:
                      address: host.docker.internal  # For Docker
                      # address: localhost           # For local envoy binary
                      port_value: 9003
```

### 4.2 Running Envoy

**Using Docker** (Recommended):
```bash
# Start Envoy proxy
docker run -d \
  --name envoy-proxy \
  -v "$(pwd)/envoy/envoy.yaml:/etc/envoy/envoy.yaml:ro" \
  -p 8080:8080 \
  envoyproxy/envoy:v1.31-latest

# View logs
docker logs -f envoy-proxy

# Stop
docker stop envoy-proxy && docker rm envoy-proxy
```

**Using Binary**:
```bash
# Install envoy (macOS)
brew install envoy

# Run
envoy -c envoy/envoy.yaml
```

### 4.3 Health Check
```bash
# Test Envoy is running
curl http://localhost:8080/stats/prometheus

# Expected: Prometheus metrics
```

---

## 5. Proto Compilation Pipeline

### 5.1 Required Tools

```bash
# Install protoc (protocol buffer compiler)
# macOS
brew install protobuf

# Install grpc-web plugin
npm install -g protoc-gen-grpc-web

# Or download from:
# https://github.com/grpc/grpc-web/releases
```

### 5.2 Code Generation Script

**Location**: `/frontend/scripts/generate-proto.sh`

```bash
#!/bin/bash

set -e

PROTO_DIR="../protos"
OUT_DIR="./lib/grpc/generated"

echo "Generating TypeScript code from proto files..."

# Create output directory
mkdir -p $OUT_DIR

# Generate JavaScript/TypeScript code
protoc \
  -I=$PROTO_DIR \
  test_cases.proto \
  --js_out=import_style=commonjs,binary:$OUT_DIR \
  --grpc-web_out=import_style=typescript,mode=grpcwebtext:$OUT_DIR

echo "✓ Proto files generated successfully!"
echo "  Output: $OUT_DIR/"
ls -lh $OUT_DIR/
```

**Make executable**:
```bash
chmod +x scripts/generate-proto.sh
```

### 5.3 Generated Files

After running `./scripts/generate-proto.sh`:

```
lib/grpc/generated/
├── test_cases_pb.js              # Message classes (JS)
├── test_cases_pb.d.ts            # Message types (TS declarations)
├── test_cases_grpc_web_pb.js     # Service client (JS)
└── test_cases_grpc_web_pb.d.ts   # Service client types (TS)
```

### 5.4 Package.json Integration

```json
{
  "scripts": {
    "proto:gen": "bash ./scripts/generate-proto.sh",
    "proto:watch": "nodemon --watch ../protos --exec npm run proto:gen",
    "postinstall": "npm run proto:gen",
    "dev": "npm run proto:gen && next dev",
    "build": "npm run proto:gen && next build"
  },
  "devDependencies": {
    "nodemon": "^3.0.2"
  }
}
```

---

## 6. Frontend Implementation

### 6.1 Dependencies

**Install gRPC-Web**:
```bash
npm install grpc-web
npm install --save-dev @types/google-protobuf
```

**Full package.json dependencies**:
```json
{
  "dependencies": {
    "next": "14.2.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "grpc-web": "^1.5.0",
    "tailwindcss": "^3.4.0",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-select": "^2.0.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/node": "^20.10.0",
    "@types/react": "^18.3.0",
    "@types/google-protobuf": "^3.15.12",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32"
  }
}
```

### 6.2 gRPC-Web Client Service

**Location**: `/frontend/lib/grpc/testCasesClient.ts`

```typescript
import { TestCasesServiceClient } from './generated/test_cases_grpc_web_pb';

// Client points to Envoy proxy
const GRPC_WEB_URL = process.env.NEXT_PUBLIC_GRPC_WEB_URL || 'http://localhost:8080';

// Create singleton client instance
export const testCasesClient = new TestCasesServiceClient(
  GRPC_WEB_URL,
  null,  // credentials (null for insecure)
  null   // options
);

export default testCasesClient;
```

**Environment variables**:
```bash
# .env.local
NEXT_PUBLIC_GRPC_WEB_URL=http://localhost:8080

# Production
# NEXT_PUBLIC_GRPC_WEB_URL=https://grpc.example.com
```

### 6.3 React Hook: useGenerateTestCases

**Location**: `/frontend/hooks/useGenerateTestCases.ts`

```typescript
import { useState } from 'react';
import testCasesClient from '@/lib/grpc/testCasesClient';
import {
  GenerateTestCasesRequest,
  UserStoryInput,
  ApiSpecInput,
  FreeFormInput,
  GenerationConfig,
  OutputFormat,
  CoverageLevel,
  TestType
} from '@/lib/grpc/generated/test_cases_pb';

export interface GenerateFormData {
  inputType: 'user_story' | 'api_spec' | 'free_form';
  // User Story fields
  story?: string;
  acceptanceCriteria?: string[];
  additionalContext?: string;
  // API Spec fields
  apiSpec?: string;
  specFormat?: 'openapi' | 'graphql';
  endpoints?: string[];
  // Free Form fields
  freeFormText?: string;
  freeFormContext?: Record<string, string>;
  // Generation config
  outputFormat: 'TRADITIONAL' | 'GHERKIN' | 'JSON';
  coverageLevel: 'QUICK' | 'STANDARD' | 'EXHAUSTIVE';
  testTypes: string[];
  maxTestCases?: number;
  priorityFocus?: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  detailLevel?: 'low' | 'medium' | 'high';
}

export function useGenerateTestCases() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [testCases, setTestCases] = useState<any[]>([]);
  const [metadata, setMetadata] = useState<any>(null);

  const generateTestCases = async (formData: GenerateFormData) => {
    setLoading(true);
    setError(null);
    setTestCases([]);
    setMetadata(null);

    try {
      // Build proto request
      const request = new GenerateTestCasesRequest();
      request.setRequestId(`req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);

      // Set input based on type
      if (formData.inputType === 'user_story') {
        const userStory = new UserStoryInput();
        userStory.setStory(formData.story || '');
        userStory.setAcceptanceCriteriaList(formData.acceptanceCriteria || []);
        if (formData.additionalContext) {
          userStory.setAdditionalContext(formData.additionalContext);
        }
        request.setUserStory(userStory);
      } else if (formData.inputType === 'api_spec') {
        const apiSpec = new ApiSpecInput();
        apiSpec.setSpec(formData.apiSpec || '');
        apiSpec.setSpecFormat(formData.specFormat || 'openapi');
        if (formData.endpoints && formData.endpoints.length > 0) {
          apiSpec.setEndpointsList(formData.endpoints);
        }
        request.setApiSpec(apiSpec);
      } else if (formData.inputType === 'free_form') {
        const freeForm = new FreeFormInput();
        freeForm.setRequirement(formData.freeFormText || '');
        if (formData.freeFormContext) {
          const contextMap = freeForm.getContextMap();
          Object.entries(formData.freeFormContext).forEach(([key, value]) => {
            contextMap.set(key, value);
          });
        }
        request.setFreeForm(freeForm);
      }

      // Set generation config
      const config = new GenerationConfig();

      // Output format
      const formatEnum = OutputFormat[formData.outputFormat as keyof typeof OutputFormat];
      config.setOutputFormat(formatEnum);

      // Coverage level
      const coverageEnum = CoverageLevel[formData.coverageLevel as keyof typeof CoverageLevel];
      config.setCoverageLevel(coverageEnum);

      // Test types
      const testTypeEnums = formData.testTypes.map(
        t => TestType[t as keyof typeof TestType]
      );
      config.setTestTypesList(testTypeEnums);

      // Optional fields
      if (formData.maxTestCases) {
        config.setMaxTestCases(formData.maxTestCases);
      }
      if (formData.priorityFocus) {
        // Note: priorityFocus is string (not enum) in proto for flexibility
        config.setPriorityFocus(formData.priorityFocus.toLowerCase());
      }
      if (formData.detailLevel) {
        config.setDetailLevel(formData.detailLevel);
      }

      request.setGenerationConfig(config);

      // Call gRPC-Web service
      const response = await new Promise<any>((resolve, reject) => {
        testCasesClient.generateTestCases(request, {}, (err, response) => {
          if (err) {
            reject(err);
          } else {
            resolve(response);
          }
        });
      });

      // Convert proto response to plain objects
      const testCasesList = response.getTestCasesList();
      const testCasesData = testCasesList.map((tc: any) => tc.toObject());

      setTestCases(testCasesData);

      if (response.hasMetadata()) {
        setMetadata(response.getMetadata().toObject());
      }

    } catch (err: any) {
      console.error('gRPC-Web Error:', err);

      // Handle gRPC error codes
      let errorMessage = 'Failed to generate test cases';

      switch (err.code) {
        case 0:
          return; // OK - no error
        case 1:
          errorMessage = 'Request cancelled. Please try again.';
          break;
        case 2:
          errorMessage = 'Unknown error occurred. Please check logs.';
          break;
        case 3:
          errorMessage = 'Invalid input. Please check your form data.';
          break;
        case 4:
          errorMessage = 'Request timed out. Test case generation may take up to 60 seconds.';
          break;
        case 5:
          errorMessage = 'Test case not found.';
          break;
        case 7:
          errorMessage = 'Permission denied. Check authentication.';
          break;
        case 8:
          errorMessage = 'Rate limit exceeded. Please wait and try again.';
          break;
        case 9:
          errorMessage = 'Prerequisites not met. Check your configuration.';
          break;
        case 12:
          errorMessage = 'Feature not implemented yet.';
          break;
        case 13:
          errorMessage = 'Internal server error. Please contact support.';
          break;
        case 14:
          errorMessage = 'Service unavailable. Please ensure Test Cases Agent and Envoy proxy are running.';
          break;
        case 16:
          errorMessage = 'Authentication required.';
          break;
        default:
          errorMessage = err.message || 'Unknown error occurred';
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return {
    generateTestCases,
    loading,
    error,
    testCases,
    metadata
  };
}
```

### 6.4 Component Usage Example

**Location**: `/frontend/components/test-cases/GenerationForm.tsx`

```typescript
'use client';

import { useState } from 'react';
import { useGenerateTestCases } from '@/hooks/useGenerateTestCases';
import type { GenerateFormData } from '@/hooks/useGenerateTestCases';

export function GenerationForm() {
  const { generateTestCases, loading, error, testCases, metadata } = useGenerateTestCases();

  const [formData, setFormData] = useState<GenerateFormData>({
    inputType: 'user_story',
    story: '',
    acceptanceCriteria: [''],
    outputFormat: 'TRADITIONAL',
    coverageLevel: 'STANDARD',
    testTypes: ['FUNCTIONAL', 'NEGATIVE'],
    maxTestCases: 10
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await generateTestCases(formData);
  };

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Input Type Tabs */}
        <div>
          <label>Input Type</label>
          <select
            value={formData.inputType}
            onChange={(e) => setFormData({
              ...formData,
              inputType: e.target.value as any
            })}
          >
            <option value="user_story">User Story</option>
            <option value="api_spec">API Specification</option>
            <option value="free_form">Free Form</option>
          </select>
        </div>

        {/* User Story Fields */}
        {formData.inputType === 'user_story' && (
          <div>
            <label>Story</label>
            <textarea
              value={formData.story}
              onChange={(e) => setFormData({ ...formData, story: e.target.value })}
              placeholder="As a customer, I want to..."
              required
            />
          </div>
        )}

        {/* Config Fields */}
        <div>
          <label>Output Format</label>
          <select
            value={formData.outputFormat}
            onChange={(e) => setFormData({
              ...formData,
              outputFormat: e.target.value as any
            })}
          >
            <option value="TRADITIONAL">Traditional</option>
            <option value="GHERKIN">Gherkin</option>
            <option value="JSON">JSON</option>
          </select>
        </div>

        {/* Coverage Level */}
        <div>
          <label>Coverage Level</label>
          <select
            value={formData.coverageLevel}
            onChange={(e) => setFormData({
              ...formData,
              coverageLevel: e.target.value as any
            })}
          >
            <option value="QUICK">Quick (Happy path + critical negatives)</option>
            <option value="STANDARD">Standard (Comprehensive functional + negative)</option>
            <option value="EXHAUSTIVE">Exhaustive (All scenarios including edge cases)</option>
          </select>
        </div>

        {/* Test Types (Multi-select) */}
        <div>
          <label>Test Types</label>
          <div className="grid grid-cols-2 gap-2">
            {/* Functional Tests */}
            <label className="flex items-center gap-2">
              <input type="checkbox" value="FUNCTIONAL" />
              <span>Functional</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" value="ACCEPTANCE" />
              <span>Acceptance</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" value="SMOKE" />
              <span>Smoke</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" value="REGRESSION" />
              <span>Regression</span>
            </label>

            {/* Risk-Based Tests */}
            <label className="flex items-center gap-2">
              <input type="checkbox" value="NEGATIVE" />
              <span>Negative</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" value="BOUNDARY" />
              <span>Boundary</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" value="EDGE_CASE" />
              <span>Edge Case</span>
            </label>

            {/* Technical Tests */}
            <label className="flex items-center gap-2">
              <input type="checkbox" value="UNIT" />
              <span>Unit</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" value="INTEGRATION" />
              <span>Integration</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" value="API" />
              <span>API</span>
            </label>

            {/* Quality Tests */}
            <label className="flex items-center gap-2">
              <input type="checkbox" value="SECURITY" />
              <span>Security</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" value="USABILITY" />
              <span>Usability</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" value="ACCESSIBILITY" />
              <span>Accessibility</span>
            </label>

            {/* Performance Tests */}
            <label className="flex items-center gap-2">
              <input type="checkbox" value="PERFORMANCE" />
              <span>Performance</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" value="LOAD" />
              <span>Load</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" value="STRESS" />
              <span>Stress</span>
            </label>
          </div>
          <p className="text-sm text-text-muted mt-2">
            See proto for full list of 20 test types
          </p>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="bg-[#CE0037] text-white px-6 py-2 rounded"
        >
          {loading ? 'Generating...' : 'Generate Test Cases'}
        </button>
      </form>

      {/* Error Display */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Results Display */}
      {testCases.length > 0 && (
        <div>
          <h3>Generated {testCases.length} Test Cases</h3>
          {testCases.map((tc, idx) => (
            <div key={idx} className="border p-4 rounded mb-2">
              <h4>{tc.title}</h4>
              <p>Type: {tc.type}</p>
              <p>Priority: {tc.priority}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## 7. Deployment Configuration

### 7.1 Docker Compose (Full Stack)

**Location**: `/docker-compose.yml`

```yaml
version: '3.8'

services:
  # Test Cases Agent (gRPC backend)
  test-cases-agent:
    build: ./agents/test-cases-agent
    ports:
      - "9003:9003"      # gRPC port
      - "8083:8083"      # HTTP health check
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GRPC_PORT=9003
      - HTTP_PORT=8083
    networks:
      - qa-platform

  # Envoy Proxy (gRPC-Web gateway)
  envoy:
    image: envoyproxy/envoy:v1.31-latest
    ports:
      - "8080:8080"      # gRPC-Web port
      - "9901:9901"      # Envoy admin
    volumes:
      - ./envoy/envoy.yaml:/etc/envoy/envoy.yaml:ro
    depends_on:
      - test-cases-agent
    networks:
      - qa-platform

  # Frontend (Next.js)
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_GRPC_WEB_URL=http://localhost:8080
    depends_on:
      - envoy
    networks:
      - qa-platform

networks:
  qa-platform:
    driver: bridge
```

### 7.2 Start/Stop Scripts

**start-all.sh**:
```bash
#!/bin/bash

echo "Starting QA Platform services..."

# Start test-cases-agent
echo "→ Starting Test Cases Agent (gRPC)"
cd agents/test-cases-agent && python -m test_cases_agent.main &
AGENT_PID=$!
echo "  PID: $AGENT_PID"

sleep 3

# Start Envoy proxy
echo "→ Starting Envoy Proxy (gRPC-Web)"
docker run -d \
  --name envoy-proxy \
  -v "$(pwd)/envoy/envoy.yaml:/etc/envoy/envoy.yaml:ro" \
  -p 8080:8080 \
  envoyproxy/envoy:v1.31-latest

sleep 2

# Start Frontend
echo "→ Starting Frontend (Next.js)"
cd frontend && npm run dev &
FRONTEND_PID=$!
echo "  PID: $FRONTEND_PID"

echo ""
echo "✓ All services started!"
echo "  Test Cases Agent: localhost:9003 (gRPC)"
echo "  Envoy Proxy:      localhost:8080 (gRPC-Web)"
echo "  Frontend:         localhost:3000 (HTTP)"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "echo 'Stopping services...'; kill $AGENT_PID $FRONTEND_PID; docker stop envoy-proxy; docker rm envoy-proxy; exit" INT
wait
```

---

## 8. Testing & Debugging

### 8.1 Testing gRPC-Web Connection

**Test with grpcurl** (requires `grpc-reflection`):
```bash
# Test direct gRPC (port 9003)
grpcurl -plaintext localhost:9003 testcases.v1.TestCasesService/HealthCheck

# Test via Envoy (port 8080) - requires gRPC-Web client
# Use browser DevTools Network tab instead
```

**Test with Browser DevTools**:
1. Open browser DevTools → Network tab
2. Generate test cases via UI
3. Look for requests to `localhost:8080`
4. Check request/response headers for `grpc-status`, `grpc-message`

### 8.2 Common Errors & Solutions

**Error**: "Failed to fetch" or CORS error
- **Solution**: Check Envoy CORS configuration
- Verify `allow_origin_string_match` includes frontend origin

**Error**: "Code 14: UNAVAILABLE"
- **Solution**: Test Cases Agent not running
- Start agent: `cd agents/test-cases-agent && python -m test_cases_agent.main`

**Error**: "Code 4: DEADLINE_EXCEEDED"
- **Solution**: Request timeout
- Increase timeout in Envoy config: `grpc_timeout_header_max: 120s`

**Error**: Proto compilation fails
- **Solution**: Check protoc installation
- Verify proto file syntax: `protoc --decode_raw < test_cases.proto`

---

## 9. Project Structure

```
qa-platform/
├── frontend/                       # Next.js frontend
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                # Landing page
│   │   ├── test-cases/
│   │   │   └── page.tsx            # Test cases agent page
│   │   └── globals.css
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   └── Footer.tsx
│   │   └── test-cases/
│   │       ├── GenerationForm.tsx
│   │       ├── UserStoryTab.tsx
│   │       ├── TestCaseCard.tsx
│   │       └── TestCaseDetail.tsx
│   ├── hooks/
│   │   └── useGenerateTestCases.ts
│   ├── lib/
│   │   └── grpc/
│   │       ├── testCasesClient.ts
│   │       └── generated/           # Auto-generated from proto
│   │           ├── test_cases_pb.js
│   │           ├── test_cases_pb.d.ts
│   │           ├── test_cases_grpc_web_pb.js
│   │           └── test_cases_grpc_web_pb.d.ts
│   ├── scripts/
│   │   └── generate-proto.sh
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   └── tsconfig.json
├── envoy/
│   └── envoy.yaml                  # Envoy proxy config
├── protos/
│   └── test_cases.proto            # gRPC service definition
├── agents/
│   └── test-cases-agent/           # Python gRPC service
├── docs/
│   └── frontend/
│       ├── PRD.md                  # This document
│       ├── FRONTEND_REQUIREMENTS.md
│       └── styles.md
├── docker-compose.yml
├── start-all.sh
└── stop-all.sh
```

---

## 10. User Interface Pages

### 10.1 Landing Page (`/`)

**Purpose**: Platform overview and navigation hub for all agents

**Design Reference**: `/docs/frontend/styles.md` (Macy's brand theme)

**Layout**:
```tsx
<main className="max-w-7xl mx-auto px-6 py-8">
  {/* Hero Section */}
  <section className="mb-12">
    <h1 className="text-4xl font-bold text-text-primary mb-4">
      QA Platform
    </h1>
    <p className="text-lg text-text-muted">
      AI-powered test generation platform for comprehensive QA coverage
    </p>
  </section>

  {/* Agent Cards Grid */}
  <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {agents.map(agent => <AgentCard {...agent} />)}
  </section>

  {/* Quick Stats (real backend data) */}
  <section className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
    <StatCard title="Test Cases Generated" value={stats.testCasesGenerated} />
    <StatCard title="Agents Active" value={stats.agentsActive} />
    <StatCard title="Coverage Score" value={stats.averageCoverage} />
  </section>
</main>
```

**Agent Cards**:
```typescript
const agents = [
  {
    name: 'Test Cases Agent',
    description: 'Generate comprehensive test cases from requirements',
    status: 'operational',  // From HealthCheck API
    icon: '/icons/test-cases.svg',
    link: '/test-cases',
    features: ['User Stories', 'API Specs', 'Free Form Input']
  },
  {
    name: 'Test Data Agent',
    description: 'Generate realistic test data using AI',
    status: 'operational',
    icon: '/icons/test-data.svg',
    link: 'http://localhost:3001',  // External link to existing UI
    external: true,
    features: ['Schema-based', 'AI Generated', 'Realistic Data']
  },
  {
    name: 'eCommerce Domain Agent',
    description: 'Domain-specific context and business rules',
    status: 'coming_soon',  // Phase 2
    icon: '/icons/ecommerce.svg',
    link: '#',
    features: ['Business Rules', 'Edge Cases', 'Domain Context']
  }
];
```

**Agent Status Display**:
- Use `HealthCheck` gRPC endpoint for each agent
- Display status badge: Operational (green), Down (red), Coming Soon (gray)
- Show last health check timestamp

**Stats Dashboard**:
- Fetch real stats from backend (Phase 2: ListTestCases API)
- Display:
  - Total test cases generated (all time)
  - Active agents count
  - Average coverage score

### 10.2 Test Cases Agent Page (`/test-cases`)

**Layout Structure**:
```tsx
<div className="max-w-7xl mx-auto px-6 py-8">
  {/* Page Header */}
  <PageHeader
    title="Test Cases Agent"
    status={agentStatus}  // From HealthCheck
    description="Generate comprehensive test cases from requirements"
  />

  {/* Generation Form */}
  <section className="mb-8">
    <GenerationForm />
  </section>

  {/* Results Section */}
  {testCases.length > 0 && (
    <section>
      <ResultsHeader metadata={metadata} />
      <TestCaseList testCases={testCases} />
    </section>
  )}
</div>
```

**Components**:
1. `GenerationForm` - All 3 input types + configuration
2. `ResultsHeader` - Shows metadata (see Metadata Display below)
3. `TestCaseList` - Cards with filtering/sorting
4. `TestCaseDetail` - Modal or panel with full test case

**Metadata Display** (GenerationMetadata from proto):
```tsx
<div className="bg-bg-secondary rounded-lg p-6 mb-6">
  <h3 className="text-lg font-semibold mb-4">Generation Summary</h3>
  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
    {/* LLM Info */}
    <div>
      <p className="text-sm text-text-muted">Model</p>
      <p className="font-medium">{metadata.llmProvider} / {metadata.llmModel}</p>
    </div>

    {/* Tokens */}
    <div>
      <p className="text-sm text-text-muted">Tokens Used</p>
      <p className="font-medium">{metadata.llmTokensUsed.toLocaleString()}</p>
    </div>

    {/* Time */}
    <div>
      <p className="text-sm text-text-muted">Generation Time</p>
      <p className="font-medium">{(metadata.generationTimeMs / 1000).toFixed(2)}s</p>
    </div>

    {/* Count */}
    <div>
      <p className="text-sm text-text-muted">Test Cases</p>
      <p className="font-medium">{metadata.testCasesGenerated}</p>
    </div>
  </div>

  {/* Coverage Breakdown (if available) */}
  {metadata.coverage && (
    <div className="mt-4">
      <p className="text-sm font-medium mb-2">Coverage Analysis:</p>
      <div className="flex gap-4 text-sm">
        <span>Functional: {metadata.coverage.functionalCount}</span>
        <span>Negative: {metadata.coverage.negativeCount}</span>
        <span>Boundary: {metadata.coverage.boundaryCount}</span>
        <span>Edge Cases: {metadata.coverage.edgeCaseCount}</span>
      </div>
      {metadata.coverage.uncoveredAreas?.length > 0 && (
        <p className="text-sm text-yellow-600 mt-2">
          Gaps: {metadata.coverage.uncoveredAreas.join(', ')}
        </p>
      )}
    </div>
  )}

  {/* Domain Context (Phase 2) */}
  {metadata.domainContextUsed && (
    <p className="text-sm text-text-muted mt-2">
      Domain: {metadata.domainContextUsed}
    </p>
  )}

  {/* Duplicates */}
  {metadata.duplicatesFound > 0 && (
    <p className="text-sm text-yellow-600 mt-2">
      ⚠ {metadata.duplicatesFound} duplicate(s) detected and removed
    </p>
  )}
</div>
```

---

## 11. Development Roadmap

### Phase 1.1: Setup (Week 1)
- [ ] Initialize Next.js project
- [ ] Install gRPC-Web dependencies
- [ ] Set up proto compilation pipeline
- [ ] Configure Envoy proxy
- [ ] Create project structure
- [ ] Build layout components (Header, Footer)
- [ ] Build landing page

### Phase 1.2: Generation Form (Week 2)
- [ ] Create gRPC-Web client service
- [ ] Implement useGenerateTestCases hook
- [ ] Build all 3 input tabs (User Story, API Spec, Free Form)
- [ ] Build configuration panel
- [ ] Wire up proto message building
- [ ] Test end-to-end generation flow

### Phase 1.3: Results Display (Week 2-3)
- [ ] Build test case card list view
- [ ] Implement proto response parsing
- [ ] Add filtering/sorting
- [ ] Display generation metadata
- [ ] Handle loading and error states

### Phase 1.4: Detail View (Week 3)
- [ ] Build test case detail panel
- [ ] Display all test case sections
- [ ] Format Gherkin vs Traditional display
- [ ] Add navigation between test cases

### Phase 1.5: Polish & Testing (Week 4)
- [ ] Error handling improvements
- [ ] Responsive design
- [ ] Accessibility improvements
- [ ] Cross-browser testing
- [ ] Performance optimization
- [ ] Documentation

---

## 11. Success Criteria

### Technical Requirements
✅ Proto compilation integrated into build process
✅ Envoy proxy running and configured
✅ gRPC-Web client successfully calling backend
✅ All proto message types properly generated
✅ Form data correctly converted to proto messages
✅ Proto responses correctly parsed and displayed

### Functional Requirements
✅ All 3 input types working (User Story, API Spec, Free Form)
✅ All configuration options functional
✅ Test cases generated and displayed
✅ Detail view shows complete test case
✅ Error handling for network/service failures
✅ Loading states during generation

### Non-Functional Requirements
✅ Type-safe proto-to-TS conversion
✅ No manual JSON/proto serialization
✅ Responsive on mobile/tablet/desktop
✅ WCAG AA accessibility
✅ Macy's brand theme applied

---

## 12. Appendix

### 12.1 Environment Variables

```bash
# Frontend (.env.local)
NEXT_PUBLIC_GRPC_WEB_URL=http://localhost:8080

# Test Cases Agent
ANTHROPIC_API_KEY=sk-ant-...
GRPC_PORT=9003
HTTP_PORT=8083
```

### 12.2 Proto Reference

**Service**: `testcases.v1.TestCasesService`

**Methods**:
- `GenerateTestCases(GenerateTestCasesRequest) returns (GenerateTestCasesResponse)`
- `GetTestCase(GetTestCaseRequest) returns (GetTestCaseResponse)`
- `HealthCheck(HealthCheckRequest) returns (HealthCheckResponse)`

**Full proto**: `/protos/test_cases.proto`

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.0 | 2025-12-21 | Claude (AI) | Complete rewrite for gRPC-Web architecture |

**Approval Required From**:
- [ ] Product Owner
- [ ] Tech Lead
- [ ] DevOps Lead (for Envoy setup)

**Next Steps**:
1. Approve gRPC-Web architecture
2. Set up Envoy proxy in local environment
3. Test proto compilation pipeline
4. Begin Phase 1.1 implementation
