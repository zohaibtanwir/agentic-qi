import { BinaryReader, BinaryWriter } from "@bufbuild/protobuf/wire";
import {
  DomainContextRequest as DomainContextRequestMsg,
  DomainContextResponse as DomainContextResponseMsg,
  KnowledgeRequest as KnowledgeRequestMsg,
  KnowledgeResponse as KnowledgeResponseMsg,
  EntityRequest as EntityRequestMsg,
  EntityResponse as EntityResponseMsg,
  WorkflowRequest as WorkflowRequestMsg,
  WorkflowResponse as WorkflowResponseMsg,
  ListEntitiesRequest as ListEntitiesRequestMsg,
  ListEntitiesResponse as ListEntitiesResponseMsg,
  ListWorkflowsRequest as ListWorkflowsRequestMsg,
  ListWorkflowsResponse as ListWorkflowsResponseMsg,
  EdgeCasesRequest as EdgeCasesRequestMsg,
  EdgeCasesResponse as EdgeCasesResponseMsg,
  GenerateTestDataRequest as GenerateTestDataRequestMsg,
  GenerateTestDataResponse as GenerateTestDataResponseMsg,
  HealthCheckRequest as HealthCheckRequestMsg,
  HealthCheckResponse as HealthCheckResponseMsg,
  GenerationMethod,
  type DomainContextRequest,
  type DomainContextResponse,
  type KnowledgeRequest,
  type KnowledgeResponse,
  type EntityRequest,
  type EntityResponse,
  type WorkflowRequest,
  type WorkflowResponse,
  type ListEntitiesRequest,
  type ListEntitiesResponse,
  type ListWorkflowsRequest,
  type ListWorkflowsResponse,
  type EdgeCasesRequest,
  type EdgeCasesResponse,
  type GenerateTestDataRequest,
  type GenerateTestDataResponse,
  type HealthCheckResponse,
  type Entity,
  type EntitySummary,
  type EntityField,
  type Workflow,
  type WorkflowSummary,
  type WorkflowStep,
  type BusinessRule,
  type EntityRelationship,
  type KnowledgeItem,
  type EdgeCase,
  type GenerationMetadata,
} from './generated/ecommerce_domain';

const GRPC_WEB_URL = process.env.NEXT_PUBLIC_GRPC_WEB_URL || 'http://localhost:8085';

// Default to real backend; only use mock if explicitly set to 'true'
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

// ============= Mock Data =============

const MOCK_ENTITIES: EntitySummary[] = [
  { name: 'cart', description: 'Shopping cart with items and customer info', category: 'shopping', fieldCount: 8 },
  { name: 'cart_item', description: 'Individual item in a shopping cart', category: 'shopping', fieldCount: 6 },
  { name: 'order', description: 'Customer order with shipping and payment info', category: 'orders', fieldCount: 12 },
  { name: 'order_item', description: 'Individual item in an order', category: 'orders', fieldCount: 7 },
  { name: 'product', description: 'Product catalog entry', category: 'inventory', fieldCount: 15 },
  { name: 'product_variant', description: 'Product variant (size, color)', category: 'inventory', fieldCount: 8 },
  { name: 'customer', description: 'Customer profile and preferences', category: 'customer', fieldCount: 10 },
  { name: 'address', description: 'Customer address for shipping/billing', category: 'customer', fieldCount: 9 },
  { name: 'payment', description: 'Payment transaction record', category: 'payments', fieldCount: 11 },
  { name: 'payment_method', description: 'Stored payment method', category: 'payments', fieldCount: 7 },
  { name: 'shipment', description: 'Shipment tracking information', category: 'shipping', fieldCount: 10 },
  { name: 'return', description: 'Product return request', category: 'returns', fieldCount: 9 },
  { name: 'review', description: 'Product review from customer', category: 'customer', fieldCount: 6 },
  { name: 'coupon', description: 'Discount coupon or promo code', category: 'pricing', fieldCount: 8 },
  { name: 'inventory', description: 'Inventory stock levels', category: 'inventory', fieldCount: 6 },
];

