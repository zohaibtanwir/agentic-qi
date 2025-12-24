'use client';

import React, { useEffect } from 'react';
import {
  useTestCasesStore,
  type TestCasesStore,
} from '@/lib/stores/test-cases-store';
import { type HistorySessionSummary } from '@/lib/grpc/testCasesClient';

function formatTimestamp(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

function getCoverageBadgeColor(level: string): string {
  switch (level.toLowerCase()) {
    case 'comprehensive':
      return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400';
    case 'standard':
      return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400';
    case 'minimal':
      return 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300';
    default:
      return 'bg-[var(--surface-tertiary)] text-[var(--text-muted)]';
  }
}

function getStatusIcon(status: string): React.ReactElement | null {
  switch (status.toLowerCase()) {
    case 'success':
      return (
        <svg className="w-3 h-3 text-green-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
        </svg>
      );
    case 'partial':
      return (
        <svg className="w-3 h-3 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
      );
    case 'failed':
      return (
        <svg className="w-3 h-3 text-red-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
        </svg>
      );
    default:
      return null;
  }
}

interface HistoryItemProps {
  entry: HistorySessionSummary;
  onLoad: (sessionId: string) => void;
  onDelete: (sessionId: string) => void;
  isLoading?: boolean;
}

function HistoryItem({ entry, onLoad, onDelete, isLoading }: HistoryItemProps) {
  return (
    <div
      className={`p-3 bg-[var(--surface-secondary)] rounded-lg border border-[var(--border-default)] hover:border-[var(--accent-default)] transition-colors cursor-pointer group ${isLoading ? 'opacity-50 pointer-events-none' : ''}`}
      onClick={() => onLoad(entry.sessionId)}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-medium text-[var(--text-primary)] text-sm line-clamp-2">
              {entry.userStoryPreview || 'Untitled session'}
            </span>
          </div>
          <div className="flex items-center gap-2 mt-1.5">
            <span className="text-xs px-1.5 py-0.5 bg-[var(--surface-tertiary)] rounded text-[var(--text-muted)]">
              {entry.testCaseCount} cases
            </span>
            <span className={`text-xs px-1.5 py-0.5 rounded ${getCoverageBadgeColor(entry.coverageLevel)}`}>
              {entry.coverageLevel}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-1">
          {getStatusIcon(entry.status)}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(entry.sessionId);
            }}
            className="opacity-0 group-hover:opacity-100 p-1 text-[var(--text-muted)] hover:text-red-500 transition-all"
            title="Delete"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
      <div className="flex items-center justify-between mt-2 text-xs text-[var(--text-muted)]">
        <span>{formatTimestamp(entry.createdAt)}</span>
        {entry.domain && (
          <span className="capitalize">{entry.domain}</span>
        )}
      </div>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="p-3 space-y-2">
      {[1, 2, 3].map((i) => (
        <div key={i} className="p-3 bg-[var(--surface-secondary)] rounded-lg border border-[var(--border-default)] animate-pulse">
          <div className="h-4 bg-[var(--surface-tertiary)] rounded w-3/4 mb-2"></div>
          <div className="flex gap-2">
            <div className="h-5 bg-[var(--surface-tertiary)] rounded w-16"></div>
            <div className="h-5 bg-[var(--surface-tertiary)] rounded w-20"></div>
          </div>
          <div className="h-3 bg-[var(--surface-tertiary)] rounded w-1/3 mt-2"></div>
        </div>
      ))}
    </div>
  );
}

export function HistorySidebar() {
  const historyEntries = useTestCasesStore((state: TestCasesStore) => state.historyEntries);
  const historyTotalCount = useTestCasesStore((state: TestCasesStore) => state.historyTotalCount);
  const isLoadingHistory = useTestCasesStore((state: TestCasesStore) => state.isLoadingHistory);
  const isLoadingSession = useTestCasesStore((state: TestCasesStore) => state.isLoadingSession);
  const loadHistory = useTestCasesStore((state: TestCasesStore) => state.loadHistory);
  const loadHistorySession = useTestCasesStore((state: TestCasesStore) => state.loadHistorySession);
  const deleteHistorySession = useTestCasesStore((state: TestCasesStore) => state.deleteHistorySession);
  const error = useTestCasesStore((state: TestCasesStore) => state.error);

  // Load history on mount
  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleDelete = async (sessionId: string) => {
    if (confirm('Are you sure you want to delete this session?')) {
      await deleteHistorySession(sessionId);
    }
  };

  if (isLoadingHistory && historyEntries.length === 0) {
    return <LoadingSkeleton />;
  }

  if (historyEntries.length === 0) {
    return (
      <div className="p-4 text-center">
        <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-[var(--surface-secondary)] flex items-center justify-center">
          <svg className="w-6 h-6 text-[var(--text-muted)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
          </svg>
        </div>
        <p className="text-sm text-[var(--text-muted)]">No history yet</p>
        <p className="text-xs text-[var(--text-muted)] mt-1">Generated test cases will appear here</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border-default)]">
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4 text-[var(--text-muted)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-sm font-medium text-[var(--text-primary)]">History</span>
          <span className="text-xs px-1.5 py-0.5 bg-[var(--surface-tertiary)] rounded text-[var(--text-muted)]">
            {historyTotalCount}
          </span>
        </div>
        {isLoadingHistory && (
          <svg className="w-4 h-4 animate-spin text-[var(--text-muted)]" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        )}
      </div>

      {error && (
        <div className="px-4 py-2 bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800">
          <p className="text-xs text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {historyEntries.map((entry) => (
          <HistoryItem
            key={entry.sessionId}
            entry={entry}
            onLoad={loadHistorySession}
            onDelete={handleDelete}
            isLoading={isLoadingSession}
          />
        ))}
      </div>
    </div>
  );
}
