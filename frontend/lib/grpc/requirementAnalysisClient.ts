import { BinaryReader, BinaryWriter } from "@bufbuild/protobuf/wire";
import {
  AnalyzeRequest as AnalyzeRequestMsg,
  AnalyzeResponse as AnalyzeResponseMsg,
  ReanalyzeRequest as ReanalyzeRequestMsg,
  ExportRequest as ExportRequestMsg,
  ExportResponse as ExportResponseMsg,
  HealthCheckRequest as HealthCheckRequestMsg,
  HealthCheckResponse as HealthCheckResponseMsg,
  type AnalyzeRequest,
  type AnalyzeResponse,
  type ReanalyzeRequest,
  type ExportRequest,
  type ExportResponse,
  type HealthCheckResponse,
  type QualityScore,
  type Gap,
  type ClarifyingQuestion,
  type GeneratedAC,
  type ExtractedRequirement,
  type DomainValidation,
  type AnalysisMetadata,
} from './generated/requirement_analysis';

const GRPC_WEB_URL = process.env.NEXT_PUBLIC_GRPC_WEB_URL || 'http://localhost:8085';

function isMockMode(): boolean {
  return process.env.NEXT_PUBLIC_USE_MOCK === 'true';
}

/**
 * Encode a protobuf message with gRPC-Web framing
 */
function encodeGrpcWebRequest(messageBytes: Uint8Array): Uint8Array {
  const frame = new Uint8Array(5 + messageBytes.length);
  frame[0] = 0; // No compression
  const length = messageBytes.length;
  frame[1] = (length >> 24) & 0xff;
  frame[2] = (length >> 16) & 0xff;
  frame[3] = (length >> 8) & 0xff;
  frame[4] = length & 0xff;
  frame.set(messageBytes, 5);
  return frame;
}

