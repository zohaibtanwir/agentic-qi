# Frontend-Backend Integration Guide

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Next.js UI    │────▶│   Envoy Proxy   │────▶│ Test Cases Agent│
│  (Port 3000)    │     │   (Port 8080)   │     │   (Port 9003)   │
│                 │     │                 │     │                 │
│  gRPC-Web       │     │  Protocol       │     │  gRPC Server    │
│  (HTTP/1.1)     │     │  Translation    │     │  (HTTP/2)       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Communication Stack

### Frontend (Browser)
- **Framework**: Next.js 14 with React 18
- **Protocol**: gRPC-Web over HTTP/1.1
- **Client**: Custom client with mock support (`lib/grpc/testCasesClient.ts`)
- **Types**: Generated from proto files using ts-proto

### Envoy Proxy (Gateway)
- **Purpose**: Translates gRPC-Web (HTTP/1.1) to native gRPC (HTTP/2)
- **Port**: 8080
- **Features**: CORS handling, request routing, timeout management

### Backend (Test Cases Agent)
- **Framework**: Python with grpcio
- **Protocol**: Native gRPC over HTTP/2
- **Port**: 9003

## Proto Service Definition

**File**: `/protos/test_cases.proto`

```protobuf
service TestCasesService {
  rpc GenerateTestCases(GenerateTestCasesRequest) returns (GenerateTestCasesResponse);
  rpc GetTestCase(GetTestCaseRequest) returns (GetTestCaseResponse);
  rpc HealthCheck(HealthCheckRequest) returns (HealthCheckResponse);
}
```

## Frontend Implementation

### 1. Proto Types Generation

Types are generated using ts-proto:

```bash
cd frontend
npm run proto:gen
```

This creates `lib/grpc/generated/test_cases.ts` with:
- TypeScript interfaces for all proto messages
- Enum definitions (OutputFormat, CoverageLevel, TestType, etc.)
- Service client stubs

### 2. gRPC Client (`lib/grpc/testCasesClient.ts`)

```typescript
import { TestType, Priority, OutputFormat, TestCaseStatus } from './generated/test_cases';

export const testCasesClient = {
  async generateTestCases(request: GenerateTestCasesRequest): Promise<GenerateTestCasesResponse> {
    // Mock mode for development (default)
    if (USE_MOCK) {
      return generateMockResponse(request);
    }

    // Real gRPC-Web call via Envoy
    const response = await fetch(`${GRPC_WEB_URL}/testcases.v1.TestCasesService/GenerateTestCases`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/grpc-web+proto',
        'X-Grpc-Web': '1',
      },
      body: encodeRequest(request),
    });
    return decodeResponse(response);
  },
};
```

### 3. React Hook (`hooks/useGenerateTestCases.ts`)

```typescript
export function useGenerateTestCases() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [testCases, setTestCases] = useState<TestCase[]>([]);

  const generateTestCases = async (formData: GenerateFormData) => {
    setLoading(true);
    try {
      const response = await testCasesClient.generateTestCases(buildRequest(formData));
      setTestCases(response.testCases);
    } catch (err) {
      setError(parseGrpcError(err));
    } finally {
      setLoading(false);
    }
  };

  return { generateTestCases, loading, error, testCases };
}
```

## Environment Configuration

### Frontend (.env.local)

```bash
# gRPC-Web endpoint (Envoy proxy)
NEXT_PUBLIC_GRPC_WEB_URL=http://localhost:8080

# Enable mock mode for development without backend
NEXT_PUBLIC_USE_MOCK=true
```

### Backend (.env)

```bash
# gRPC server port
GRPC_PORT=9003

# LLM Provider
ANTHROPIC_API_KEY=sk-ant-...
```

## Running the Stack

### Development Mode (Mock)

```bash
cd frontend
npm run dev
# Frontend at http://localhost:3000 with mock data
```

### Full Stack (with Backend)

```bash
# Terminal 1: Start Test Cases Agent
cd agents/test-cases-agent
python -m test_cases_agent.main

# Terminal 2: Start Envoy Proxy
docker run -d \
  --name envoy-proxy \
  -v "$(pwd)/envoy/envoy.yaml:/etc/envoy/envoy.yaml:ro" \
  -p 8080:8080 \
  envoyproxy/envoy:v1.31-latest

# Terminal 3: Start Frontend
cd frontend
NEXT_PUBLIC_USE_MOCK=false npm run dev
```

## Error Handling

### gRPC Error Codes

| Code | Name | Frontend Message |
|------|------|-----------------|
| 0 | OK | (success) |
| 3 | INVALID_ARGUMENT | Invalid input. Please check your form data. |
| 4 | DEADLINE_EXCEEDED | Request timed out. |
| 14 | UNAVAILABLE | Service unavailable. Check if backend is running. |
| 16 | UNAUTHENTICATED | Authentication required. |

### Error Display

```typescript
{error && (
  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
    <h4>Generation Failed</h4>
    <p>{error}</p>
  </div>
)}
```

## Data Flow

### Request Flow

1. User fills form in GenerationForm component
2. Form data converted to GenerateFormData interface
3. useGenerateTestCases hook builds proto request
4. Client sends to Envoy proxy (port 8080)
5. Envoy translates and forwards to backend (port 9003)
6. Backend generates test cases with Anthropic Claude
7. Response flows back through same path

### Response Processing

```typescript
// Proto response structure
interface GenerateTestCasesResponse {
  requestId: string;
  success: boolean;
  testCases: TestCase[];
  metadata: GenerationMetadata;
  errorMessage: string;
}

// Display in UI
{testCases.map(tc => (
  <TestCaseCard key={tc.id} testCase={tc} />
))}
```

## Debugging

### Browser DevTools

1. Open Network tab
2. Filter by `localhost:8080`
3. Check request/response headers for `grpc-status`

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| CORS error | Envoy not configured | Check envoy.yaml CORS settings |
| Connection refused | Backend not running | Start test-cases-agent |
| Timeout | Slow LLM response | Increase timeout in Envoy config |

## Testing Integration

### Unit Tests (Mock)

```typescript
jest.mock('@/lib/grpc/testCasesClient', () => ({
  testCasesClient: {
    generateTestCases: jest.fn().mockResolvedValue({
      success: true,
      testCases: [mockTestCase],
    }),
  },
}));
```

### Integration Tests

```bash
# Start backend and Envoy first
cd frontend
NEXT_PUBLIC_USE_MOCK=false npm test
```
