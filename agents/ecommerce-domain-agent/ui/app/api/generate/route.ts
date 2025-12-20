import { NextRequest, NextResponse } from "next/server";

// This endpoint will communicate with the eCommerce Domain Agent backend
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Call the eCommerce Domain Agent backend API
    const backendUrl = process.env.BACKEND_URL || "http://localhost:8082";

    const response = await fetch(`${backendUrl}/api/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        entity: body.entity,
        count: body.count || 10,
        workflow: body.workflow,
        scenario: body.scenario,
        context: body.context,
        scenarios: body.scenarios,
        output_format: body.outputFormat || "JSON",
        include_edge_cases: body.includeEdgeCases || false,
        production_like: body.productionLike || true,
        use_cache: body.useCache !== false,
        generation_method: body.generationMethod || "HYBRID",
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Backend error:", errorText);

      // If backend is not available, return mock data for demo
      if (response.status === 404 || response.status === 502) {
        return NextResponse.json({
          success: true,
          data: generateMockData(body.entity, body.count || 10),
          metadata: {
            generated_at: new Date().toISOString(),
            is_mock: true,
            message: "Using mock data - backend service not available"
          }
        });
      }

      throw new Error(`Backend returned ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error("Generate API error:", error);

    // Return mock data if there's an error
    const body = await request.json().catch(() => ({ entity: "cart", count: 10 }));

    return NextResponse.json({
      success: true,
      data: generateMockData(body.entity, body.count || 10),
      metadata: {
        generated_at: new Date().toISOString(),
        is_mock: true,
        message: "Using mock data due to connection error"
      }
    });
  }
}

// Mock data generator for demonstration
function generateMockData(entity: string, count: number): string {
  const data = [];

  for (let i = 1; i <= Math.min(count, 100); i++) {
    switch (entity) {
      case "cart":
      case "shopping_cart":
        data.push({
          id: `cart_${String(i).padStart(3, '0')}`,
          userId: `user_${Math.floor(Math.random() * 1000)}`,
          sessionId: `session_${Math.random().toString(36).substr(2, 9)}`,
          items: [
            {
              productId: `prod_${Math.floor(Math.random() * 100)}`,
              quantity: Math.floor(Math.random() * 5) + 1,
              price: parseFloat((Math.random() * 100 + 10).toFixed(2))
            }
          ],
          subtotal: parseFloat((Math.random() * 500 + 50).toFixed(2)),
          tax: parseFloat((Math.random() * 50 + 5).toFixed(2)),
          total: parseFloat((Math.random() * 550 + 55).toFixed(2)),
          createdAt: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
          updatedAt: new Date().toISOString(),
          status: ["active", "abandoned", "converted"][Math.floor(Math.random() * 3)]
        });
        break;

      case "order":
        data.push({
          id: `order_${String(i).padStart(3, '0')}`,
          orderNumber: `ORD-${Date.now()}-${String(i).padStart(3, '0')}`,
          customerId: `customer_${Math.floor(Math.random() * 1000)}`,
          items: [
            {
              productId: `prod_${Math.floor(Math.random() * 100)}`,
              quantity: Math.floor(Math.random() * 3) + 1,
              price: parseFloat((Math.random() * 100 + 10).toFixed(2))
            }
          ],
          subtotal: parseFloat((Math.random() * 500 + 50).toFixed(2)),
          tax: parseFloat((Math.random() * 50 + 5).toFixed(2)),
          shipping: parseFloat((Math.random() * 20 + 5).toFixed(2)),
          total: parseFloat((Math.random() * 570 + 60).toFixed(2)),
          status: ["pending", "processing", "shipped", "delivered"][Math.floor(Math.random() * 4)],
          paymentStatus: ["pending", "paid", "failed"][Math.floor(Math.random() * 3)],
          createdAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
        });
        break;

      case "payment":
        data.push({
          id: `payment_${String(i).padStart(3, '0')}`,
          orderId: `order_${Math.floor(Math.random() * 1000)}`,
          amount: parseFloat((Math.random() * 1000 + 10).toFixed(2)),
          currency: "USD",
          method: ["credit_card", "debit_card", "paypal", "apple_pay"][Math.floor(Math.random() * 4)],
          status: ["pending", "authorized", "captured", "failed"][Math.floor(Math.random() * 4)],
          gateway: ["stripe", "paypal", "square"][Math.floor(Math.random() * 3)],
          transactionId: `txn_${Math.random().toString(36).substr(2, 16)}`,
          processedAt: new Date().toISOString(),
        });
        break;

      case "customer":
        data.push({
          id: `customer_${String(i).padStart(3, '0')}`,
          email: `customer${i}@example.com`,
          firstName: ["John", "Jane", "Bob", "Alice", "Charlie"][Math.floor(Math.random() * 5)],
          lastName: ["Smith", "Johnson", "Williams", "Brown", "Jones"][Math.floor(Math.random() * 5)],
          phone: `+1${Math.floor(Math.random() * 9000000000 + 1000000000)}`,
          dateOfBirth: new Date(1970 + Math.floor(Math.random() * 40), Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1).toISOString().split('T')[0],
          loyaltyPoints: Math.floor(Math.random() * 10000),
          tier: ["bronze", "silver", "gold", "platinum"][Math.floor(Math.random() * 4)],
          createdAt: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString(),
        });
        break;

      case "product":
        data.push({
          id: `product_${String(i).padStart(3, '0')}`,
          sku: `SKU-${Math.random().toString(36).substr(2, 8).toUpperCase()}`,
          name: `Product ${i}`,
          description: `This is the description for product ${i}`,
          price: parseFloat((Math.random() * 500 + 10).toFixed(2)),
          category: ["Electronics", "Clothing", "Home", "Books", "Sports"][Math.floor(Math.random() * 5)],
          brand: ["Brand A", "Brand B", "Brand C"][Math.floor(Math.random() * 3)],
          inStock: Math.random() > 0.2,
          stockQuantity: Math.floor(Math.random() * 1000),
          createdAt: new Date(Date.now() - Math.random() * 180 * 24 * 60 * 60 * 1000).toISOString(),
        });
        break;

      default:
        // Generic entity data
        data.push({
          id: `${entity}_${String(i).padStart(3, '0')}`,
          name: `${entity.charAt(0).toUpperCase() + entity.slice(1)} ${i}`,
          description: `Sample ${entity} record ${i}`,
          status: "active",
          value: Math.floor(Math.random() * 1000),
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        });
    }
  }

  return JSON.stringify(data, null, 2);
}