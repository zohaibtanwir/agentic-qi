import { BinaryReader, BinaryWriter } from "@bufbuild/protobuf/wire";
import {
  GenerationMethod,
  OutputFormat,
  GenerateRequest as GenerateRequestMsg,
  GenerateResponse as GenerateResponseMsg,
  GetSchemasRequest as GetSchemasRequestMsg,
  GetSchemasResponse as GetSchemasResponseMsg,
  HealthCheckRequest as HealthCheckRequestMsg,
  HealthCheckResponse as HealthCheckResponseMsg,
  type GenerateRequest,
  type GenerateResponse,
  type GetSchemasResponse,
  type HealthCheckResponse,
  type SchemaInfo,
  type Scenario,
} from './generated/test_data';

const GRPC_WEB_URL = process.env.NEXT_PUBLIC_GRPC_WEB_URL || 'http://localhost:8085';
// Default to real backend; only use mock if explicitly set to 'true'
// Use a function to check at runtime so tests can set the env variable after import
function isMockMode(): boolean {
  return process.env.NEXT_PUBLIC_USE_MOCK === 'true';
}

/**
 * Encode a protobuf message with gRPC-Web framing
 */
function encodeGrpcWebRequest(messageBytes: Uint8Array): Uint8Array {
  const frame = new Uint8Array(5 + messageBytes.length);
  frame[0] = 0; // Compression flag
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

// eslint-disable-next-line @typescript-eslint/no-unused-vars
function _base64ToBytes(base64: string): Uint8Array {
  let padded = base64;
  while (padded.length % 4 !== 0) {
    padded += '=';
  }
  padded = padded.replace(/-/g, '+').replace(/_/g, '/');
  const binaryString = atob(padded);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes;
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
function _bytesToBase64(bytes: Uint8Array): string {
  let binary = '';
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

/**
 * Make a gRPC-Web unary call (binary mode)
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

  const response = await fetch(`${url}/${method}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/grpc-web+proto',
      'X-Grpc-Web': '1',
      'Accept': 'application/grpc-web+proto',
    },
    body: framedRequest as unknown as BodyInit,
  });

  if (!response.ok) {
    throw new Error(`gRPC HTTP error: ${response.status} ${response.statusText}`);
  }

  const responseData = new Uint8Array(await response.arrayBuffer());

  if (responseData.length === 0) {
    throw new Error('Empty response from gRPC server');
  }

  const { messageBytes: respBytes, trailers } = decodeGrpcWebResponse(responseData);

  const grpcStatus = trailers.get('grpc-status');
  if (grpcStatus && grpcStatus !== '0') {
    const grpcMessage = trailers.get('grpc-message') || 'Unknown gRPC error';
    throw new Error(`gRPC error (${grpcStatus}): ${decodeURIComponent(grpcMessage)}`);
  }

  if (respBytes.length === 0) {
    throw new Error('No message data in response');
  }

  return decode(respBytes);
}

// ============= Mock Data Generators =============

const MOCK_SCHEMAS: SchemaInfo[] = [
  {
    name: 'cart',
    domain: 'ecommerce',
    description: 'Shopping cart with items and customer info',
    fields: [
      { name: 'cart_id', type: 'UUID', required: true, description: 'Unique cart identifier', example: 'CRT-2025-847291' },
      { name: 'customer_id', type: 'UUID', required: true, description: 'Customer reference', example: 'USR-4829173' },
      { name: 'items', type: 'ARRAY', required: true, description: 'Cart items', example: '[{sku, name, quantity, price}]' },
      { name: 'total', type: 'FLOAT', required: true, description: 'Cart total', example: '228.34' },
      { name: 'created_at', type: 'DATETIME', required: true, description: 'Creation timestamp', example: '2025-01-15T10:30:00Z' },
    ],
  },
  {
    name: 'order',
    domain: 'ecommerce',
    description: 'Customer order with shipping and payment info',
    fields: [
      { name: 'order_id', type: 'UUID', required: true, description: 'Unique order identifier', example: 'ORD-2025-123456' },
      { name: 'customer_id', type: 'UUID', required: true, description: 'Customer reference', example: 'USR-4829173' },
      { name: 'status', type: 'ENUM', required: true, description: 'Order status', example: 'pending' },
      { name: 'total_amount', type: 'FLOAT', required: true, description: 'Order total', example: '299.99' },
      { name: 'shipping_address', type: 'ADDRESS', required: true, description: 'Delivery address', example: '123 Main St...' },
    ],
  },
  {
    name: 'product',
    domain: 'ecommerce',
    description: 'Product catalog entry',
    fields: [
      { name: 'product_id', type: 'UUID', required: true, description: 'Product identifier', example: 'PRD-12345' },
      { name: 'name', type: 'STRING', required: true, description: 'Product name', example: 'Nike Air Max' },
      { name: 'price', type: 'FLOAT', required: true, description: 'Unit price', example: '129.99' },
      { name: 'category', type: 'STRING', required: true, description: 'Product category', example: 'Footwear' },
      { name: 'in_stock', type: 'BOOLEAN', required: true, description: 'Stock availability', example: 'true' },
    ],
  },
  {
    name: 'user',
    domain: 'ecommerce',
    description: 'Customer profile',
    fields: [
      { name: 'user_id', type: 'UUID', required: true, description: 'User identifier', example: 'USR-4829173' },
      { name: 'email', type: 'EMAIL', required: true, description: 'Email address', example: 'john@example.com' },
      { name: 'name', type: 'STRING', required: true, description: 'Full name', example: 'John Doe' },
      { name: 'phone', type: 'PHONE', required: false, description: 'Phone number', example: '+1-555-123-4567' },
    ],
  },
  {
    name: 'payment',
    domain: 'ecommerce',
    description: 'Payment transaction',
    fields: [
      { name: 'payment_id', type: 'UUID', required: true, description: 'Payment identifier', example: 'PAY-2025-789012' },
      { name: 'order_id', type: 'UUID', required: true, description: 'Associated order', example: 'ORD-2025-123456' },
      { name: 'amount', type: 'FLOAT', required: true, description: 'Payment amount', example: '299.99' },
      { name: 'method', type: 'ENUM', required: true, description: 'Payment method', example: 'credit_card' },
      { name: 'status', type: 'ENUM', required: true, description: 'Payment status', example: 'completed' },
    ],
  },
  {
    name: 'review',
    domain: 'ecommerce',
    description: 'Product review',
    fields: [
      { name: 'review_id', type: 'UUID', required: true, description: 'Review identifier', example: 'REV-2025-456789' },
      { name: 'product_id', type: 'UUID', required: true, description: 'Reviewed product', example: 'PRD-12345' },
      { name: 'user_id', type: 'UUID', required: true, description: 'Reviewer', example: 'USR-4829173' },
      { name: 'rating', type: 'INTEGER', required: true, description: 'Star rating 1-5', example: '5' },
      { name: 'comment', type: 'STRING', required: false, description: 'Review text', example: 'Great product!' },
    ],
  },
];

function generateMockCartData(count: number, scenarios: Scenario[]): object[] {
  const data: object[] = [];
  const items = [
    { sku: 'NKE-RUN-BLK-10', name: 'Nike Air Zoom Pegasus 40', price: 129.99 },
    { sku: 'ADI-TRN-WHT-9', name: 'Adidas Ultraboost 22', price: 189.99 },
    { sku: 'UA-SPT-GRY-M', name: 'Under Armour Training Tee', price: 35.00 },
    { sku: 'NKE-SHT-BLU-L', name: 'Nike Dri-FIT Shorts', price: 45.00 },
    { sku: 'PTG-YGA-MAT', name: 'Patagonia Yoga Mat', price: 68.00 },
  ];

  for (let i = 0; i < count; i++) {
    const scenario = scenarios.length > 0
      ? scenarios[i % scenarios.length].name
      : 'default';

    const cartItems = [];
    const itemCount = Math.floor(Math.random() * 4) + 1;
    let total = 0;

    for (let j = 0; j < itemCount; j++) {
      const item = items[Math.floor(Math.random() * items.length)];
      const quantity = Math.floor(Math.random() * 3) + 1;
      total += item.price * quantity;
      cartItems.push({ ...item, quantity });
    }

    data.push({
      _index: i,
      _scenario: scenario,
      cart_id: `CRT-2025-${String(Math.floor(Math.random() * 9000000) + 1000000)}`,
      customer_id: `USR-${String(Math.floor(Math.random() * 9000000) + 1000000)}`,
      items: cartItems,
      total: Math.round(total * 100) / 100,
      status: ['active', 'abandoned', 'converted'][Math.floor(Math.random() * 3)],
      created_at: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
    });
  }

  return data;
}

function generateMockOrderData(count: number, scenarios: Scenario[]): object[] {
  const data: object[] = [];
  const statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled'];

  for (let i = 0; i < count; i++) {
    const scenario = scenarios.length > 0
      ? scenarios[i % scenarios.length].name
      : 'default';

    data.push({
      _index: i,
      _scenario: scenario,
      order_id: `ORD-2025-${String(Math.floor(Math.random() * 9000000) + 1000000)}`,
      customer_id: `USR-${String(Math.floor(Math.random() * 9000000) + 1000000)}`,
      status: statuses[Math.floor(Math.random() * statuses.length)],
      total_amount: Math.round((Math.random() * 500 + 50) * 100) / 100,
      item_count: Math.floor(Math.random() * 5) + 1,
      shipping_address: `${Math.floor(Math.random() * 999) + 1} Main Street, City, ST ${String(Math.floor(Math.random() * 90000) + 10000)}`,
      created_at: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
    });
  }

  return data;
}

function generateMockUserData(count: number, scenarios: Scenario[]): object[] {
  const data: object[] = [];
  const firstNames = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Chris', 'Lisa'];
  const lastNames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis'];

  for (let i = 0; i < count; i++) {
    const scenario = scenarios.length > 0
      ? scenarios[i % scenarios.length].name
      : 'default';

    const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
    const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];

    data.push({
      _index: i,
      _scenario: scenario,
      user_id: `USR-${String(Math.floor(Math.random() * 9000000) + 1000000)}`,
      email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}@example.com`,
      name: `${firstName} ${lastName}`,
      phone: `+1-555-${String(Math.floor(Math.random() * 900) + 100)}-${String(Math.floor(Math.random() * 9000) + 1000)}`,
      created_at: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString(),
    });
  }

  return data;
}

function generateMockData(request: GenerateRequest): object[] {
  const { entity, count, scenarios } = request;

  switch (entity.toLowerCase()) {
    case 'cart':
      return generateMockCartData(count, scenarios);
    case 'order':
      return generateMockOrderData(count, scenarios);
    case 'user':
      return generateMockUserData(count, scenarios);
    default:
      return generateMockCartData(count, scenarios);
  }
}

// ============= Client Export =============

export const testDataClient = {
  async generateData(request: GenerateRequest): Promise<GenerateResponse> {
    if (isMockMode()) {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));

      const data = generateMockData(request);
      const generationPath = request.generationMethod === GenerationMethod.TRADITIONAL
        ? 'traditional'
        : request.context ? 'llm' : 'traditional';

      return {
        requestId: request.requestId || `REQ-${Date.now()}`,
        success: true,
        data: JSON.stringify(data, null, 2),
        recordCount: data.length,
        metadata: {
          generationPath,
          llmTokensUsed: generationPath === 'llm' ? Math.floor(Math.random() * 3000) + 500 : 0,
          generationTimeMs: Math.floor(Math.random() * 2000) + 500,
          coherenceScore: 0.85 + Math.random() * 0.15,
          scenarioCounts: request.scenarios.reduce((acc, s) => {
            acc[s.name] = s.count;
            return acc;
          }, {} as Record<string, number>),
        },
        error: '',
      };
    }

    return grpcWebUnaryCall<GenerateRequest, GenerateResponse>(
      GRPC_WEB_URL,
      'testdata.v1.TestDataService/GenerateData',
      request,
      GenerateRequestMsg.encode,
      GenerateResponseMsg.decode
    );
  },

  async getSchemas(domain?: string): Promise<GetSchemasResponse> {
    if (isMockMode()) {
      await new Promise(resolve => setTimeout(resolve, 300));

      const schemas = domain
        ? MOCK_SCHEMAS.filter(s => s.domain === domain)
        : MOCK_SCHEMAS;

      return { schemas };
    }

    return grpcWebUnaryCall<{ domain: string }, GetSchemasResponse>(
      GRPC_WEB_URL,
      'testdata.v1.TestDataService/GetSchemas',
      { domain: domain || '' },
      GetSchemasRequestMsg.encode,
      GetSchemasResponseMsg.decode
    );
  },

  async healthCheck(): Promise<HealthCheckResponse> {
    if (isMockMode()) {
      return {
        status: 'healthy',
        components: {
          llm: 'healthy',
          database: 'healthy',
          cache: 'healthy',
        },
      };
    }

    return grpcWebUnaryCall<Record<string, never>, HealthCheckResponse>(
      GRPC_WEB_URL,
      'testdata.v1.TestDataService/HealthCheck',
      {},
      HealthCheckRequestMsg.encode,
      HealthCheckResponseMsg.decode
    );
  },
};

// Re-export types for consumers
export type {
  GenerateRequest,
  GenerateResponse,
  GetSchemasResponse,
  HealthCheckResponse,
  SchemaInfo,
  Scenario,
};

export { GenerationMethod, OutputFormat };

export default testDataClient;
