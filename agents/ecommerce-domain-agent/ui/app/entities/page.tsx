"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import {
  Package, ShoppingCart, CreditCard, ArrowRight, Database, Link2,
  Truck, Star, Heart, RotateCcw, BarChart, Bell, RefreshCw, Gift,
  Search, Shield, HelpCircle, Tag, Box, Users
} from "lucide-react";

// Comprehensive entity list with all domain entities
const entities = [
  // Shopping & Cart
  {
    name: "cart",
    displayName: "Shopping Cart",
    description: "Shopping cart containing items before checkout",
    category: "shopping",
    icon: ShoppingCart,
    color: "text-blue-600",
    fields: 8,
    relationships: 2,
    businessRules: 3,
    edgeCases: 5,
  },
  {
    name: "cart_item",
    displayName: "Cart Item",
    description: "Individual item in a shopping cart",
    category: "shopping",
    icon: ShoppingCart,
    color: "text-blue-600",
    fields: 6,
    relationships: 2,
    businessRules: 2,
    edgeCases: 3,
  },
  {
    name: "saved_cart",
    displayName: "Saved Cart",
    description: "Cart saved for later purchase",
    category: "shopping",
    icon: ShoppingCart,
    color: "text-blue-600",
    fields: 7,
    relationships: 1,
    businessRules: 2,
    edgeCases: 2,
  },

  // Orders
  {
    name: "order",
    displayName: "Order",
    description: "Confirmed purchase order after successful checkout",
    category: "orders",
    icon: Package,
    color: "text-green-600",
    fields: 12,
    relationships: 3,
    businessRules: 4,
    edgeCases: 6,
  },
  {
    name: "order_item",
    displayName: "Order Item",
    description: "Individual item within an order",
    category: "orders",
    icon: Package,
    color: "text-green-600",
    fields: 8,
    relationships: 2,
    businessRules: 3,
    edgeCases: 4,
  },
  {
    name: "order_status",
    displayName: "Order Status",
    description: "Status tracking for orders",
    category: "orders",
    icon: Package,
    color: "text-green-600",
    fields: 5,
    relationships: 1,
    businessRules: 2,
    edgeCases: 3,
  },

  // Payments
  {
    name: "payment",
    displayName: "Payment",
    description: "Payment transaction record for an order",
    category: "payments",
    icon: CreditCard,
    color: "text-purple-600",
    fields: 10,
    relationships: 2,
    businessRules: 3,
    edgeCases: 4,
  },
  {
    name: "refund",
    displayName: "Refund",
    description: "Refund transaction for returned items",
    category: "payments",
    icon: CreditCard,
    color: "text-purple-600",
    fields: 8,
    relationships: 2,
    businessRules: 3,
    edgeCases: 3,
  },
  {
    name: "payment_authorization",
    displayName: "Payment Authorization",
    description: "Authorization for payment processing",
    category: "payments",
    icon: CreditCard,
    color: "text-purple-600",
    fields: 7,
    relationships: 1,
    businessRules: 2,
    edgeCases: 2,
  },

  // Inventory
  {
    name: "inventory",
    displayName: "Inventory",
    description: "Product inventory tracking",
    category: "inventory",
    icon: Box,
    color: "text-orange-600",
    fields: 9,
    relationships: 2,
    businessRules: 3,
    edgeCases: 4,
  },
  {
    name: "stock",
    displayName: "Stock",
    description: "Current stock levels",
    category: "inventory",
    icon: Box,
    color: "text-orange-600",
    fields: 6,
    relationships: 1,
    businessRules: 2,
    edgeCases: 3,
  },
  {
    name: "stock_alert",
    displayName: "Stock Alert",
    description: "Low stock notifications",
    category: "inventory",
    icon: Box,
    color: "text-orange-600",
    fields: 5,
    relationships: 1,
    businessRules: 2,
    edgeCases: 2,
  },

  // Customer
  {
    name: "customer",
    displayName: "Customer",
    description: "Customer account information",
    category: "customer",
    icon: Users,
    color: "text-indigo-600",
    fields: 11,
    relationships: 3,
    businessRules: 3,
    edgeCases: 4,
  },
  {
    name: "loyalty_member",
    displayName: "Loyalty Member",
    description: "Loyalty program membership",
    category: "customer",
    icon: Users,
    color: "text-indigo-600",
    fields: 8,
    relationships: 2,
    businessRules: 3,
    edgeCases: 3,
  },
  {
    name: "customer_preferences",
    displayName: "Customer Preferences",
    description: "Customer shopping preferences",
    category: "customer",
    icon: Users,
    color: "text-indigo-600",
    fields: 6,
    relationships: 1,
    businessRules: 2,
    edgeCases: 2,
  },

  // Shipping
  {
    name: "shipping",
    displayName: "Shipping",
    description: "Shipping information for orders",
    category: "shipping",
    icon: Truck,
    color: "text-cyan-600",
    fields: 10,
    relationships: 2,
    businessRules: 3,
    edgeCases: 4,
  },
  {
    name: "shipment",
    displayName: "Shipment",
    description: "Individual shipment tracking",
    category: "shipping",
    icon: Truck,
    color: "text-cyan-600",
    fields: 9,
    relationships: 2,
    businessRules: 3,
    edgeCases: 3,
  },
  {
    name: "tracking",
    displayName: "Tracking",
    description: "Package tracking information",
    category: "shipping",
    icon: Truck,
    color: "text-cyan-600",
    fields: 7,
    relationships: 1,
    businessRules: 2,
    edgeCases: 3,
  },

  // Promotions
  {
    name: "discount",
    displayName: "Discount",
    description: "Discount rules and applications",
    category: "promotions",
    icon: Tag,
    color: "text-pink-600",
    fields: 8,
    relationships: 2,
    businessRules: 4,
    edgeCases: 5,
  },
  {
    name: "coupon",
    displayName: "Coupon",
    description: "Coupon codes for discounts",
    category: "promotions",
    icon: Tag,
    color: "text-pink-600",
    fields: 7,
    relationships: 1,
    businessRules: 3,
    edgeCases: 4,
  },
  {
    name: "promotion",
    displayName: "Promotion",
    description: "Promotional campaigns",
    category: "promotions",
    icon: Tag,
    color: "text-pink-600",
    fields: 9,
    relationships: 2,
    businessRules: 3,
    edgeCases: 4,
  },

  // Reviews
  {
    name: "review",
    displayName: "Review",
    description: "Product reviews from customers",
    category: "reviews",
    icon: Star,
    color: "text-yellow-600",
    fields: 8,
    relationships: 2,
    businessRules: 3,
    edgeCases: 3,
  },
  {
    name: "rating",
    displayName: "Rating",
    description: "Product rating scores",
    category: "reviews",
    icon: Star,
    color: "text-yellow-600",
    fields: 5,
    relationships: 2,
    businessRules: 2,
    edgeCases: 2,
  },

  // Wishlist
  {
    name: "wishlist",
    displayName: "Wishlist",
    description: "Customer's saved items for later",
    category: "wishlist",
    icon: Heart,
    color: "text-red-600",
    fields: 6,
    relationships: 2,
    businessRules: 2,
    edgeCases: 3,
  },
  {
    name: "favorites",
    displayName: "Favorites",
    description: "Customer's favorite products",
    category: "wishlist",
    icon: Heart,
    color: "text-red-600",
    fields: 5,
    relationships: 2,
    businessRules: 2,
    edgeCases: 2,
  },

  // Returns
  {
    name: "return",
    displayName: "Return",
    description: "Product return request",
    category: "returns",
    icon: RotateCcw,
    color: "text-gray-600",
    fields: 10,
    relationships: 2,
    businessRules: 4,
    edgeCases: 5,
  },
  {
    name: "exchange",
    displayName: "Exchange",
    description: "Product exchange request",
    category: "returns",
    icon: RotateCcw,
    color: "text-gray-600",
    fields: 9,
    relationships: 2,
    businessRules: 3,
    edgeCases: 4,
  },

  // Analytics
  {
    name: "analytics_event",
    displayName: "Analytics Event",
    description: "User behavior tracking events",
    category: "analytics",
    icon: BarChart,
    color: "text-teal-600",
    fields: 7,
    relationships: 1,
    businessRules: 2,
    edgeCases: 3,
  },

  // Communications
  {
    name: "notification",
    displayName: "Notification",
    description: "Customer notifications",
    category: "communications",
    icon: Bell,
    color: "text-blue-600",
    fields: 6,
    relationships: 1,
    businessRules: 2,
    edgeCases: 3,
  },

  // Subscriptions
  {
    name: "subscription",
    displayName: "Subscription",
    description: "Recurring subscription service",
    category: "subscriptions",
    icon: RefreshCw,
    color: "text-violet-600",
    fields: 9,
    relationships: 2,
    businessRules: 3,
    edgeCases: 4,
  },

  // Gift Cards
  {
    name: "gift_card",
    displayName: "Gift Card",
    description: "Gift card purchase and redemption",
    category: "gift_cards",
    icon: Gift,
    color: "text-emerald-600",
    fields: 8,
    relationships: 2,
    businessRules: 3,
    edgeCases: 4,
  },

  // Search
  {
    name: "search_query",
    displayName: "Search Query",
    description: "Customer search queries",
    category: "search",
    icon: Search,
    color: "text-slate-600",
    fields: 6,
    relationships: 1,
    businessRules: 2,
    edgeCases: 3,
  },

  // Security
  {
    name: "fraud_check",
    displayName: "Fraud Check",
    description: "Fraud detection and prevention",
    category: "security",
    icon: Shield,
    color: "text-red-700",
    fields: 8,
    relationships: 2,
    businessRules: 4,
    edgeCases: 5,
  },

  // Support
  {
    name: "support_ticket",
    displayName: "Support Ticket",
    description: "Customer support requests",
    category: "support",
    icon: HelpCircle,
    color: "text-amber-600",
    fields: 9,
    relationships: 2,
    businessRules: 3,
    edgeCases: 4,
  },
];

