import { BinaryReader, BinaryWriter } from "@bufbuild/protobuf/wire";
import {
  TestType,
  Priority,
  OutputFormat,
  TestCaseStatus,
  GenerateTestCasesRequest as GenerateTestCasesRequestMsg,
  GenerateTestCasesResponse as GenerateTestCasesResponseMsg,
  HealthCheckRequest as HealthCheckRequestMsg,
  HealthCheckResponse as HealthCheckResponseMsg,
  ListHistoryRequest as ListHistoryRequestMsg,
  ListHistoryResponse as ListHistoryResponseMsg,
  GetHistorySessionRequest as GetHistorySessionRequestMsg,
  GetHistorySessionResponse as GetHistorySessionResponseMsg,
  DeleteHistorySessionRequest as DeleteHistorySessionRequestMsg,
  DeleteHistorySessionResponse as DeleteHistorySessionResponseMsg,
  type GenerateTestCasesRequest,
  type GenerateTestCasesResponse,
  type HealthCheckResponse,
  type TestCase,
  type ListHistoryRequest,
  type ListHistoryResponse,
  type GetHistorySessionRequest,
  type GetHistorySessionResponse,
  type DeleteHistorySessionRequest,
  type DeleteHistorySessionResponse,
  type HistorySessionSummary,
  type HistorySession,
} from './generated/test_cases';

const GRPC_WEB_URL = process.env.NEXT_PUBLIC_GRPC_WEB_URL || 'http://localhost:8085';
// Default to real backend; only use mock if explicitly set to 'true'
// Use a function to check at runtime so tests can set the env variable after import
function isMockMode(): boolean {
  return process.env.NEXT_PUBLIC_USE_MOCK === 'true';
}

/**
 * Encode a protobuf message with gRPC-Web framing
 * Frame format: 1 byte compression flag + 4 bytes length (big-endian) + message bytes
 */
function encodeGrpcWebRequest(messageBytes: Uint8Array): Uint8Array {
  const frame = new Uint8Array(5 + messageBytes.length);
  // Compression flag (0 = no compression)
  frame[0] = 0;
  // Message length (big-endian)
  const length = messageBytes.length;
  frame[1] = (length >> 24) & 0xff;
  frame[2] = (length >> 16) & 0xff;
  frame[3] = (length >> 8) & 0xff;
  frame[4] = length & 0xff;
  // Message bytes
  frame.set(messageBytes, 5);
  return frame;
}

/**
 * Decode a gRPC-Web response
 * Returns the message bytes and any trailers
 */
function decodeGrpcWebResponse(data: Uint8Array): { messageBytes: Uint8Array; trailers: Map<string, string> } {
  const trailers = new Map<string, string>();
  let messageBytes = new Uint8Array(0);
  let offset = 0;

  while (offset < data.length) {
    if (offset + 5 > data.length) break;

    const compressionFlag = data[offset];
    const length =
      (data[offset + 1] << 24) |
      (data[offset + 2] << 16) |
      (data[offset + 3] << 8) |
      data[offset + 4];

    offset += 5;

    if (offset + length > data.length) break;

    const frameData = data.slice(offset, offset + length);
    offset += length;

    // Check if this is a trailer frame (compression flag has bit 7 set)
    if (compressionFlag & 0x80) {
      // Parse trailers
      const trailerStr = new TextDecoder().decode(frameData);
      trailerStr.split('\r\n').forEach((line) => {
        const colonIdx = line.indexOf(':');
        if (colonIdx > 0) {
          const key = line.slice(0, colonIdx).trim().toLowerCase();
          const value = line.slice(colonIdx + 1).trim();
          trailers.set(key, value);
        }
      });
    } else {
      // This is the message
      messageBytes = frameData;
    }
  }

  return { messageBytes, trailers };
}

/**
 * Make a gRPC-Web unary call
 */
