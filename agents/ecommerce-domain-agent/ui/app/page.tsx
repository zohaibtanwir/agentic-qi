"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import {
  Package,
  Workflow,
  Database,
  Brain,
  ArrowRight,
  CheckCircle,
  XCircle,
  AlertCircle
} from "lucide-react";

interface HealthStatus {
  status: string;
  components: Record<string, string>;
}

export default function DashboardPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 10000); // Check every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchHealth = async () => {
    try {
      const response = await fetch("/api/health");
      const data = await response.json();
      setHealth(data);
    } catch (error) {
      console.error("Failed to fetch health status:", error);
      setHealth({ status: "error", components: {} });
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "healthy":
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "degraded":
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      case "unhealthy":
      case "error":
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-400" />;
    }
  };

  const features = [
    {
      title: "Domain Entities",
      description: "Browse and explore eCommerce domain entities with their relationships and business rules.",
      icon: Package,
      href: "/entities",
      color: "text-blue-600",
    },
    {
      title: "Workflows",
      description: "Visualize and understand complex business workflows like checkout and order processing.",
      icon: Workflow,
      href: "/workflows",
      color: "text-purple-600",
    },
    {
      title: "Orchestrate Generation",
      description: "Orchestrate test data generation with domain enrichment before calling Test Data Agent.",
      icon: Database,
      href: "/generate",
      color: "text-green-600",
    },
    {
      title: "Knowledge Base",
      description: "Query and explore the AI-powered knowledge base with semantic search.",
      icon: Brain,
      href: "/knowledge",
      color: "text-orange-600",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center py-12 bg-gradient-to-b from-white to-gray-50 rounded-lg">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          <span className="text-macys-red">Macy's</span> eCommerce Domain Agent
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Intelligent orchestration layer that enriches test data requests with eCommerce domain expertise
          before calling the Test Data Agent for generation.
        </p>
      </div>

      {/* System Status */}
      <Card className="border-gray-200">
        <CardHeader>
          <CardTitle>System Status</CardTitle>
          <CardDescription>Real-time health monitoring of all components</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-gray-500">Loading status...</div>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                {getStatusIcon(health?.status || "unknown")}
                <span className="font-semibold">
                  Overall Status: {health?.status || "unknown"}
                </span>
              </div>
              <div className="grid grid-cols-3 gap-4 mt-4">
                {Object.entries(health?.components || {}).map(([component, status]) => (
                  <div key={component} className="flex items-center space-x-2 p-2 bg-gray-50 rounded">
                    {getStatusIcon(status)}
                    <span className="text-sm capitalize">
                      {component.replace(/_/g, " ")}: {status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {features.map((feature) => {
          const Icon = feature.icon;
          return (
            <Card key={feature.title} className="hover:shadow-lg transition-shadow cursor-pointer">
              <Link href={feature.href}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg bg-gray-50 ${feature.color}`}>
                        <Icon className="h-6 w-6" />
                      </div>
                      <CardTitle className="text-xl">{feature.title}</CardTitle>
                    </div>
                    <ArrowRight className="h-5 w-5 text-gray-400" />
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600">{feature.description}</p>
                </CardContent>
              </Link>
            </Card>
          );
        })}
      </div>

      {/* Quick Actions */}
      <Card className="border-macys-red/20 bg-red-50/30">
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Get started with common tasks</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Link href="/generate">
              <Button>Orchestrate Test Data</Button>
            </Link>
            <Link href="/entities/cart">
              <Button variant="outline">View Cart Entity</Button>
            </Link>
            <Link href="/workflows/checkout">
              <Button variant="outline">Checkout Workflow</Button>
            </Link>
            <Link href="/knowledge">
              <Button variant="outline">Search Knowledge</Button>
            </Link>
          </div>
        </CardContent>
      </Card>

      {/* Statistics */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="text-2xl font-bold text-macys-red">68</div>
            <p className="text-sm text-gray-600 mt-1">Domain Entities</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="text-2xl font-bold text-macys-red">26</div>
            <p className="text-sm text-gray-600 mt-1">Predefined Entities</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="text-2xl font-bold text-macys-red">94</div>
            <p className="text-sm text-gray-600 mt-1">Total Entities</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="text-2xl font-bold text-macys-red">19</div>
            <p className="text-sm text-gray-600 mt-1">Entity Categories</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}