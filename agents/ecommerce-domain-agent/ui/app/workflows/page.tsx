import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { Workflow, ArrowRight, ShoppingBag, RotateCcw } from "lucide-react";

const workflows = [
  {
    name: "checkout",
    displayName: "Checkout Process",
    description: "Complete checkout workflow from cart to order confirmation",
    icon: ShoppingBag,
    steps: 5,
    entities: ["cart", "order", "payment"],
    color: "text-green-600",
  },
  {
    name: "return_flow",
    displayName: "Return Flow",
    description: "Product return and refund processing workflow",
    icon: RotateCcw,
    steps: 4,
    entities: ["order", "payment"],
    color: "text-orange-600",
  },
];

export default function WorkflowsPage() {
  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="border-b pb-6">
        <h1 className="text-3xl font-bold text-gray-900">Business Workflows</h1>
        <p className="text-gray-600 mt-2">
          Visualize and understand complex eCommerce business processes
        </p>
      </div>

      {/* Workflow Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {workflows.map((workflow) => {
          const Icon = workflow.icon;
          return (
            <Card key={workflow.name} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`p-3 rounded-lg bg-gray-50 ${workflow.color}`}>
                      <Icon className="h-6 w-6" />
                    </div>
                    <div>
                      <CardTitle className="text-xl">{workflow.displayName}</CardTitle>
                      <CardDescription className="mt-1">
                        {workflow.description}
                      </CardDescription>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <span>{workflow.steps} Steps</span>
                    <span>•</span>
                    <span>{workflow.entities.length} Entities</span>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {workflow.entities.map((entity) => (
                      <span
                        key={entity}
                        className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs"
                      >
                        {entity}
                      </span>
                    ))}
                  </div>

                  <div className="pt-3 border-t">
                    <Button variant="outline" className="w-full">
                      View Workflow Details
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}