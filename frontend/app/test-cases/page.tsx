import { GenerationForm } from '@/components/test-cases/GenerationForm';

export const metadata = {
  title: 'Test Cases Agent | QA Platform',
  description: 'Generate comprehensive test cases from requirements using AI',
};

export default function TestCasesPage() {
  return (
    <main className="max-w-7xl mx-auto px-6 py-8">
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-[var(--accent-default)] rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
          <div>
            <h1 className="text-2xl font-bold text-[var(--text-primary)]">
              Test Cases Agent
            </h1>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                <span className="w-1.5 h-1.5 bg-green-500 rounded-full mr-1.5"></span>
                Operational
              </span>
              <span className="text-sm text-[var(--text-muted)]">v1.0.0</span>
            </div>
          </div>
        </div>
        <p className="text-[var(--text-secondary)] mt-3 max-w-2xl">
          Generate comprehensive test cases from user stories, API specifications, or free-form requirements.
          Powered by AI to ensure thorough test coverage across functional, negative, boundary, and edge case scenarios.
        </p>
      </div>

      {/* Generation Form */}
      <GenerationForm />
    </main>
  );
}
