'use client';

import { useState, useEffect, useRef } from 'react';
import { useTestCasesStore, type TestCasesStore } from '@/lib/stores/test-cases-store';
import { GenerationForm } from '@/components/test-cases/GenerationForm';
import { HistorySidebar } from '@/components/test-cases/HistorySidebar';

export default function TestCasesPage() {
  const error = useTestCasesStore((state: TestCasesStore) => state.error);
  const clearError = useTestCasesStore((state: TestCasesStore) => state.clearError);
  const historyTotalCount = useTestCasesStore((state: TestCasesStore) => state.historyTotalCount);
  const loadHistory = useTestCasesStore((state: TestCasesStore) => state.loadHistory);

  const [showHistory, setShowHistory] = useState(false);
  const historyLoadedRef = useRef(false);

  useEffect(() => {
    // Load history once on mount
    if (!historyLoadedRef.current) {
      historyLoadedRef.current = true;
      loadHistory();
    }
  }, [loadHistory]);

  return (
    <main className="max-w-7xl mx-auto px-6 py-8">
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
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
          {/* History Toggle Button */}
          <button
            onClick={() => setShowHistory(!showHistory)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg border transition-colors ${
              showHistory
                ? 'bg-[var(--accent-default)] text-white border-[var(--accent-default)]'
                : 'bg-[var(--surface-secondary)] text-[var(--text-secondary)] border-[var(--border-default)] hover:border-[var(--accent-default)]'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm font-medium">History</span>
            {historyTotalCount > 0 && (
              <span className={`text-xs px-1.5 py-0.5 rounded ${
                showHistory ? 'bg-white/20' : 'bg-[var(--surface-tertiary)]'
              }`}>
                {historyTotalCount}
              </span>
            )}
          </button>
        </div>
        <p className="text-[var(--text-secondary)] mt-3 max-w-2xl">
          Generate comprehensive test cases from user stories, API specifications, or free-form requirements.
          Powered by AI to ensure thorough test coverage across functional, negative, boundary, and edge case scenarios.
        </p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-red-700">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="font-medium">Error</span>
            </div>
            <button
              onClick={clearError}
              className="text-red-500 hover:text-red-700"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <p className="mt-1 text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Main Layout with optional History Sidebar */}
      <div className="flex gap-6">
        {/* History Sidebar */}
        {showHistory && (
          <div className="w-80 flex-shrink-0 bg-[var(--surface-primary)] rounded-xl border border-[var(--border-default)] overflow-hidden" style={{ height: '700px' }}>
            <HistorySidebar />
          </div>
        )}

        {/* Main Content: Generation Form */}
        <div className="flex-1">
          <GenerationForm />
        </div>
      </div>
    </main>
  );
}