const categories = [
  { value: "all", label: "All Entities", count: entities.length },
  { value: "shopping", label: "Shopping & Cart", count: entities.filter(e => e.category === "shopping").length },
  { value: "orders", label: "Orders", count: entities.filter(e => e.category === "orders").length },
  { value: "payments", label: "Payments", count: entities.filter(e => e.category === "payments").length },
  { value: "inventory", label: "Inventory", count: entities.filter(e => e.category === "inventory").length },
  { value: "customer", label: "Customer", count: entities.filter(e => e.category === "customer").length },
  { value: "shipping", label: "Shipping", count: entities.filter(e => e.category === "shipping").length },
  { value: "promotions", label: "Promotions", count: entities.filter(e => e.category === "promotions").length },
  { value: "reviews", label: "Reviews", count: entities.filter(e => e.category === "reviews").length },
  { value: "wishlist", label: "Wishlist", count: entities.filter(e => e.category === "wishlist").length },
  { value: "returns", label: "Returns", count: entities.filter(e => e.category === "returns").length },
];

export default function EntitiesPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>("all");

  const filteredEntities = selectedCategory === "all"
    ? entities
    : entities.filter(e => e.category === selectedCategory);

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="border-b pb-6">
        <h1 className="text-3xl font-bold text-gray-900">Domain Entities</h1>
        <p className="text-gray-600 mt-2">
          Explore all {entities.length} eCommerce domain entities with their relationships and business rules
        </p>
      </div>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2">
        {categories.map((cat) => (
          <Button
            key={cat.value}
            variant={selectedCategory === cat.value ? "default" : "outline"}
            onClick={() => setSelectedCategory(cat.value)}
            size="sm"
          >
            {cat.label} ({cat.count})
          </Button>
        ))}
      </div>

      {/* Entity Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredEntities.map((entity) => {
          const Icon = entity.icon;
          return (
            <Card key={entity.name} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`p-3 rounded-lg bg-gray-50 ${entity.color}`}>
                      <Icon className="h-6 w-6" />
                    </div>
                    <div>
                      <CardTitle className="text-xl">{entity.displayName}</CardTitle>
                      <CardDescription className="mt-1">
                        {entity.description}
                      </CardDescription>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div className="flex items-center space-x-2">
                      <Database className="h-4 w-4 text-gray-400" />
                      <span className="text-gray-600">{entity.fields} Fields</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Link2 className="h-4 w-4 text-gray-400" />
                      <span className="text-gray-600">{entity.relationships} Relations</span>
                    </div>
                  </div>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-2">
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">
                      {entity.businessRules} Business Rules
                    </span>
                    <span className="px-2 py-1 bg-orange-100 text-orange-700 rounded-full text-xs">
                      {entity.edgeCases} Edge Cases
                    </span>
                  </div>

                  {/* Actions */}
                  <div className="flex justify-between items-center pt-3 border-t">
                    <Link href={`/entities/${entity.name}`}>
                      <Button variant="outline" size="sm">
                        View Details
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </Button>
                    </Link>
                    <Link href={`/generate?entity=${entity.name}`}>
                      <Button size="sm">
                        Generate Data
                      </Button>
                    </Link>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Summary Stats */}
      <Card className="bg-gray-50">
        <CardHeader>
          <CardTitle>Entity Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-4">
            <div>
              <div className="text-2xl font-bold text-macys-red">
                {entities.length}
              </div>
              <p className="text-sm text-gray-600">Domain Entities</p>
            </div>
            <div>
              <div className="text-2xl font-bold text-macys-red">
                {entities.reduce((acc, e) => acc + e.fields, 0)}
              </div>
              <p className="text-sm text-gray-600">Total Fields</p>
            </div>
            <div>
              <div className="text-2xl font-bold text-macys-red">
                {entities.reduce((acc, e) => acc + e.businessRules, 0)}
              </div>
              <p className="text-sm text-gray-600">Business Rules</p>
            </div>
            <div>
              <div className="text-2xl font-bold text-macys-red">
                {entities.reduce((acc, e) => acc + e.edgeCases, 0)}
              </div>
              <p className="text-sm text-gray-600">Edge Cases</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}