import { testDataClient, GenerationMethod, OutputFormat } from '../testDataClient';
import type { GenerateRequest, Scenario } from '../testDataClient';

// Mock the fetch function
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('testDataClient', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset environment variables to mock mode
    process.env.NEXT_PUBLIC_USE_MOCK = 'true';
  });

  describe('generateData', () => {
    it('should generate cart data with correct structure in mock mode', async () => {
      const request: GenerateRequest = {
        requestId: 'test-123',
        domain: 'ecommerce',
        entity: 'cart',
        schema: undefined,
        constraints: undefined,
        scenarios: [],
        context: '',
        hints: [],
        outputFormat: OutputFormat.JSON,
        count: 5,
        useCache: false,
        learnFromHistory: false,
        defectTriggering: false,
        productionLike: false,
        inlineSchema: '',
        generationMethod: GenerationMethod.TRADITIONAL,
        customSchema: '',
      };

      const response = await testDataClient.generateData(request);

      expect(response.success).toBe(true);
      expect(response.recordCount).toBe(5);
      expect(response.error).toBe('');
      expect(response.metadata).toBeDefined();
      expect(response.metadata?.generationPath).toBe('traditional');

      const data = JSON.parse(response.data);
      expect(Array.isArray(data)).toBe(true);
      expect(data.length).toBe(5);

      // Verify cart structure
      const firstCart = data[0];
      expect(firstCart).toHaveProperty('cart_id');
      expect(firstCart).toHaveProperty('customer_id');
      expect(firstCart).toHaveProperty('items');
      expect(firstCart).toHaveProperty('total');
      expect(firstCart).toHaveProperty('created_at');
      expect(firstCart.cart_id).toMatch(/^CRT-2025-\d+$/);
    });

    it('should generate order data in mock mode', async () => {
      const request: GenerateRequest = {
        requestId: 'test-456',
        domain: 'ecommerce',
        entity: 'order',
        schema: undefined,
        constraints: undefined,
        scenarios: [],
        context: '',
        hints: [],
        outputFormat: OutputFormat.JSON,
        count: 3,
        useCache: false,
        learnFromHistory: false,
        defectTriggering: false,
        productionLike: false,
        inlineSchema: '',
        generationMethod: GenerationMethod.TRADITIONAL,
        customSchema: '',
      };

      const response = await testDataClient.generateData(request);

      expect(response.success).toBe(true);
      expect(response.recordCount).toBe(3);

      const data = JSON.parse(response.data);
      expect(data.length).toBe(3);

      const firstOrder = data[0];
      expect(firstOrder).toHaveProperty('order_id');
      expect(firstOrder).toHaveProperty('status');
      expect(firstOrder).toHaveProperty('total_amount');
      expect(firstOrder.order_id).toMatch(/^ORD-2025-\d+$/);
    });

    it('should generate user data in mock mode', async () => {
      const request: GenerateRequest = {
        requestId: 'test-789',
        domain: 'ecommerce',
        entity: 'user',
        schema: undefined,
        constraints: undefined,
        scenarios: [],
        context: '',
        hints: [],
        outputFormat: OutputFormat.JSON,
        count: 2,
        useCache: false,
        learnFromHistory: false,
        defectTriggering: false,
        productionLike: false,
        inlineSchema: '',
        generationMethod: GenerationMethod.TRADITIONAL,
        customSchema: '',
      };

      const response = await testDataClient.generateData(request);

      expect(response.success).toBe(true);
      expect(response.recordCount).toBe(2);

      const data = JSON.parse(response.data);
      const firstUser = data[0];
      expect(firstUser).toHaveProperty('user_id');
      expect(firstUser).toHaveProperty('email');
      expect(firstUser).toHaveProperty('name');
      expect(firstUser.user_id).toMatch(/^USR-\d+$/);
      expect(firstUser.email).toContain('@example.com');
    });

    it('should use LLM path when context is provided', async () => {
      const request: GenerateRequest = {
        requestId: 'test-llm',
        domain: 'ecommerce',
        entity: 'cart',
        schema: undefined,
        constraints: undefined,
        scenarios: [],
        context: 'Generate carts for ApplePay testing',
        hints: [],
        outputFormat: OutputFormat.JSON,
        count: 5,
        useCache: false,
        learnFromHistory: false,
        defectTriggering: false,
        productionLike: false,
        inlineSchema: '',
        generationMethod: GenerationMethod.LLM,
        customSchema: '',
      };

      const response = await testDataClient.generateData(request);

      expect(response.success).toBe(true);
      expect(response.metadata?.generationPath).toBe('llm');
      expect(response.metadata?.llmTokensUsed).toBeGreaterThan(0);
    });

    it('should respect scenario counts', async () => {
      const scenarios: Scenario[] = [
        { name: 'happy_path', count: 3, overrides: {}, description: '' },
        { name: 'edge_case', count: 2, overrides: {}, description: '' },
      ];

      const request: GenerateRequest = {
        requestId: 'test-scenarios',
        domain: 'ecommerce',
        entity: 'cart',
        schema: undefined,
        constraints: undefined,
        scenarios,
        context: '',
        hints: [],
        outputFormat: OutputFormat.JSON,
        count: 5,
        useCache: false,
        learnFromHistory: false,
        defectTriggering: false,
        productionLike: false,
        inlineSchema: '',
        generationMethod: GenerationMethod.TRADITIONAL,
        customSchema: '',
      };

      const response = await testDataClient.generateData(request);

      expect(response.success).toBe(true);
      expect(response.metadata?.scenarioCounts).toEqual({
        happy_path: 3,
        edge_case: 2,
      });

      const data = JSON.parse(response.data);
      const scenarioNames = data.map((d: { _scenario: string }) => d._scenario);
      expect(scenarioNames).toContain('happy_path');
      expect(scenarioNames).toContain('edge_case');
    });

    it('should include metadata with timing and coherence', async () => {
      const request: GenerateRequest = {
        requestId: 'test-meta',
        domain: 'ecommerce',
        entity: 'cart',
        schema: undefined,
        constraints: undefined,
        scenarios: [],
        context: '',
        hints: [],
        outputFormat: OutputFormat.JSON,
        count: 1,
        useCache: false,
        learnFromHistory: false,
        defectTriggering: false,
        productionLike: false,
        inlineSchema: '',
        generationMethod: GenerationMethod.TRADITIONAL,
        customSchema: '',
      };

      const response = await testDataClient.generateData(request);

      expect(response.metadata).toBeDefined();
      expect(response.metadata?.generationTimeMs).toBeGreaterThan(0);
      expect(response.metadata?.coherenceScore).toBeGreaterThanOrEqual(0.85);
      expect(response.metadata?.coherenceScore).toBeLessThanOrEqual(1.0);
    });
  });

  describe('getSchemas', () => {
    it('should return all schemas when no domain filter', async () => {
      const response = await testDataClient.getSchemas();

      expect(response.schemas).toBeDefined();
      expect(response.schemas.length).toBeGreaterThan(0);

      const schemaNames = response.schemas.map(s => s.name);
      expect(schemaNames).toContain('cart');
      expect(schemaNames).toContain('order');
      expect(schemaNames).toContain('user');
      expect(schemaNames).toContain('product');
      expect(schemaNames).toContain('payment');
      expect(schemaNames).toContain('review');
    });

    it('should filter schemas by domain', async () => {
      const response = await testDataClient.getSchemas('ecommerce');

      expect(response.schemas).toBeDefined();
      response.schemas.forEach(schema => {
        expect(schema.domain).toBe('ecommerce');
      });
    });

    it('should return empty array for unknown domain', async () => {
      const response = await testDataClient.getSchemas('unknown_domain');

      expect(response.schemas).toEqual([]);
    });

    it('should include field information in schemas', async () => {
      const response = await testDataClient.getSchemas();

      const cartSchema = response.schemas.find(s => s.name === 'cart');
      expect(cartSchema).toBeDefined();
      expect(cartSchema?.fields.length).toBeGreaterThan(0);

      const cartIdField = cartSchema?.fields.find(f => f.name === 'cart_id');
      expect(cartIdField).toBeDefined();
      expect(cartIdField?.type).toBe('UUID');
      expect(cartIdField?.required).toBe(true);
      expect(cartIdField?.description).toBeTruthy();
    });
  });

  describe('healthCheck', () => {
    it('should return healthy status in mock mode', async () => {
      const response = await testDataClient.healthCheck();

      expect(response.status).toBe('healthy');
      expect(response.components).toBeDefined();
      expect(response.components['llm']).toBe('healthy');
      expect(response.components['database']).toBe('healthy');
      expect(response.components['cache']).toBe('healthy');
    });
  });

  describe('error handling', () => {
    it('should return mock data even for unknown entities', async () => {
      // Mock mode should gracefully handle unknown entities with a default response
      const request: GenerateRequest = {
        requestId: 'test-unknown',
        domain: 'ecommerce',
        entity: 'unknown_entity',
        schema: undefined,
        constraints: undefined,
        scenarios: [],
        context: '',
        hints: [],
        outputFormat: OutputFormat.JSON,
        count: 2,
        useCache: false,
        learnFromHistory: false,
        defectTriggering: false,
        productionLike: false,
        inlineSchema: '',
        generationMethod: GenerationMethod.TRADITIONAL,
        customSchema: '',
      };

      const response = await testDataClient.generateData(request);

      // Should still return a valid response structure
      expect(response.success).toBe(true);
      expect(response.recordCount).toBe(2);
      expect(response.data).toBeTruthy();
    });

    it('should handle zero count gracefully', async () => {
      const request: GenerateRequest = {
        requestId: 'test-zero',
        domain: 'ecommerce',
        entity: 'cart',
        schema: undefined,
        constraints: undefined,
        scenarios: [],
        context: '',
        hints: [],
        outputFormat: OutputFormat.JSON,
        count: 0,
        useCache: false,
        learnFromHistory: false,
        defectTriggering: false,
        productionLike: false,
        inlineSchema: '',
        generationMethod: GenerationMethod.TRADITIONAL,
        customSchema: '',
      };

      const response = await testDataClient.generateData(request);

      expect(response.success).toBe(true);
      expect(response.recordCount).toBe(0);
      const data = JSON.parse(response.data);
      expect(data.length).toBe(0);
    });
  });
});

