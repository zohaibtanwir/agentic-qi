import {
  TestType,
  Priority,
  OutputFormat,
  TestCaseStatus,
  type GenerateTestCasesRequest,
  type GenerateTestCasesResponse,
  type HealthCheckResponse,
  type TestCase,
} from './generated/test_cases';

const GRPC_WEB_URL = process.env.NEXT_PUBLIC_GRPC_WEB_URL || 'http://localhost:8080';
const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true' || true; // Default to mock for development

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
    if (USE_MOCK) {
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

    // Real gRPC-Web call (when Envoy is configured)
    const response = await fetch(`${GRPC_WEB_URL}/testcases.v1.TestCasesService/GenerateTestCases`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/grpc-web+proto',
        'X-Grpc-Web': '1',
      },
      body: JSON.stringify(request), // Note: Real gRPC-Web uses binary encoding
    });

    if (!response.ok) {
      throw new Error(`gRPC error: ${response.status}`);
    }

    return response.json();
  },

  async healthCheck(): Promise<HealthCheckResponse> {
    if (USE_MOCK) {
      return {
        status: 1, // SERVING
        version: '1.0.0',
        components: {
          llm: 'healthy',
          database: 'healthy',
        },
      };
    }

    const response = await fetch(`${GRPC_WEB_URL}/testcases.v1.TestCasesService/HealthCheck`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/grpc-web+proto',
        'X-Grpc-Web': '1',
      },
    });

    return response.json();
  },
};

export default testCasesClient;
