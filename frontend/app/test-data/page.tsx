'use client';

import { useEffect, useRef, useState } from 'react';
import { useTestDataStore } from '@/lib/stores/test-data-store';
import { GeneratorForm } from '@/components/test-data/GeneratorForm';
import { DataPreview } from '@/components/test-data/DataPreview';
import { HistorySidebar } from '@/components/test-data/HistorySidebar';

export default function TestDataPage() {
  const error = useTestDataStore((state) => state.error);
  const clearError = useTestDataStore((state) => state.clearError);
  const loadSchemas = useTestDataStore((state) => state.loadSchemas);
  const historyEntries = useTestDataStore((state) => state.historyEntries);
  const schemasLoadedRef = useRef(false);
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    // Only load schemas once on mount
    if (!schemasLoadedRef.current) {
      schemasLoadedRef.current = true;
      loadSchemas();
    }
  }, [loadSchemas]);

  return (
    <main className="max-w-7xl mx-auto px-6 py-8">
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-[var(--accent-default)] rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-[var(--text-primary)]">
                Test Data Agent
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
            {historyEntries.length > 0 && (
              <span className={`text-xs px-1.5 py-0.5 rounded ${
                showHistory ? 'bg-white/20' : 'bg-[var(--surface-tertiary)]'
              }`}>
                {historyEntries.length}
              </span>
            )}
          </button>
        </div>
        <p className="text-[var(--text-secondary)] mt-3 max-w-2xl">
          Generate realistic, schema-compliant test data for e-commerce testing scenarios.
          Supports traditional generation, LLM-enhanced context, and RAG retrieval.
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
          <div className="w-72 flex-shrink-0 bg-[var(--surface-primary)] rounded-xl border border-[var(--border-default)] overflow-hidden" style={{ height: '600px' }}>
            <HistorySidebar />
          </div>
        )}

        {/* Main Content: 2-column Grid */}
        <div className={`flex-1 grid grid-cols-1 ${showHistory ? 'xl:grid-cols-2' : 'lg:grid-cols-2'} gap-6`} style={{ minHeight: '600px' }}>
          {/* Left Column: Generator Form */}
          <GeneratorForm />

          {/* Right Column: Preview */}
          <DataPreview />
        </div>
      </div>
    </main>
  );
}