const MOCK_WORKFLOWS: WorkflowSummary[] = [
  { name: 'checkout', description: 'Complete checkout flow from cart to order confirmation', stepCount: 8, involvedEntities: ['cart', 'order', 'payment', 'shipment'] },
  { name: 'return', description: 'Product return and refund processing', stepCount: 6, involvedEntities: ['order', 'return', 'payment', 'inventory'] },
  { name: 'guest_checkout', description: 'Checkout flow for guest users', stepCount: 7, involvedEntities: ['cart', 'order', 'payment', 'customer'] },
  { name: 'subscription', description: 'Recurring subscription order flow', stepCount: 5, involvedEntities: ['order', 'payment', 'customer'] },
];

const MOCK_ENTITY_DETAILS: Record<string, Entity> = {
  cart: {
    name: 'cart',
    description: 'Shopping cart with items and customer info',
    fields: [
      { name: 'cart_id', type: 'UUID', description: 'Unique cart identifier', required: true, validations: ['format:uuid'], example: 'CRT-2025-847291' },
      { name: 'customer_id', type: 'UUID', description: 'Customer reference', required: true, validations: ['format:uuid'], example: 'USR-4829173' },
      { name: 'items', type: 'ARRAY', description: 'Cart items', required: true, validations: ['min_items:0', 'max_items:100'], example: '[{sku, quantity, price}]' },
      { name: 'subtotal', type: 'DECIMAL', description: 'Cart subtotal before tax/shipping', required: true, validations: ['min:0'], example: '228.34' },
      { name: 'status', type: 'ENUM', description: 'Cart status', required: true, validations: ['values:active,abandoned,converted'], example: 'active' },
      { name: 'created_at', type: 'DATETIME', description: 'Creation timestamp', required: true, validations: [], example: '2025-01-15T10:30:00Z' },
      { name: 'updated_at', type: 'DATETIME', description: 'Last update timestamp', required: true, validations: [], example: '2025-01-15T11:45:00Z' },
      { name: 'expires_at', type: 'DATETIME', description: 'Cart expiration time', required: false, validations: [], example: '2025-01-22T10:30:00Z' },
    ],
    rules: [
      { id: 'BR-001', name: 'Cart item limit', description: 'Cart cannot exceed 100 items', entity: 'cart', condition: 'items.length <= 100', constraint: 'max_items', severity: 'error' },
      { id: 'BR-002', name: 'Cart expiration', description: 'Carts expire after 7 days of inactivity', entity: 'cart', condition: 'updated_at + 7 days', constraint: 'expiration', severity: 'warning' },
    ],
    relationships: [
      { sourceEntity: 'cart', targetEntity: 'customer', relationshipType: 'belongs_to', description: 'Cart belongs to a customer', required: true },
      { sourceEntity: 'cart', targetEntity: 'cart_item', relationshipType: 'has_many', description: 'Cart has many items', required: false },
    ],
    edgeCases: [
      'Empty cart checkout attempt',
      'Cart with out-of-stock items',
      'Cart total exceeds payment limit',
      'Concurrent cart modifications',
      'Cart with expired promotions',
    ],
    testScenarios: [
      'Add item to empty cart',
      'Remove last item from cart',
      'Update quantity to zero',
      'Apply coupon to cart',
      'Convert guest cart to logged-in user',
    ],
  },
  order: {
    name: 'order',
    description: 'Customer order with shipping and payment info',
    fields: [
      { name: 'order_id', type: 'UUID', description: 'Unique order identifier', required: true, validations: ['format:uuid'], example: 'ORD-2025-123456' },
      { name: 'customer_id', type: 'UUID', description: 'Customer reference', required: true, validations: ['format:uuid'], example: 'USR-4829173' },
      { name: 'status', type: 'ENUM', description: 'Order status', required: true, validations: ['values:pending,confirmed,processing,shipped,delivered,cancelled'], example: 'pending' },
      { name: 'total_amount', type: 'DECIMAL', description: 'Order total including tax/shipping', required: true, validations: ['min:0'], example: '299.99' },
      { name: 'shipping_address', type: 'ADDRESS', description: 'Delivery address', required: true, validations: [], example: '123 Main St, City, ST 12345' },
      { name: 'billing_address', type: 'ADDRESS', description: 'Billing address', required: true, validations: [], example: '123 Main St, City, ST 12345' },
      { name: 'payment_method', type: 'STRING', description: 'Payment method used', required: true, validations: [], example: 'credit_card' },
      { name: 'created_at', type: 'DATETIME', description: 'Order creation time', required: true, validations: [], example: '2025-01-15T10:30:00Z' },
    ],
    rules: [
      { id: 'BR-010', name: 'Order minimum', description: 'Order must have at least one item', entity: 'order', condition: 'items.length >= 1', constraint: 'min_items', severity: 'error' },
      { id: 'BR-011', name: 'Valid shipping address', description: 'Shipping address must be complete', entity: 'order', condition: 'shipping_address is valid', constraint: 'required_fields', severity: 'error' },
    ],
    relationships: [
      { sourceEntity: 'order', targetEntity: 'customer', relationshipType: 'belongs_to', description: 'Order belongs to a customer', required: true },
      { sourceEntity: 'order', targetEntity: 'order_item', relationshipType: 'has_many', description: 'Order has many items', required: true },
      { sourceEntity: 'order', targetEntity: 'payment', relationshipType: 'has_one', description: 'Order has one payment', required: true },
      { sourceEntity: 'order', targetEntity: 'shipment', relationshipType: 'has_many', description: 'Order may have multiple shipments', required: false },
    ],
    edgeCases: [
      'Order with mixed shipping destinations',
      'Order cancellation after shipment',
      'Partial refund processing',
      'Order with backordered items',
      'International shipping restrictions',
    ],
    testScenarios: [
      'Place order with valid payment',
      'Cancel order before processing',
      'Track order shipment',
      'Request order return',
      'Reorder from order history',
    ],
  },
};