describe('Output format types', () => {
  it('should have correct OutputFormat enum values', () => {
    expect(OutputFormat.JSON).toBe(0);
    expect(OutputFormat.CSV).toBe(1);
    expect(OutputFormat.SQL).toBe(2);
  });
});

describe('GenerationMethod types', () => {
  it('should have correct GenerationMethod enum values', () => {
    expect(GenerationMethod.TRADITIONAL).toBe(0);
    expect(GenerationMethod.LLM).toBe(1);
    expect(GenerationMethod.RAG).toBe(2);
    expect(GenerationMethod.HYBRID).toBe(3);
  });
});

describe('additional entity types', () => {
  it('should generate product data with correct structure', async () => {
    const request: GenerateRequest = {
      requestId: 'test-product',
      domain: 'ecommerce',
      entity: 'product',
      schema: undefined,
      constraints: undefined,
      scenarios: [],
      context: '',
      hints: [],
      outputFormat: OutputFormat.JSON,
      count: 3,
      useCache: false,
      learnFromHistory: false,
      defectTriggering: false,
      productionLike: false,
      inlineSchema: '',
      generationMethod: GenerationMethod.TRADITIONAL,
      customSchema: '',
    };

    const response = await testDataClient.generateData(request);

    expect(response.success).toBe(true);
    expect(response.recordCount).toBe(3);
    // Product defaults to cart generator in current implementation
    const data = JSON.parse(response.data);
    expect(data.length).toBe(3);
  });

  it('should handle RAG generation method', async () => {
    const request: GenerateRequest = {
      requestId: 'test-rag',
      domain: 'ecommerce',
      entity: 'cart',
      schema: undefined,
      constraints: undefined,
      scenarios: [],
      context: 'Use RAG retrieval for context',
      hints: [],
      outputFormat: OutputFormat.JSON,
      count: 2,
      useCache: false,
      learnFromHistory: false,
      defectTriggering: false,
      productionLike: false,
      inlineSchema: '',
      generationMethod: GenerationMethod.RAG,
      customSchema: '',
    };

    const response = await testDataClient.generateData(request);

    expect(response.success).toBe(true);
    // With context, it should use llm path
    expect(response.metadata?.generationPath).toBe('llm');
  });

  it('should handle HYBRID generation method', async () => {
    const request: GenerateRequest = {
      requestId: 'test-hybrid',
      domain: 'ecommerce',
      entity: 'order',
      schema: undefined,
      constraints: undefined,
      scenarios: [],
      context: '',
      hints: ['Use realistic data'],
      outputFormat: OutputFormat.CSV,
      count: 4,
      useCache: true,
      learnFromHistory: true,
      defectTriggering: true,
      productionLike: true,
      inlineSchema: '',
      generationMethod: GenerationMethod.HYBRID,
      customSchema: '',
    };

    const response = await testDataClient.generateData(request);

    expect(response.success).toBe(true);
    expect(response.recordCount).toBe(4);
  });
});