async function grpcWebUnaryCall<TRequest, TResponse>(
  url: string,
  method: string,
  request: TRequest,
  encode: (message: TRequest, writer?: BinaryWriter) => BinaryWriter,
  decode: (input: BinaryReader | Uint8Array, length?: number) => TResponse
): Promise<TResponse> {
  // Encode the request
  const writer = new BinaryWriter();
  encode(request, writer);
  const messageBytes = writer.finish();
  const framedRequest = encodeGrpcWebRequest(messageBytes);

  // Convert to ArrayBuffer for fetch body (ensures type compatibility)
  const bodyBuffer = new ArrayBuffer(framedRequest.length);
  const bodyView = new Uint8Array(bodyBuffer);
  bodyView.set(framedRequest);

  // Make the HTTP request
  const response = await fetch(`${url}/${method}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/grpc-web+proto',
      'X-Grpc-Web': '1',
      'Accept': 'application/grpc-web+proto',
    },
    body: bodyBuffer,
  });

  if (!response.ok) {
    throw new Error(`gRPC HTTP error: ${response.status} ${response.statusText}`);
  }

  // Read the response
  const responseData = new Uint8Array(await response.arrayBuffer());
  const { messageBytes: respBytes, trailers } = decodeGrpcWebResponse(responseData);

  // Check for gRPC status in trailers
  const grpcStatus = trailers.get('grpc-status');
  if (grpcStatus && grpcStatus !== '0') {
    const grpcMessage = trailers.get('grpc-message') || 'Unknown gRPC error';
    throw new Error(`gRPC error (${grpcStatus}): ${decodeURIComponent(grpcMessage)}`);
  }

  // Decode the response
  if (respBytes.length === 0) {
    throw new Error('Empty response from server');
  }

  return decode(respBytes);
}

// Mock data generator for development
function generateMockTestCases(request: GenerateTestCasesRequest): TestCase[] {
  const baseTitle = request.userStory?.story
    ? request.userStory.story.substring(0, 50)
    : request.apiSpec?.spec
      ? 'API Endpoint Test'
      : request.freeForm?.requirement?.substring(0, 50) || 'Test Case';

  const testTypes = request.generationConfig?.testTypes || [TestType.FUNCTIONAL, TestType.NEGATIVE];
  const count = request.generationConfig?.maxTestCases || 5;

  const testCases: TestCase[] = [];

  for (let i = 0; i < count; i++) {
    const testType = testTypes[i % testTypes.length];
    const isGherkin = request.generationConfig?.outputFormat === OutputFormat.GHERKIN;

    testCases.push({
      id: `TC-${String(i + 1).padStart(3, '0')}`,
      title: `${getTestTypeLabel(testType)}: ${baseTitle}`,
      description: `Verify ${getTestTypeDescription(testType)} for the given requirement`,
      type: testType,
      priority: i < 2 ? Priority.HIGH : i < 4 ? Priority.MEDIUM : Priority.LOW,
      tags: [getTestTypeLabel(testType).toLowerCase(), 'generated'],
      requirementId: `REQ-${String(i + 1).padStart(3, '0')}`,
      preconditions: [
        'User is logged into the system',
        'Test environment is properly configured',
      ],
      steps: isGherkin ? [] : [
        {
          order: 1,
          action: 'Navigate to the feature',
          expectedResult: 'Feature page is displayed',
          testData: '',
        },
        {
          order: 2,
          action: 'Perform the main action',
          expectedResult: 'Action completes successfully',
          testData: 'Sample test data',
        },
        {
          order: 3,
          action: 'Verify the outcome',
          expectedResult: 'Expected results are displayed',
          testData: '',
        },
      ],
      gherkin: isGherkin ? `Feature: ${baseTitle}

  Scenario: ${getTestTypeLabel(testType)} test
    Given the user is logged into the system
    And the test environment is configured
    When the user performs the main action
    Then the expected outcome should be displayed
    And the system should be in the correct state` : '',
      testData: {
        items: [
          { field: 'username', value: 'testuser@example.com', description: 'Test user email' },
          { field: 'product_id', value: 'PROD-12345', description: 'Sample product ID' },
        ],
      },
      expectedResult: 'The system behaves as expected according to the requirements',
      postconditions: ['System returns to initial state'],
      status: TestCaseStatus.READY,
    });
  }

  return testCases;
}

function getTestTypeLabel(type: TestType): string {
  const labels: Record<TestType, string> = {
    [TestType.TEST_TYPE_UNSPECIFIED]: 'Unspecified',
    [TestType.FUNCTIONAL]: 'Functional',
    [TestType.NEGATIVE]: 'Negative',
    [TestType.BOUNDARY]: 'Boundary',
    [TestType.EDGE_CASE]: 'Edge Case',
    [TestType.SECURITY]: 'Security',
    [TestType.PERFORMANCE]: 'Performance',
    [TestType.INTEGRATION]: 'Integration',
    [TestType.UNIT]: 'Unit',
    [TestType.USABILITY]: 'Usability',
    [TestType.REGRESSION]: 'Regression',
    [TestType.SMOKE]: 'Smoke',
    [TestType.ACCEPTANCE]: 'Acceptance',
    [TestType.COMPATIBILITY]: 'Compatibility',
    [TestType.ACCESSIBILITY]: 'Accessibility',
    [TestType.LOCALIZATION]: 'Localization',
    [TestType.API]: 'API',
    [TestType.DATABASE]: 'Database',
    [TestType.LOAD]: 'Load',
    [TestType.STRESS]: 'Stress',
    [TestType.RECOVERY]: 'Recovery',
    [TestType.UNRECOGNIZED]: 'Unrecognized',
  };
  return labels[type] || 'Unknown';
}

function getTestTypeDescription(type: TestType): string {
  const descriptions: Record<TestType, string> = {
    [TestType.TEST_TYPE_UNSPECIFIED]: 'general behavior',
    [TestType.FUNCTIONAL]: 'expected behavior and functionality',
    [TestType.NEGATIVE]: 'error handling and invalid input scenarios',
    [TestType.BOUNDARY]: 'boundary conditions and limit values',
    [TestType.EDGE_CASE]: 'unusual and edge case scenarios',
    [TestType.SECURITY]: 'security vulnerabilities and access control',
    [TestType.PERFORMANCE]: 'system performance under various conditions',
    [TestType.INTEGRATION]: 'integration between components',
    [TestType.UNIT]: 'individual unit functionality',
    [TestType.USABILITY]: 'user experience and usability',
    [TestType.REGRESSION]: 'existing functionality after changes',
    [TestType.SMOKE]: 'basic critical functionality',
    [TestType.ACCEPTANCE]: 'business requirements acceptance criteria',
    [TestType.COMPATIBILITY]: 'compatibility across environments',
    [TestType.ACCESSIBILITY]: 'accessibility compliance',
    [TestType.LOCALIZATION]: 'localization and internationalization',
    [TestType.API]: 'API endpoints and responses',
    [TestType.DATABASE]: 'database operations and data integrity',
    [TestType.LOAD]: 'system behavior under load',
    [TestType.STRESS]: 'system limits and stress conditions',
    [TestType.RECOVERY]: 'system recovery capabilities',
    [TestType.UNRECOGNIZED]: 'general behavior',
  };
  return descriptions[type] || 'behavior';
}

export const testCasesClient = {
  async generateTestCases(request: GenerateTestCasesRequest): Promise<GenerateTestCasesResponse> {
    if (isMockMode()) {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 1500));

      const testCases = generateMockTestCases(request);

      return {
        requestId: request.requestId,
        success: true,
        testCases,
        metadata: {
          llmProvider: 'anthropic',
          llmModel: 'claude-3-sonnet',
          llmTokensUsed: 2500,
          generationTimeMs: 1500,
          testCasesGenerated: testCases.length,
          duplicatesFound: 0,
          coverage: {
            functionalCount: testCases.filter(tc => tc.type === TestType.FUNCTIONAL).length,
            negativeCount: testCases.filter(tc => tc.type === TestType.NEGATIVE).length,
            boundaryCount: testCases.filter(tc => tc.type === TestType.BOUNDARY).length,
            edgeCaseCount: testCases.filter(tc => tc.type === TestType.EDGE_CASE).length,
            uncoveredAreas: [],
          },
          domainContextUsed: '',
        },
        errorMessage: '',
      };
    }

    // Real gRPC-Web call using proper protobuf encoding
    return grpcWebUnaryCall<GenerateTestCasesRequest, GenerateTestCasesResponse>(
      GRPC_WEB_URL,
      'testcases.v1.TestCasesService/GenerateTestCases',
      request,
      GenerateTestCasesRequestMsg.encode,
      GenerateTestCasesResponseMsg.decode
    );
  },

  async healthCheck(): Promise<HealthCheckResponse> {
    if (isMockMode()) {
      return {
        status: 1, // SERVING
        version: '1.0.0',
        components: {
          llm: 'healthy',
          database: 'healthy',
        },
      };
    }

    // Real gRPC-Web call using proper protobuf encoding
    return grpcWebUnaryCall<Record<string, never>, HealthCheckResponse>(
      GRPC_WEB_URL,
      'testcases.v1.TestCasesService/HealthCheck',
      {},
      HealthCheckRequestMsg.encode,
      HealthCheckResponseMsg.decode
    );
  },

  // ============ History Methods ============

  async listHistory(request: ListHistoryRequest): Promise<ListHistoryResponse> {
    if (isMockMode()) {
      // Return mock history data
      await new Promise(resolve => setTimeout(resolve, 300));
      return {
        sessions: [
          {
            sessionId: 'mock-session-1',
            userStoryPreview: 'As a user, I want to login to the system...',
            domain: 'ecommerce',
            testTypes: ['functional', 'negative'],
            coverageLevel: 'standard',
            testCaseCount: 5,
            status: 'success',
            createdAt: new Date(Date.now() - 3600000).toISOString(),
          },
          {
            sessionId: 'mock-session-2',
            userStoryPreview: 'As a customer, I want to add items to cart...',
            domain: 'ecommerce',
            testTypes: ['functional', 'boundary'],
            coverageLevel: 'comprehensive',
            testCaseCount: 8,
            status: 'success',
            createdAt: new Date(Date.now() - 7200000).toISOString(),
          },
        ],
        totalCount: 2,
      };
    }

    return grpcWebUnaryCall<ListHistoryRequest, ListHistoryResponse>(
      GRPC_WEB_URL,
      'testcases.v1.TestCasesService/ListHistory',
      request,
      ListHistoryRequestMsg.encode,
      ListHistoryResponseMsg.decode
    );
  },

  async getHistorySession(request: GetHistorySessionRequest): Promise<GetHistorySessionResponse> {
    if (isMockMode()) {
      await new Promise(resolve => setTimeout(resolve, 300));
      if (request.sessionId === 'mock-session-1') {
        return {
          session: {
            sessionId: 'mock-session-1',
            userStory: 'As a user, I want to login to the system so that I can access my account',
            acceptanceCriteria: [
              'User can enter email and password',
              'System validates credentials',
              'User is redirected to dashboard on success',
            ],
            domain: 'ecommerce',
            testTypes: ['functional', 'negative'],
            coverageLevel: 'standard',
            testCases: generateMockTestCases({
              requestId: 'mock',
              userStory: { story: 'Login test', acceptanceCriteria: [], additionalContext: '' },
              generationConfig: {
                testTypes: [TestType.FUNCTIONAL, TestType.NEGATIVE],
                maxTestCases: 5,
                outputFormat: OutputFormat.TRADITIONAL,
                coverageLevel: 0,
                llmProvider: 'anthropic',
                checkDuplicates: false,
                priorityFocus: '',
                count: 5,
                includeEdgeCases: false,
                includeNegativeTests: true,
                detailLevel: 'medium',
              },
              domainConfig: {
                domain: 'ecommerce',
                entity: '',
                workflow: '',
                includeBusinessRules: false,
                includeEdgeCases: false,
              },
              testDataConfig: {
                generateTestData: false,
                placement: 0,
                samplesPerCase: 0,
              },
            }),
            testCaseCount: 5,
            generationMethod: 'llm',
            modelUsed: 'claude-3-sonnet',
            generationTimeMs: 1500,
            status: 'success',
            errorMessage: '',
            metadata: {},
            createdAt: new Date(Date.now() - 3600000).toISOString(),
            updatedAt: new Date(Date.now() - 3600000).toISOString(),
          },
          found: true,
        };
      }
      return { found: false, session: undefined };
    }

    return grpcWebUnaryCall<GetHistorySessionRequest, GetHistorySessionResponse>(
      GRPC_WEB_URL,
      'testcases.v1.TestCasesService/GetHistorySession',
      request,
      GetHistorySessionRequestMsg.encode,
      GetHistorySessionResponseMsg.decode
    );
  },

  async deleteHistorySession(request: DeleteHistorySessionRequest): Promise<DeleteHistorySessionResponse> {
    if (isMockMode()) {
      await new Promise(resolve => setTimeout(resolve, 200));
      return {
        success: true,
        message: `Session ${request.sessionId} deleted successfully`,
      };
    }

    return grpcWebUnaryCall<DeleteHistorySessionRequest, DeleteHistorySessionResponse>(
      GRPC_WEB_URL,
      'testcases.v1.TestCasesService/DeleteHistorySession',
      request,
      DeleteHistorySessionRequestMsg.encode,
      DeleteHistorySessionResponseMsg.decode
    );
  },
};

// Re-export types for convenience
export type {
  ListHistoryRequest,
  ListHistoryResponse,
  GetHistorySessionRequest,
  GetHistorySessionResponse,
  DeleteHistorySessionRequest,
  DeleteHistorySessionResponse,
  HistorySessionSummary,
  HistorySession,
};

export default testCasesClient;