const MOCK_WORKFLOW_DETAILS: Record<string, Workflow> = {
  checkout: {
    name: 'checkout',
    description: 'Complete checkout flow from cart to order confirmation',
    steps: [
      { order: 1, name: 'Review Cart', description: 'Customer reviews cart contents', entity: 'cart', action: 'validate', validations: ['cart not empty', 'items in stock'], possibleOutcomes: ['proceed', 'update cart', 'abandon'] },
      { order: 2, name: 'Enter Shipping', description: 'Customer enters shipping address', entity: 'address', action: 'create/select', validations: ['valid address format', 'serviceable area'], possibleOutcomes: ['proceed', 'edit address'] },
      { order: 3, name: 'Select Shipping Method', description: 'Customer selects shipping speed', entity: 'shipment', action: 'select', validations: ['method available', 'delivery date valid'], possibleOutcomes: ['proceed', 'change method'] },
      { order: 4, name: 'Enter Payment', description: 'Customer enters payment information', entity: 'payment', action: 'create/select', validations: ['valid payment method', 'not expired'], possibleOutcomes: ['proceed', 'try different method'] },
      { order: 5, name: 'Apply Promotions', description: 'Apply coupon codes and promotions', entity: 'coupon', action: 'apply', validations: ['coupon valid', 'not expired', 'applicable'], possibleOutcomes: ['discount applied', 'coupon rejected'] },
      { order: 6, name: 'Review Order', description: 'Final review before placement', entity: 'order', action: 'preview', validations: ['all required fields', 'totals correct'], possibleOutcomes: ['place order', 'edit order'] },
      { order: 7, name: 'Process Payment', description: 'Authorize and capture payment', entity: 'payment', action: 'process', validations: ['sufficient funds', 'fraud check passed'], possibleOutcomes: ['success', 'declined', 'requires verification'] },
      { order: 8, name: 'Confirm Order', description: 'Order confirmation and notification', entity: 'order', action: 'confirm', validations: ['payment successful'], possibleOutcomes: ['confirmation sent', 'notification failed'] },
    ],
    involvedEntities: ['cart', 'order', 'payment', 'shipment', 'address', 'coupon'],
    rules: [
      { id: 'WF-001', name: 'Payment required', description: 'Payment must be processed before order confirmation', entity: 'order', condition: 'payment.status = success', constraint: 'prerequisite', severity: 'error' },
    ],
    edgeCases: [
      'Payment declined during checkout',
      'Item goes out of stock during checkout',
      'Session timeout during checkout',
      'Price change during checkout',
      'Coupon expires during checkout',
    ],
    testScenarios: [
      'Complete checkout with credit card',
      'Complete checkout with PayPal',
      'Checkout with saved address',
      'Checkout with new address',
      'Checkout with coupon code',
    ],
  },
  return: {
    name: 'return',
    description: 'Product return and refund processing',
    steps: [
      { order: 1, name: 'Initiate Return', description: 'Customer requests return', entity: 'return', action: 'create', validations: ['within return window', 'item eligible'], possibleOutcomes: ['approved', 'denied'] },
      { order: 2, name: 'Generate Label', description: 'Create return shipping label', entity: 'shipment', action: 'create', validations: ['address valid'], possibleOutcomes: ['label created', 'error'] },
      { order: 3, name: 'Ship Item', description: 'Customer ships item back', entity: 'shipment', action: 'update', validations: ['tracking provided'], possibleOutcomes: ['in transit', 'not shipped'] },
      { order: 4, name: 'Receive Item', description: 'Warehouse receives returned item', entity: 'return', action: 'receive', validations: ['item matches', 'condition acceptable'], possibleOutcomes: ['accepted', 'rejected'] },
      { order: 5, name: 'Process Refund', description: 'Issue refund to customer', entity: 'payment', action: 'refund', validations: ['return accepted'], possibleOutcomes: ['refund issued', 'partial refund', 'store credit'] },
      { order: 6, name: 'Update Inventory', description: 'Return item to inventory if resellable', entity: 'inventory', action: 'update', validations: ['item resellable'], possibleOutcomes: ['inventory updated', 'item disposed'] },
    ],
    involvedEntities: ['order', 'return', 'payment', 'inventory', 'shipment'],
    rules: [
      { id: 'WF-010', name: 'Return window', description: 'Returns must be initiated within 30 days', entity: 'return', condition: 'order.created_at + 30 days > now', constraint: 'time_limit', severity: 'error' },
    ],
    edgeCases: [
      'Return after return window',
      'Item damaged during return shipping',
      'Partial order return',
      'Return without receipt',
      'Exchange instead of refund',
    ],
    testScenarios: [
      'Return within 30 days',
      'Return with original payment',
      'Return for store credit',
      'Return multiple items',
      'Return gift item',
    ],
  },
};