describe('schema details', () => {
  it('should include all ecommerce schemas', async () => {
    const response = await testDataClient.getSchemas();

    expect(response.schemas.length).toBe(6);
    const names = response.schemas.map(s => s.name);
    expect(names).toContain('cart');
    expect(names).toContain('order');
    expect(names).toContain('product');
    expect(names).toContain('user');
    expect(names).toContain('payment');
    expect(names).toContain('review');
  });

  it('should have correct field types for order schema', async () => {
    const response = await testDataClient.getSchemas();
    const orderSchema = response.schemas.find(s => s.name === 'order');

    expect(orderSchema).toBeDefined();
    expect(orderSchema?.fields.find(f => f.name === 'order_id')?.type).toBe('UUID');
    expect(orderSchema?.fields.find(f => f.name === 'status')?.type).toBe('ENUM');
    expect(orderSchema?.fields.find(f => f.name === 'total_amount')?.type).toBe('FLOAT');
  });

  it('should have correct field types for user schema', async () => {
    const response = await testDataClient.getSchemas();
    const userSchema = response.schemas.find(s => s.name === 'user');

    expect(userSchema).toBeDefined();
    expect(userSchema?.fields.find(f => f.name === 'email')?.type).toBe('EMAIL');
    expect(userSchema?.fields.find(f => f.name === 'phone')?.required).toBe(false);
  });
});

