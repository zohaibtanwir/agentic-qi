import { AgentCard } from '@/components/AgentCard';

export default function Home() {
  return (
    <main className="min-h-screen bg-[var(--bg-secondary)]">
      {/* Hero Section */}
      <div className="bg-white border-b border-[var(--border-default)]">
        <div className="max-w-7xl mx-auto px-6 py-16">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl font-bold text-[var(--text-primary)] mb-4">
              QA Platform
            </h1>
            <p className="text-lg text-[var(--text-secondary)] mb-2">
              AI-powered test generation and validation suite
            </p>
            <p className="text-sm text-[var(--text-muted)]">
              Accelerate your testing workflow with intelligent agents for test cases, test data, and domain expertise
            </p>
          </div>
        </div>
      </div>

      {/* Agent Cards Section */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-[var(--text-primary)] mb-2">
            Available Agents
          </h2>
          <p className="text-sm text-[var(--text-muted)]">
            Select an agent to start generating test artifacts
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Test Cases Agent */}
          <AgentCard
            name="Test Cases Agent"
            description="Generate comprehensive test cases from user stories, API specs, or free-form input"
            status="operational"
            link="/test-cases"
            features={[
              'User Stories to test cases',
              'API Specifications parsing',
              'Free-form input generation',
              'Comprehensive coverage analysis',
            ]}
          />

          {/* Test Data Agent */}
          <AgentCard
            name="Test Data Agent"
            description="Create realistic, schema-compliant test data for your applications"
            status="operational"
            link="/test-data"
            features={[
              'Schema-based generation',
              'AI-powered realistic data',
              'Multiple output formats',
              'Custom constraints support',
            ]}
          />

          {/* eCommerce Domain Agent */}
          <AgentCard
            name="eCommerce Domain Agent"
            description="Specialized agent with deep eCommerce domain knowledge and validation"
            status="coming_soon"
            link="#"
            features={[
              'Business rules validation',
              'Edge case identification',
              'Domain-specific scenarios',
              'Integration test generation',
            ]}
          />
        </div>
      </div>
    </main>
  );
}