const MOCK_KNOWLEDGE_ITEMS: KnowledgeItem[] = [
  { id: 'KI-001', category: 'business_rules', title: 'Cart Expiration Policy', content: 'Shopping carts expire after 7 days of inactivity. Expired carts are archived but can be restored within 30 days.', relevanceScore: 0.95, metadata: { entity: 'cart', lastUpdated: '2025-01-15' } },
  { id: 'KI-002', category: 'business_rules', title: 'Return Policy', content: 'Returns are accepted within 30 days of delivery for most items. Electronics have a 15-day return window. Final sale items cannot be returned.', relevanceScore: 0.92, metadata: { entity: 'return', lastUpdated: '2025-01-10' } },
  { id: 'KI-003', category: 'edge_cases', title: 'Payment Decline Handling', content: 'When payment is declined, show user-friendly error message without exposing bank response codes. Allow 3 retry attempts before locking checkout.', relevanceScore: 0.88, metadata: { entity: 'payment', workflow: 'checkout' } },
  { id: 'KI-004', category: 'test_patterns', title: 'Inventory Edge Cases', content: 'Test scenarios: concurrent purchases of last item, negative inventory prevention, backorder handling, warehouse transfer timing.', relevanceScore: 0.85, metadata: { entity: 'inventory' } },
  { id: 'KI-005', category: 'business_rules', title: 'Shipping Restrictions', content: 'Certain products cannot be shipped to PO boxes (oversized items). Hazardous materials have carrier restrictions. International shipping requires customs declaration.', relevanceScore: 0.82, metadata: { entity: 'shipment' } },
];

