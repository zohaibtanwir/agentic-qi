"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, Loader2, Copy, Check, ArrowRight, Database, Brain, Sparkles } from "lucide-react";

export default function GenerateTestDataPage() {
  const [entity, setEntity] = useState("cart");
  const [count, setCount] = useState(10);
  const [workflow, setWorkflow] = useState("");
  const [scenario, setScenario] = useState("happy_path");
  const [outputFormat, setOutputFormat] = useState<"JSON" | "CSV" | "SQL">("JSON");
  const [includeEdgeCases, setIncludeEdgeCases] = useState(false);
  const [productionLike, setProductionLike] = useState(true);
  const [context, setContext] = useState("");
  const [generationMethod, setGenerationMethod] = useState("HYBRID");

  const [loading, setLoading] = useState(false);
  const [generatedData, setGeneratedData] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [copied, setCopied] = useState(false);
  const [orchestrationSteps, setOrchestrationSteps] = useState<string[]>([]);

  const handleGenerate = async () => {
    setLoading(true);
    setError("");
    setGeneratedData("");
    setOrchestrationSteps([]);

    try {
      // Show orchestration steps
      const steps = [
        "Analyzing request for entity: " + entity,
        "Enriching with eCommerce domain knowledge...",
        "Applying business rules and constraints...",
        "Determining generation strategy...",
        entity === "user" || entity === "product" || entity === "address" || entity === "credit_card"
          ? "Using Test Data Agent's predefined entity schema"
          : "Building custom schema for domain entity",
        "Calling Test Data Agent with enriched context...",
        "Validating generated data...",
        "Generation complete!"
      ];

      // Show orchestration steps progressively (but faster)
      for (let i = 0; i < steps.length - 1; i++) {
        setOrchestrationSteps(prev => [...prev, steps[i]]);
        await new Promise(resolve => setTimeout(resolve, 200));
      }

      // Call the actual API
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          entity,
          count,
          workflow,
          scenario,
          context,
          outputFormat,
          includeEdgeCases,
          productionLike,
          generationMethod,
        }),
      });

      if (!response.ok) {
        throw new Error(`Generation failed: ${response.statusText}`);
      }

      const result = await response.json();

      // Show final step
      setOrchestrationSteps(prev => [...prev, steps[steps.length - 1]]);

      if (result.success) {
        // If data is already stringified, use it directly; otherwise stringify it
        const dataToDisplay = typeof result.data === 'string'
          ? result.data
          : JSON.stringify(result.data, null, 2);
        setGeneratedData(dataToDisplay);

        // Show a message if using mock data
        if (result.metadata?.is_mock) {
          setError(`Note: ${result.metadata.message || "Using mock data for demonstration"}`);
        }
      } else {
        setError(result.error || "Failed to generate test data");
      }
    } catch (err) {
      console.error("Generation error:", err);
      setError(`Failed to orchestrate test data generation: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generatedData);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([generatedData], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `test-data-${entity}-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="border-b pb-6">
        <h1 className="text-3xl font-bold text-gray-900">Test Data Orchestration</h1>
        <p className="text-gray-600 mt-2">
          eCommerce Domain Agent enriches your requests with domain knowledge before calling Test Data Agent
        </p>
      </div>

      {/* Orchestration Flow Visualization */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <CardHeader>
          <CardTitle className="text-blue-900">How eCommerce Domain Agent Orchestrates</CardTitle>
          <CardDescription className="text-blue-700">
            The eCommerce Domain Agent enriches your request and coordinates with Test Data Agent
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between space-x-4">
            <div className="flex-1 text-center">
              <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-2 shadow-md">
                <Brain className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="font-semibold text-sm">eCommerce Domain Agent</h3>
              <p className="text-xs text-gray-600 mt-1">Enriches with context</p>
            </div>

            <ArrowRight className="h-6 w-6 text-gray-400" />

            <div className="flex-1 text-center">
              <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-2 shadow-md">
                <Database className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="font-semibold text-sm">Knowledge Base</h3>
              <p className="text-xs text-gray-600 mt-1">Business rules & patterns</p>
            </div>

            <ArrowRight className="h-6 w-6 text-gray-400" />

            <div className="flex-1 text-center">
              <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-2 shadow-md">
                <Sparkles className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="font-semibold text-sm">Test Data Agent</h3>
              <p className="text-xs text-gray-600 mt-1">Generates test data</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Configuration Form */}
        <Card>
          <CardHeader>
            <CardTitle>Request Configuration</CardTitle>
            <CardDescription>
              Configure what test data you need - eCommerce Domain Agent will handle the rest
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Entity Selection */}
            <div>
              <label className="block text-sm font-medium mb-2">Entity</label>
              <select
                value={entity}
                onChange={(e) => setEntity(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-macys-red"
              >
                <optgroup label="🛒 Shopping & Cart">
                  <option value="cart">Shopping Cart</option>
                  <option value="cart_item">Cart Item</option>
                  <option value="saved_cart">Saved Cart</option>
                </optgroup>
                <optgroup label="📦 Orders">
                  <option value="order">Order</option>
                  <option value="order_item">Order Item</option>
                  <option value="order_status">Order Status</option>
                  <option value="order_history">Order History</option>
                </optgroup>
                <optgroup label="💳 Payments">
                  <option value="payment">Payment</option>
                  <option value="payment_transaction">Payment Transaction</option>
                  <option value="refund">Refund</option>
                  <option value="payment_authorization">Payment Authorization</option>
                </optgroup>
                <optgroup label="📊 Inventory">
                  <option value="inventory">Inventory</option>
                  <option value="stock">Stock</option>
                  <option value="inventory_adjustment">Inventory Adjustment</option>
                  <option value="stock_alert">Stock Alert</option>
                </optgroup>
                <optgroup label="👤 Customer">
                  <option value="customer">Customer</option>
                  <option value="customer_segment">Customer Segment</option>
                  <option value="loyalty_member">Loyalty Member</option>
                  <option value="customer_preferences">Customer Preferences</option>
                </optgroup>
                <optgroup label="🚚 Shipping & Fulfillment">
                  <option value="shipping">Shipping</option>
                  <option value="shipment">Shipment</option>
                  <option value="tracking">Tracking</option>
                  <option value="delivery">Delivery</option>
                  <option value="fulfillment">Fulfillment</option>
                </optgroup>
                <optgroup label="🏷️ Promotions">
                  <option value="discount">Discount</option>
                  <option value="coupon">Coupon</option>
                  <option value="promotion">Promotion</option>
                  <option value="price_adjustment">Price Adjustment</option>
                  <option value="deal">Deal</option>
                </optgroup>
                <optgroup label="🛍️ Product Management">
                  <option value="category">Category</option>
                  <option value="brand">Brand</option>
                  <option value="product_variant">Product Variant</option>
                  <option value="product_bundle">Product Bundle</option>
                </optgroup>
                <optgroup label="⭐ Reviews & Ratings">
                  <option value="review">Review</option>
                  <option value="rating">Rating</option>
                  <option value="product_feedback">Product Feedback</option>
                  <option value="merchant_review">Merchant Review</option>
                </optgroup>
                <optgroup label="❤️ Wishlist & Favorites">
                  <option value="wishlist">Wishlist</option>
                  <option value="favorites">Favorites</option>
                  <option value="save_for_later">Save for Later</option>
                  <option value="gift_registry">Gift Registry</option>
                </optgroup>
                <optgroup label="↩️ Returns & Exchanges">
                  <option value="return">Return</option>
                  <option value="exchange">Exchange</option>
                  <option value="rma">RMA</option>
                  <option value="return_label">Return Label</option>
                </optgroup>
                <optgroup label="📈 Analytics">
                  <option value="analytics_event">Analytics Event</option>
                  <option value="page_view">Page View</option>
                  <option value="click_event">Click Event</option>
                  <option value="conversion">Conversion</option>
                </optgroup>
                <optgroup label="📧 Communication">
                  <option value="notification">Notification</option>
                  <option value="email_campaign">Email Campaign</option>
                  <option value="sms_alert">SMS Alert</option>
                  <option value="push_notification">Push Notification</option>
                </optgroup>
                <optgroup label="🔄 Subscription">
                  <option value="subscription">Subscription</option>
                  <option value="recurring_order">Recurring Order</option>
                  <option value="subscription_plan">Subscription Plan</option>
                </optgroup>
                <optgroup label="🎁 Gift Cards & Credit">
                  <option value="gift_card">Gift Card</option>
                  <option value="store_credit">Store Credit</option>
                  <option value="reward_points">Reward Points</option>
                  <option value="voucher">Voucher</option>
                </optgroup>
                <optgroup label="🔍 Search & Recommendations">
                  <option value="search_query">Search Query</option>
                  <option value="recommendation">Recommendation</option>
                  <option value="personalization">Personalization</option>
                  <option value="trending_item">Trending Item</option>
                </optgroup>
                <optgroup label="🔒 Security & Fraud">
                  <option value="fraud_check">Fraud Check</option>
                  <option value="security_event">Security Event</option>
                  <option value="risk_assessment">Risk Assessment</option>
                  <option value="blocked_transaction">Blocked Transaction</option>
                </optgroup>
                <optgroup label="🆘 Support">
                  <option value="support_ticket">Support Ticket</option>
                  <option value="chat_session">Chat Session</option>
                  <option value="complaint">Complaint</option>
                  <option value="inquiry">Inquiry</option>
                </optgroup>
                <optgroup label="--- PREDEFINED ENTITIES (Test Data Agent) ---">
                  <option value="user">User</option>
                  <option value="person">Person</option>
                  <option value="customer_profile">Customer Profile</option>
                  <option value="email">Email</option>
                  <option value="phone">Phone</option>
                  <option value="address">Address</option>
                  <option value="credit_card">Credit Card</option>
                  <option value="bank_account">Bank Account</option>
                  <option value="payment_method">Payment Method</option>
                  <option value="company">Company</option>
                  <option value="merchant">Merchant</option>
                  <option value="vendor">Vendor</option>
                  <option value="product">Product</option>
                  <option value="sku">SKU</option>
                  <option value="item">Item</option>
                  <option value="location">Location</option>
                  <option value="store">Store</option>
                  <option value="warehouse">Warehouse</option>
                  <option value="date">Date</option>
                  <option value="timestamp">Timestamp</option>
                  <option value="schedule">Schedule</option>
                  <option value="transaction">Transaction</option>
                  <option value="invoice">Invoice</option>
                  <option value="receipt">Receipt</option>
                </optgroup>
              </select>
            </div>

            {/* Count */}
            <div>
              <label className="block text-sm font-medium mb-2">Number of Records</label>
              <input
                type="number"
                min="1"
                max="1000"
                value={count}
                onChange={(e) => setCount(parseInt(e.target.value) || 1)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-macys-red"
              />
            </div>

            {/* Workflow */}
            <div>
              <label className="block text-sm font-medium mb-2">Workflow Context (Optional)</label>
              <select
                value={workflow}
                onChange={(e) => setWorkflow(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-macys-red"
              >
                <option value="">None</option>
                <option value="checkout">Checkout Flow</option>
                <option value="return">Return Flow</option>
                <option value="browsing">Product Browsing</option>
                <option value="registration">User Registration</option>
              </select>
            </div>

            {/* Scenario */}
            <div>
              <label className="block text-sm font-medium mb-2">Scenario</label>
              <select
                value={scenario}
                onChange={(e) => setScenario(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-macys-red"
              >
                <option value="happy_path">Happy Path</option>
                <option value="edge_cases">Edge Cases</option>
                <option value="error_conditions">Error Conditions</option>
                <option value="stress_test">Stress Test</option>
                <option value="seasonal">Seasonal (Holiday/Sale)</option>
              </select>
            </div>

            {/* Generation Method */}
            <div>
              <label className="block text-sm font-medium mb-2">Generation Method</label>
              <select
                value={generationMethod}
                onChange={(e) => setGenerationMethod(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-macys-red"
              >
                <option value="TRADITIONAL">Traditional (Rule-based)</option>
                <option value="LLM">LLM-Powered (AI Generated)</option>
                <option value="RAG">RAG (Knowledge-based)</option>
                <option value="HYBRID">Hybrid (Best of All)</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">
                {generationMethod === "TRADITIONAL" && "Fast, deterministic generation using predefined patterns"}
                {generationMethod === "LLM" && "AI-powered generation for creative and realistic data"}
                {generationMethod === "RAG" && "Uses domain knowledge base for contextually accurate data"}
                {generationMethod === "HYBRID" && "Intelligently combines all methods for optimal results"}
              </p>
            </div>

            {/* Output Format */}
            <div>
              <label className="block text-sm font-medium mb-2">Output Format</label>
              <div className="flex space-x-3">
                {(["JSON", "CSV", "SQL"] as const).map((format) => (
                  <label key={format} className="flex items-center">
                    <input
                      type="radio"
                      value={format}
                      checked={outputFormat === format}
                      onChange={() => setOutputFormat(format)}
                      className="mr-2 text-macys-red focus:ring-macys-red"
                    />
                    {format}
                  </label>
                ))}
              </div>
            </div>

            {/* Options */}
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeEdgeCases}
                  onChange={(e) => setIncludeEdgeCases(e.target.checked)}
                  className="mr-2 text-macys-red focus:ring-macys-red"
                />
                Include Edge Cases
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={productionLike}
                  onChange={(e) => setProductionLike(e.target.checked)}
                  className="mr-2 text-macys-red focus:ring-macys-red"
                />
                Production-like Distribution
              </label>
            </div>

            {/* Additional Context */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Additional Context (Optional)
              </label>
              <textarea
                value={context}
                onChange={(e) => setContext(e.target.value)}
                placeholder="Describe specific requirements or constraints..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-macys-red"
                rows={3}
              />
            </div>

            {/* Generate Button */}
            <Button
              onClick={handleGenerate}
              disabled={loading}
              className="w-full"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Orchestrating Generation...
                </>
              ) : (
                "Orchestrate Test Data Generation"
              )}
            </Button>

            {error && (
              <div className="p-3 bg-red-50 text-red-700 rounded-md text-sm">
                {error}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Generated Data Preview */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>Orchestration Output</CardTitle>
                <CardDescription>
                  Generated data from Test Data Agent
                </CardDescription>
              </div>
              {generatedData && (
                <div className="flex space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCopy}
                  >
                    {copied ? (
                      <>
                        <Check className="mr-2 h-4 w-4" />
                        Copied!
                      </>
                    ) : (
                      <>
                        <Copy className="mr-2 h-4 w-4" />
                        Copy
                      </>
                    )}
                  </Button>
                  <Button
                    size="sm"
                    onClick={handleDownload}
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Download
                  </Button>
                </div>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {loading && orchestrationSteps.length > 0 && (
              <div className="mb-4 p-4 bg-gray-50 rounded-md">
                <h4 className="text-sm font-semibold mb-2">Orchestration Progress:</h4>
                <ul className="space-y-1">
                  {orchestrationSteps.map((step, index) => (
                    <li key={index} className="text-sm text-gray-600 flex items-start">
                      <span className="mr-2">•</span>
                      <span>{step}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {generatedData ? (
              <pre className="bg-gray-50 p-4 rounded-md overflow-x-auto text-sm">
                <code>{generatedData}</code>
              </pre>
            ) : !loading ? (
              <div className="text-center py-12 text-gray-500">
                Generated data will appear here
              </div>
            ) : null}
          </CardContent>
        </Card>
      </div>

      {/* How it Works */}
      <Card className="bg-green-50 border-green-200">
        <CardHeader>
          <CardTitle className="text-green-900">How eCommerce Domain Agent Works</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm text-green-800">
            <li>• <strong>Request Analysis:</strong> eCommerce Domain Agent analyzes your entity and context requirements</li>
            <li>• <strong>Knowledge Enrichment:</strong> Applies eCommerce business rules, constraints, and patterns</li>
            <li>• <strong>Schema Decision:</strong> Determines whether to use predefined or custom schema</li>
            <li>• <strong>Test Data Agent Call:</strong> Sends enriched request to Test Data Agent for generation</li>
            <li>• <strong>Validation:</strong> Ensures generated data meets business requirements</li>
            <li>• <strong>Pattern Storage:</strong> Stores successful patterns for future use</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}