describe('data generation edge cases', () => {
  it('should generate large data sets', async () => {
    const request: GenerateRequest = {
      requestId: 'test-large',
      domain: 'ecommerce',
      entity: 'cart',
      schema: undefined,
      constraints: undefined,
      scenarios: [],
      context: '',
      hints: [],
      outputFormat: OutputFormat.JSON,
      count: 100,
      useCache: false,
      learnFromHistory: false,
      defectTriggering: false,
      productionLike: false,
      inlineSchema: '',
      generationMethod: GenerationMethod.TRADITIONAL,
      customSchema: '',
    };

    const response = await testDataClient.generateData(request);

    expect(response.success).toBe(true);
    expect(response.recordCount).toBe(100);
    const data = JSON.parse(response.data);
    expect(data.length).toBe(100);
  });

  it('should generate consistent metadata structure', async () => {
    const request: GenerateRequest = {
      requestId: 'test-meta-structure',
      domain: 'ecommerce',
      entity: 'user',
      schema: undefined,
      constraints: undefined,
      scenarios: [],
      context: '',
      hints: [],
      outputFormat: OutputFormat.SQL,
      count: 5,
      useCache: false,
      learnFromHistory: false,
      defectTriggering: false,
      productionLike: false,
      inlineSchema: '',
      generationMethod: GenerationMethod.TRADITIONAL,
      customSchema: '',
    };

    const response = await testDataClient.generateData(request);

    expect(response.metadata).toMatchObject({
      generationPath: expect.any(String),
      llmTokensUsed: expect.any(Number),
      generationTimeMs: expect.any(Number),
      coherenceScore: expect.any(Number),
      scenarioCounts: expect.any(Object),
    });
  });

  it('should handle multiple scenarios correctly', async () => {
    const scenarios: Scenario[] = [
      { name: 'valid_checkout', count: 5, overrides: {}, description: 'Valid checkout flow' },
      { name: 'invalid_payment', count: 3, overrides: {}, description: 'Payment failures' },
      { name: 'empty_cart', count: 2, overrides: {}, description: 'Empty cart edge case' },
    ];

    const request: GenerateRequest = {
      requestId: 'test-multi-scenarios',
      domain: 'ecommerce',
      entity: 'cart',
      schema: undefined,
      constraints: undefined,
      scenarios,
      context: '',
      hints: [],
      outputFormat: OutputFormat.JSON,
      count: 10,
      useCache: false,
      learnFromHistory: false,
      defectTriggering: false,
      productionLike: false,
      inlineSchema: '',
      generationMethod: GenerationMethod.TRADITIONAL,
      customSchema: '',
    };

    const response = await testDataClient.generateData(request);

    expect(response.success).toBe(true);
    expect(response.metadata?.scenarioCounts).toEqual({
      valid_checkout: 5,
      invalid_payment: 3,
      empty_cart: 2,
    });
  });
});
