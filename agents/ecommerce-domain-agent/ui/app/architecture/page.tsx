"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowRight, ArrowDown, Brain, Database, Sparkles, Globe, Server, Layers, GitBranch } from "lucide-react";

export default function ArchitecturePage() {
  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="border-b pb-6">
        <h1 className="text-3xl font-bold text-gray-900">System Architecture</h1>
        <p className="text-gray-600 mt-2">
          Understanding the QA Intelligence Platform Architecture
        </p>
      </div>

      {/* Main Architecture Flow */}
      <Card className="bg-gradient-to-br from-gray-50 to-gray-100">
        <CardHeader>
          <CardTitle>Orchestration Architecture</CardTitle>
          <CardDescription>
            How the eCommerce Domain Agent orchestrates test data generation through the platform
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-8">
            {/* User Request Flow */}
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="bg-white rounded-lg p-6 shadow-md">
                  <div className="flex items-center mb-4">
                    <Globe className="h-8 w-8 text-blue-600 mr-3" />
                    <div>
                      <h3 className="font-semibold text-lg">User Request</h3>
                      <p className="text-sm text-gray-600">QA Engineer/Developer</p>
                    </div>
                  </div>
                  <div className="space-y-2 text-sm">
                    <p>• Specifies entity type (cart, order, etc.)</p>
                    <p>• Defines count and scenarios</p>
                    <p>• Provides optional context</p>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-center px-4">
                <ArrowRight className="h-8 w-8 text-gray-400" />
              </div>

              <div className="flex-1">
                <div className="bg-white rounded-lg p-6 shadow-md border-2 border-macys-red">
                  <div className="flex items-center mb-4">
                    <Brain className="h-8 w-8 text-macys-red mr-3" />
                    <div>
                      <h3 className="font-semibold text-lg">eCommerce Domain Agent</h3>
                      <p className="text-sm text-gray-600">Orchestration Layer</p>
                    </div>
                  </div>
                  <div className="space-y-2 text-sm">
                    <p>• Analyzes request</p>
                    <p>• Enriches with domain knowledge</p>
                    <p>• Determines generation strategy</p>
                    <p>• Builds custom schemas if needed</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-center">
              <ArrowDown className="h-8 w-8 text-gray-400" />
            </div>

            {/* Domain Agent Processing */}
            <div className="grid grid-cols-3 gap-4">
              <Card className="bg-green-50 border-green-200">
                <CardHeader className="pb-3">
                  <div className="flex items-center">
                    <Database className="h-6 w-6 text-green-600 mr-2" />
                    <CardTitle className="text-base">Knowledge Base</CardTitle>
                  </div>
                </CardHeader>
                <CardContent className="text-sm">
                  <ul className="space-y-1">
                    <li>• Business Rules</li>
                    <li>• Domain Entities</li>
                    <li>• Workflows</li>
                    <li>• Edge Cases</li>
                    <li>• Test Patterns</li>
                  </ul>
                </CardContent>
              </Card>

              <Card className="bg-blue-50 border-blue-200">
                <CardHeader className="pb-3">
                  <div className="flex items-center">
                    <Layers className="h-6 w-6 text-blue-600 mr-2" />
                    <CardTitle className="text-base">Schema Builder</CardTitle>
                  </div>
                </CardHeader>
                <CardContent className="text-sm">
                  <ul className="space-y-1">
                    <li>• Analyzes entity type</li>
                    <li>• Checks predefined list</li>
                    <li>• Builds custom schema</li>
                    <li>• Maps constraints</li>
                    <li>• Adds validations</li>
                  </ul>
                </CardContent>
              </Card>

              <Card className="bg-purple-50 border-purple-200">
                <CardHeader className="pb-3">
                  <div className="flex items-center">
                    <GitBranch className="h-6 w-6 text-purple-600 mr-2" />
                    <CardTitle className="text-base">Context Enricher</CardTitle>
                  </div>
                </CardHeader>
                <CardContent className="text-sm">
                  <ul className="space-y-1">
                    <li>• Adds business context</li>
                    <li>• Includes relationships</li>
                    <li>• Applies constraints</li>
                    <li>• Adds test scenarios</li>
                    <li>• Includes edge cases</li>
                  </ul>
                </CardContent>
              </Card>
            </div>

            <div className="flex justify-center">
              <ArrowDown className="h-8 w-8 text-gray-400" />
            </div>

            {/* Test Data Agent Call */}
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="bg-white rounded-lg p-6 shadow-md">
                  <div className="flex items-center mb-4">
                    <Server className="h-8 w-8 text-orange-600 mr-3" />
                    <div>
                      <h3 className="font-semibold text-lg">Enriched Request</h3>
                      <p className="text-sm text-gray-600">To Test Data Agent</p>
                    </div>
                  </div>
                  <div className="space-y-2 text-sm">
                    <p>• Enhanced context</p>
                    <p>• Business rules applied</p>
                    <p>• Custom schema (if needed)</p>
                    <p>• Test scenarios defined</p>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-center px-4">
                <ArrowRight className="h-8 w-8 text-gray-400" />
              </div>

              <div className="flex-1">
                <div className="bg-white rounded-lg p-6 shadow-md">
                  <div className="flex items-center mb-4">
                    <Sparkles className="h-8 w-8 text-purple-600 mr-3" />
                    <div>
                      <h3 className="font-semibold text-lg">Test Data Agent</h3>
                      <p className="text-sm text-gray-600">AI Generation Engine</p>
                    </div>
                  </div>
                  <div className="space-y-2 text-sm">
                    <p>• Receives enriched request</p>
                    <p>• Uses predefined or custom schema</p>
                    <p>• Generates realistic data</p>
                    <p>• Returns to Domain Agent</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Decision Flow */}
      <Card>
        <CardHeader>
          <CardTitle>Schema Decision Flow</CardTitle>
          <CardDescription>
            How the eCommerce Domain Agent determines schema strategy
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-gray-50 rounded-lg p-6">
            <div className="space-y-4">
              <div className="flex items-center">
                <div className="w-48 bg-blue-100 rounded p-3 text-sm font-medium">
                  Entity Request Received
                </div>
                <ArrowRight className="mx-4 h-5 w-5 text-gray-400" />
                <div className="w-48 bg-yellow-100 rounded p-3 text-sm font-medium">
                  Check Entity Type
                </div>
              </div>

              <div className="ml-52 space-y-4">
                <div className="border-l-2 border-gray-300 pl-8 py-2">
                  <div className="flex items-center">
                    <div className="w-56 bg-green-100 rounded p-3 text-sm">
                      <strong>Predefined Entity?</strong>
                      <p className="text-xs mt-1">user, product, address, etc.</p>
                    </div>
                    <ArrowRight className="mx-4 h-5 w-5 text-gray-400" />
                    <div className="w-48 bg-green-200 rounded p-3 text-sm">
                      Use Test Data Agent directly
                    </div>
                  </div>
                </div>

                <div className="border-l-2 border-gray-300 pl-8 py-2">
                  <div className="flex items-center">
                    <div className="w-56 bg-purple-100 rounded p-3 text-sm">
                      <strong>Domain Entity?</strong>
                      <p className="text-xs mt-1">cart, order, payment, etc.</p>
                    </div>
                    <ArrowRight className="mx-4 h-5 w-5 text-gray-400" />
                    <div className="w-48 bg-purple-200 rounded p-3 text-sm">
                      Build custom schema
                    </div>
                  </div>
                </div>

                <div className="border-l-2 border-gray-300 pl-8 py-2">
                  <div className="flex items-center">
                    <div className="w-56 bg-red-100 rounded p-3 text-sm">
                      <strong>Unknown Entity?</strong>
                      <p className="text-xs mt-1">Not in either category</p>
                    </div>
                    <ArrowRight className="mx-4 h-5 w-5 text-gray-400" />
                    <div className="w-48 bg-red-200 rounded p-3 text-sm">
                      Return error
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Benefits */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="bg-blue-50 border-blue-200">
          <CardHeader>
            <CardTitle className="text-blue-900">Benefits of Orchestration</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">✓</span>
                <span><strong>Domain Expertise:</strong> Leverages eCommerce-specific knowledge</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">✓</span>
                <span><strong>Intelligent Routing:</strong> Automatically chooses optimal generation path</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">✓</span>
                <span><strong>Custom Schemas:</strong> Handles domain-specific entities</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">✓</span>
                <span><strong>Business Rules:</strong> Ensures data meets business constraints</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">✓</span>
                <span><strong>Pattern Learning:</strong> Stores and reuses successful patterns</span>
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card className="bg-green-50 border-green-200">
          <CardHeader>
            <CardTitle className="text-green-900">Supported Entity Types</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm">
              <div>
                <h4 className="font-semibold text-green-800 mb-1">Predefined Entities (26 Total)</h4>
                <p className="text-gray-600 text-xs">Direct Test Data Agent calls - no custom schema needed</p>
                <div className="mt-2 grid grid-cols-3 gap-1 text-xs">
                  <span className="bg-green-100 px-2 py-1 rounded">user</span>
                  <span className="bg-green-100 px-2 py-1 rounded">person</span>
                  <span className="bg-green-100 px-2 py-1 rounded">customer_profile</span>
                  <span className="bg-green-100 px-2 py-1 rounded">email</span>
                  <span className="bg-green-100 px-2 py-1 rounded">phone</span>
                  <span className="bg-green-100 px-2 py-1 rounded">address</span>
                  <span className="bg-green-100 px-2 py-1 rounded">credit_card</span>
                  <span className="bg-green-100 px-2 py-1 rounded">product</span>
                  <span className="bg-green-100 px-2 py-1 rounded">company</span>
                  <span className="text-green-600">+ 17 more...</span>
                </div>
              </div>
              <div>
                <h4 className="font-semibold text-green-800 mb-1">Domain Entities (68 Total)</h4>
                <p className="text-gray-600 text-xs">Custom schemas built by Domain Agent</p>
                <div className="mt-2 grid grid-cols-3 gap-1 text-xs">
                  <span className="bg-blue-100 px-2 py-1 rounded">cart</span>
                  <span className="bg-blue-100 px-2 py-1 rounded">order</span>
                  <span className="bg-blue-100 px-2 py-1 rounded">payment</span>
                  <span className="bg-blue-100 px-2 py-1 rounded">shipping</span>
                  <span className="bg-blue-100 px-2 py-1 rounded">review</span>
                  <span className="bg-blue-100 px-2 py-1 rounded">subscription</span>
                  <span className="bg-blue-100 px-2 py-1 rounded">gift_card</span>
                  <span className="bg-blue-100 px-2 py-1 rounded">return</span>
                  <span className="bg-blue-100 px-2 py-1 rounded">fraud_check</span>
                  <span className="text-blue-600">+ 59 more...</span>
                </div>
              </div>
              <div className="pt-2 border-t">
                <p className="font-semibold text-gray-700">Total Entities: 94</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}