/**
 * Decode a gRPC-Web response
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

    if (compressionFlag & 0x80) {
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
  const writer = new BinaryWriter();
  encode(request, writer);
  const messageBytes = writer.finish();
  const framedRequest = encodeGrpcWebRequest(messageBytes);

  const bodyBuffer = new ArrayBuffer(framedRequest.length);
  const bodyView = new Uint8Array(bodyBuffer);
  bodyView.set(framedRequest);

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

  const responseData = new Uint8Array(await response.arrayBuffer());
  const { messageBytes: respBytes, trailers } = decodeGrpcWebResponse(responseData);

  const grpcStatus = trailers.get('grpc-status');
  if (grpcStatus && grpcStatus !== '0') {
    const grpcMessage = trailers.get('grpc-message') || 'Unknown gRPC error';
    throw new Error(`gRPC error (${grpcStatus}): ${decodeURIComponent(grpcMessage)}`);
  }

  return decode(respBytes);
}

// Mock data generators
function generateMockQualityScore(): QualityScore {
  return {
    overallScore: 72,
    overallGrade: 'B',
    clarity: {
      score: 75,
      grade: 'B',
      issues: ['Some terms could be more specific', 'Consider defining edge cases'],
    },
    completeness: {
      score: 65,
      grade: 'C',
      issues: ['Missing error handling scenarios', 'No performance requirements specified'],
    },
    testability: {
      score: 80,
      grade: 'B',
      issues: ['Some acceptance criteria could be more measurable'],
    },
    consistency: {
      score: 70,
      grade: 'B',
      issues: ['Minor terminology inconsistencies'],
    },
    recommendation: 'Address the completeness gaps before proceeding to test case generation.',
  };
}

function generateMockGaps(): Gap[] {
  return [
    {
      id: 'GAP-001',
      category: 'missing_error_handling',
      severity: 'high',
      description: 'No error handling specified for failed authentication',
      location: 'Description',
      suggestion: 'Add acceptance criteria for invalid credentials, locked accounts, and network failures',
    },
    {
      id: 'GAP-002',
      category: 'ambiguous_term',
      severity: 'medium',
      description: 'Term "quickly" is not measurable',
      location: 'Acceptance Criteria #2',
      suggestion: 'Define specific time threshold (e.g., "within 2 seconds")',
    },
    {
      id: 'GAP-003',
      category: 'missing_edge_case',
      severity: 'medium',
      description: 'Cart with maximum item limit not addressed',
      location: 'Description',
      suggestion: 'Specify behavior when cart reaches maximum capacity',
    },
  ];
}

function generateMockQuestions(): ClarifyingQuestion[] {
  return [
    {
      id: 'Q-001',
      priority: 'high',
      category: 'error_handling',
      question: 'What should happen when a user tries to add an out-of-stock item to cart?',
      context: 'The requirement does not specify behavior for unavailable items',
      suggestedAnswers: [
        'Show error message and prevent adding',
        'Add to wishlist instead',
        'Allow adding but mark as backordered',
      ],
      answer: '',
    },
    {
      id: 'Q-002',
      priority: 'medium',
      category: 'scope',
      question: 'Should guest users be able to add items to cart?',
      context: 'User authentication requirements are not specified',
      suggestedAnswers: ['Yes, with session-based cart', 'No, require login first', 'Yes, with cart transfer on login'],
      answer: '',
    },
  ];
}

function generateMockGeneratedACs(): GeneratedAC[] {
  return [
    {
      id: 'AC-GEN-001',
      source: 'gap_detection',
      confidence: 0.85,
      text: 'When invalid credentials are provided, the system should display an error message and allow retry',
      gherkin: `Given a user is on the login page
When they enter invalid credentials
Then the system displays an error message
And the user can retry authentication`,
      accepted: false,
    },
    {
      id: 'AC-GEN-002',
      source: 'domain_knowledge',
      confidence: 0.9,
      text: 'Cart total should update automatically when item quantity changes',
      gherkin: `Given items are in the cart
When the user changes item quantity
Then the cart total updates automatically
And the new total is displayed`,
      accepted: false,
    },
  ];
}

function generateMockAnalysisResponse(request: AnalyzeRequest): AnalyzeResponse {
  const inputType = request.jiraStory ? 'jira' : request.freeForm ? 'free_form' : 'transcript';
  const title = request.jiraStory?.summary ||
    request.freeForm?.title ||
    request.transcript?.meetingTitle ||
    'Untitled Requirement';
  const description = request.jiraStory?.description ||
    request.freeForm?.text ||
    request.transcript?.transcript ||
    '';

  return {
    requestId: request.requestId || `mock-${Date.now()}`,
    success: true,
    qualityScore: generateMockQualityScore(),
    extractedRequirement: {
      title,
      description,
      structure: {
        actor: 'Customer',
        secondaryActors: ['System'],
        action: 'add items to cart',
        object: 'shopping cart',
        outcome: 'successfully manage cart items',
        preconditions: ['User is logged in', 'Product catalog is available'],
        postconditions: ['Cart is updated', 'Cart total is recalculated'],
        triggers: ['User clicks Add to Cart button'],
        constraints: ['Maximum 100 items per cart'],
        entities: ['Cart', 'Product', 'User', 'Inventory'],
      },
      originalAcs: request.jiraStory?.acceptanceCriteria || [],
      inputType,
    },
    gaps: generateMockGaps(),
    questions: generateMockQuestions(),
    generatedAcs: generateMockGeneratedACs(),
    domainValidation: {
      valid: true,
      entitiesFound: [
        { term: 'cart', mappedEntity: 'ShoppingCart', confidence: 0.95, domainDescription: 'Customer shopping cart for holding products' },
        { term: 'product', mappedEntity: 'Product', confidence: 0.9, domainDescription: 'Item available for purchase' },
      ],
      rulesApplicable: [
        { ruleId: 'CART-001', rule: 'Cart must have at least one item for checkout', relevance: 'high' },
        { ruleId: 'CART-002', rule: 'Maximum cart value is $10,000', relevance: 'medium' },
      ],
      warnings: [],
    },
    readyForTestGeneration: false,
    blockers: ['High severity gaps need to be addressed', 'Clarifying questions need answers'],
    metadata: {
      llmProvider: 'anthropic',
      llmModel: 'claude-sonnet-4-20250514',
      tokensUsed: 3500,
      analysisTimeMs: 2100,
      inputType,
      agentVersion: '1.0.0',
    },
    error: '',
  };
}

export const requirementAnalysisClient = {
  async analyzeRequirement(request: AnalyzeRequest): Promise<AnalyzeResponse> {
    if (isMockMode()) {
      await new Promise(resolve => setTimeout(resolve, 2000));
      return generateMockAnalysisResponse(request);
    }

    return grpcWebUnaryCall<AnalyzeRequest, AnalyzeResponse>(
      GRPC_WEB_URL,
      'requirementanalysis.v1.RequirementAnalysisService/AnalyzeRequirement',
      request,
      AnalyzeRequestMsg.encode,
      AnalyzeResponseMsg.decode
    );
  },

  async reanalyzeRequirement(request: ReanalyzeRequest): Promise<AnalyzeResponse> {
    if (isMockMode()) {
      await new Promise(resolve => setTimeout(resolve, 1500));
      // Simulate improved score after reanalysis
      const mockResponse = generateMockAnalysisResponse({
        requestId: request.requestId,
        freeForm: { text: 'Updated requirement', context: '', title: 'Updated' },
        config: request.config,
      });
      mockResponse.qualityScore!.overallScore = 85;
      mockResponse.qualityScore!.overallGrade = 'A';
      mockResponse.readyForTestGeneration = true;
      mockResponse.blockers = [];
      return mockResponse;
    }

    return grpcWebUnaryCall<ReanalyzeRequest, AnalyzeResponse>(
      GRPC_WEB_URL,
      'requirementanalysis.v1.RequirementAnalysisService/ReanalyzeRequirement',
      request,
      ReanalyzeRequestMsg.encode,
      AnalyzeResponseMsg.decode
    );
  },

  async exportAnalysis(request: ExportRequest): Promise<ExportResponse> {
    if (isMockMode()) {
      await new Promise(resolve => setTimeout(resolve, 500));
      const isJson = request.format === 'json';
      return {
        requestId: request.requestId,
        success: true,
        format: request.format,
        content: isJson
          ? JSON.stringify({ analysis: 'mock export data' }, null, 2)
          : 'Mock text export content',
        filename: `analysis_${Date.now()}.${isJson ? 'json' : 'txt'}`,
        error: '',
      };
    }

    return grpcWebUnaryCall<ExportRequest, ExportResponse>(
      GRPC_WEB_URL,
      'requirementanalysis.v1.RequirementAnalysisService/ExportAnalysis',
      request,
      ExportRequestMsg.encode,
      ExportResponseMsg.decode
    );
  },

  async healthCheck(): Promise<HealthCheckResponse> {
    if (isMockMode()) {
      return {
        status: 'healthy',
        components: {
          llm: 'healthy',
          weaviate: 'healthy',
          domain_agent: 'healthy',
        },
      };
    }

    return grpcWebUnaryCall<Record<string, never>, HealthCheckResponse>(
      GRPC_WEB_URL,
      'requirementanalysis.v1.RequirementAnalysisService/HealthCheck',
      {},
      HealthCheckRequestMsg.encode,
      HealthCheckResponseMsg.decode
    );
  },
};

// Re-export types for convenience
export type {
  AnalyzeRequest,
  AnalyzeResponse,
  ReanalyzeRequest,
  ExportRequest,
  ExportResponse,
  HealthCheckResponse,
  QualityScore,
  Gap,
  ClarifyingQuestion,
  GeneratedAC,
  ExtractedRequirement,
  DomainValidation,
  AnalysisMetadata,
};

export default requirementAnalysisClient;
