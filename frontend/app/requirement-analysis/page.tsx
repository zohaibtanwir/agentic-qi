'use client';

import { useState, useEffect, useRef } from 'react';
import { useRequirementAnalysisStore, type RequirementAnalysisStore } from '@/lib/stores/requirement-analysis-store';
import { AnalysisForm } from '@/components/requirement-analysis/AnalysisForm';
import { AnalysisResults } from '@/components/requirement-analysis/AnalysisResults';
import { HistorySidebar } from '@/components/requirement-analysis/HistorySidebar';

export default function RequirementAnalysisPage() {
  const error = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.error);
  const clearError = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.clearError);
  const activeTab = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.activeTab);
  const analysisResult = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.analysisResult);
  const historyTotalCount = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.historyTotalCount);
  const loadHistory = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.loadHistory);

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
            <div className="w-10 h-10 bg-red-600 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-[var(--text-primary)]">
                Requirement Analysis Agent
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
                ? 'bg-red-600 text-white border-red-600'
                : 'bg-[var(--surface-secondary)] text-[var(--text-secondary)] border-[var(--border-default)] hover:border-red-600'
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
          Analyze requirements for quality, completeness, and testability. Identify gaps, generate clarifying questions,
          and get AI-generated acceptance criteria to improve your requirements before test case generation.
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
            <button onClick={clearError} className="text-red-500 hover:text-red-700">
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

        {/* Main Content */}
        <div className="flex-1">
          {activeTab === 'input' || !analysisResult ? (
            <AnalysisForm />
          ) : (
            <AnalysisResults />
          )}
        </div>
      </div>
    </main>
  );
}