const MOCK_EDGE_CASES: EdgeCase[] = [
  { id: 'EC-001', name: 'Empty Cart Checkout', description: 'User attempts to checkout with an empty cart', category: 'validation', entity: 'cart', workflow: 'checkout', testApproach: 'Verify error message and prevention of checkout progression', exampleData: { cart_items: '[]' }, expectedBehavior: 'Show error: "Your cart is empty. Add items to continue."', severity: 'high' },
  { id: 'EC-002', name: 'Out of Stock During Checkout', description: 'Item goes out of stock while user is in checkout flow', category: 'concurrency', entity: 'cart', workflow: 'checkout', testApproach: 'Simulate inventory depletion mid-checkout', exampleData: { initial_stock: '1', concurrent_purchase: 'true' }, expectedBehavior: 'Notify user and offer alternatives', severity: 'high' },
  { id: 'EC-003', name: 'Payment Timeout', description: 'Payment gateway times out during processing', category: 'integration', entity: 'payment', workflow: 'checkout', testApproach: 'Mock payment gateway timeout response', exampleData: { timeout_ms: '30000' }, expectedBehavior: 'Show retry option, do not create duplicate charges', severity: 'critical' },
  { id: 'EC-004', name: 'Expired Coupon', description: 'Coupon expires between cart and checkout', category: 'timing', entity: 'coupon', workflow: 'checkout', testApproach: 'Apply coupon, wait for expiration, proceed to checkout', exampleData: { coupon_code: 'SAVE20', expiry: '2025-01-01' }, expectedBehavior: 'Remove coupon and notify user', severity: 'medium' },
];

// ============= Client Export =============

export const ecommerceClient = {
  async getDomainContext(request: DomainContextRequest): Promise<DomainContextResponse> {
    if (isMockMode()) {
      await new Promise(resolve => setTimeout(resolve, 300 + Math.random() * 200));

      const entity = MOCK_ENTITY_DETAILS[request.entity] || MOCK_ENTITY_DETAILS['cart'];
      return {
        requestId: request.requestId || `REQ-${Date.now()}`,
        context: `Domain context for ${request.entity} in ${request.workflow || 'general'} workflow`,
        rules: entity.rules,
        relationships: entity.relationships,
        edgeCases: entity.edgeCases,
        metadata: { entity: request.entity, workflow: request.workflow || '' },
      };
    }

    return grpcWebUnaryCall<DomainContextRequest, DomainContextResponse>(
      GRPC_WEB_URL,
      'ecommerce.domain.v1.EcommerceDomainService/GetDomainContext',
      request,
      DomainContextRequestMsg.encode,
      DomainContextResponseMsg.decode
    );
  },

  async queryKnowledge(request: KnowledgeRequest): Promise<KnowledgeResponse> {
    if (isMockMode()) {
      await new Promise(resolve => setTimeout(resolve, 400 + Math.random() * 300));

      const filteredItems = MOCK_KNOWLEDGE_ITEMS.filter(item => {
        if (request.categories.length === 0) return true;
        return request.categories.includes(item.category);
      }).slice(0, request.maxResults || 10);

      return {
        requestId: request.requestId || `REQ-${Date.now()}`,
        items: filteredItems,
        summary: `Found ${filteredItems.length} knowledge items matching "${request.query}"`,
      };
    }

    return grpcWebUnaryCall<KnowledgeRequest, KnowledgeResponse>(
      GRPC_WEB_URL,
      'ecommerce.domain.v1.EcommerceDomainService/QueryKnowledge',
      request,
      KnowledgeRequestMsg.encode,
      KnowledgeResponseMsg.decode
    );
  },

  async getEntity(request: EntityRequest): Promise<EntityResponse> {
    if (isMockMode()) {
      await new Promise(resolve => setTimeout(resolve, 200 + Math.random() * 100));

      const entity = MOCK_ENTITY_DETAILS[request.entityName];
      if (!entity) {
        // Generate a basic entity structure for unknown entities
        const summary = MOCK_ENTITIES.find(e => e.name === request.entityName);
        return {
          entity: {
            name: request.entityName,
            description: summary?.description || `${request.entityName} entity`,
            fields: [],
            rules: [],
            relationships: [],
            edgeCases: [],
            testScenarios: [],
          },
        };
      }

      return { entity };
    }

    return grpcWebUnaryCall<EntityRequest, EntityResponse>(
      GRPC_WEB_URL,
      'ecommerce.domain.v1.EcommerceDomainService/GetEntity',
      request,
      EntityRequestMsg.encode,
      EntityResponseMsg.decode
    );
  },

  async getWorkflow(request: WorkflowRequest): Promise<WorkflowResponse> {
    if (isMockMode()) {
      await new Promise(resolve => setTimeout(resolve, 200 + Math.random() * 100));

      const workflow = MOCK_WORKFLOW_DETAILS[request.workflowName];
      if (!workflow) {
        const summary = MOCK_WORKFLOWS.find(w => w.name === request.workflowName);
        return {
          workflow: {
            name: request.workflowName,
            description: summary?.description || `${request.workflowName} workflow`,
            steps: [],
            involvedEntities: summary?.involvedEntities || [],
            rules: [],
            edgeCases: [],
            testScenarios: [],
          },
        };
      }

      return { workflow };
    }

    return grpcWebUnaryCall<WorkflowRequest, WorkflowResponse>(
      GRPC_WEB_URL,
      'ecommerce.domain.v1.EcommerceDomainService/GetWorkflow',
      request,
      WorkflowRequestMsg.encode,
      WorkflowResponseMsg.decode
    );
  },

  async listEntities(request: ListEntitiesRequest): Promise<ListEntitiesResponse> {
    if (isMockMode()) {
      await new Promise(resolve => setTimeout(resolve, 200 + Math.random() * 100));

      const entities = request.category
        ? MOCK_ENTITIES.filter(e => e.category === request.category)
        : MOCK_ENTITIES;

      return { entities };
    }

    return grpcWebUnaryCall<ListEntitiesRequest, ListEntitiesResponse>(
      GRPC_WEB_URL,
      'ecommerce.domain.v1.EcommerceDomainService/ListEntities',
      request,
      ListEntitiesRequestMsg.encode,
      ListEntitiesResponseMsg.decode
    );
  },

  async listWorkflows(request: ListWorkflowsRequest): Promise<ListWorkflowsResponse> {
    if (isMockMode()) {
      await new Promise(resolve => setTimeout(resolve, 150 + Math.random() * 100));

      return { workflows: MOCK_WORKFLOWS };
    }

    return grpcWebUnaryCall<ListWorkflowsRequest, ListWorkflowsResponse>(
      GRPC_WEB_URL,
      'ecommerce.domain.v1.EcommerceDomainService/ListWorkflows',
      request,
      ListWorkflowsRequestMsg.encode,
      ListWorkflowsResponseMsg.decode
    );
  },

  async getEdgeCases(request: EdgeCasesRequest): Promise<EdgeCasesResponse> {
    if (isMockMode()) {
      await new Promise(resolve => setTimeout(resolve, 200 + Math.random() * 100));

      let edgeCases = MOCK_EDGE_CASES;

      if (request.entity) {
        edgeCases = edgeCases.filter(ec => ec.entity === request.entity);
      }
      if (request.workflow) {
        edgeCases = edgeCases.filter(ec => ec.workflow === request.workflow);
      }
      if (request.category) {
        edgeCases = edgeCases.filter(ec => ec.category === request.category);
      }

      return { edgeCases };
    }

    return grpcWebUnaryCall<EdgeCasesRequest, EdgeCasesResponse>(
      GRPC_WEB_URL,
      'ecommerce.domain.v1.EcommerceDomainService/GetEdgeCases',
      request,
      EdgeCasesRequestMsg.encode,
      EdgeCasesResponseMsg.decode
    );
  },

  async generateTestData(request: GenerateTestDataRequest): Promise<GenerateTestDataResponse> {
    if (isMockMode()) {
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));

      const mockData = [];
      for (let i = 0; i < request.count; i++) {
        mockData.push({
          _index: i,
          _entity: request.entity,
          id: `${request.entity.toUpperCase()}-${Date.now()}-${i}`,
          generated_at: new Date().toISOString(),
        });
      }

      return {
        requestId: request.requestId || `REQ-${Date.now()}`,
        success: true,
        data: JSON.stringify(mockData, null, 2),
        recordCount: request.count,
        metadata: {
          generationPath: 'mock',
          llmTokensUsed: 0,
          generationTimeMs: 500 + Math.random() * 500,
          coherenceScore: 0.95,
          domainContextUsed: `Generated with ${request.entity} domain context`,
          scenarioCounts: { [request.entity]: request.count },
        },
        error: '',
      };
    }

    return grpcWebUnaryCall<GenerateTestDataRequest, GenerateTestDataResponse>(
      GRPC_WEB_URL,
      'ecommerce.domain.v1.EcommerceDomainService/GenerateTestData',
      request,
      GenerateTestDataRequestMsg.encode,
      GenerateTestDataResponseMsg.decode
    );
  },

  async healthCheck(): Promise<HealthCheckResponse> {
    if (isMockMode()) {
      return {
        status: 'healthy',
        components: {
          grpc: 'healthy',
          knowledge_base: 'healthy',
          test_data_agent: 'healthy',
        },
      };
    }

    return grpcWebUnaryCall<Record<string, never>, HealthCheckResponse>(
      GRPC_WEB_URL,
      'ecommerce.domain.v1.EcommerceDomainService/HealthCheck',
      {},
      HealthCheckRequestMsg.encode,
      HealthCheckResponseMsg.decode
    );
  },
};

// Re-export types for consumers
export type {
  DomainContextRequest,
  DomainContextResponse,
  KnowledgeRequest,
  KnowledgeResponse,
  EntityRequest,
  EntityResponse,
  WorkflowRequest,
  WorkflowResponse,
  ListEntitiesRequest,
  ListEntitiesResponse,
  ListWorkflowsRequest,
  ListWorkflowsResponse,
  EdgeCasesRequest,
  EdgeCasesResponse,
  GenerateTestDataRequest,
  GenerateTestDataResponse,
  HealthCheckResponse,
  Entity,
  EntitySummary,
  EntityField,
  Workflow,
  WorkflowSummary,
  WorkflowStep,
  BusinessRule,
  EntityRelationship,
  KnowledgeItem,
  EdgeCase,
  GenerationMetadata,
};

// Re-export enums
export { GenerationMethod };

export default ecommerceClient;
