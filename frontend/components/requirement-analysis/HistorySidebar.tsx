'use client';

import React, { useEffect, useState } from 'react';
import {
  useRequirementAnalysisStore,
  type RequirementAnalysisStore,
} from '@/lib/stores/requirement-analysis-store';
import { type HistorySessionSummary } from '@/lib/grpc/requirementAnalysisClient';

function formatTimestamp(isoString: string): string {
  if (!isoString) return '';
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

function getGradeBadgeColor(grade: string): string {
  // Macy's-themed grade colors with high contrast text
  switch (grade.toUpperCase()) {
    case 'A':
      return 'bg-green-600 text-white dark:bg-green-700';
    case 'B':
      return 'bg-blue-600 text-white dark:bg-blue-700';
    case 'C':
      return 'bg-amber-500 text-white dark:bg-amber-600';
    case 'D':
      return 'bg-orange-500 text-white dark:bg-orange-600';
    case 'F':
      return 'bg-red-600 text-white dark:bg-red-700';
    default:
      return 'bg-[var(--surface-tertiary)] text-[var(--text-muted)]';
  }
}

function getInputTypeLabel(inputType: string): string {
  switch (inputType) {
    case 'jira':
      return 'Jira';
    case 'free_form':
      return 'Free-form';
    case 'transcript':
      return 'Transcript';
    default:
      return inputType;
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
              {entry.title || 'Untitled analysis'}
            </span>
          </div>
          <div className="flex items-center gap-2 mt-1.5 flex-wrap">
            <span className={`text-xs px-1.5 py-0.5 rounded font-semibold ${getGradeBadgeColor(entry.qualityGrade)}`}>
              {entry.qualityScore} ({entry.qualityGrade})
            </span>
            <span className="text-xs px-1.5 py-0.5 bg-[var(--surface-tertiary)] rounded text-[var(--text-muted)]">
              {entry.gapsCount} gaps
            </span>
            {entry.readyForTests && (
              <span className="text-xs px-1.5 py-0.5 bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 rounded">
                Ready
              </span>
            )}
          </div>
          <div className="flex items-center gap-2 mt-1.5 text-xs text-[var(--text-muted)]">
            <span className="capitalize">{getInputTypeLabel(entry.inputType)}</span>
            <span>·</span>
            <span>{entry.questionsCount}Q</span>
            <span>·</span>
            <span>{entry.generatedAcsCount}AC</span>
          </div>
        </div>
        <div className="flex items-center gap-1">
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
        <span className="text-[10px] truncate max-w-[100px]">{entry.llmModel}</span>
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
            <div className="h-5 bg-[var(--surface-tertiary)] rounded w-12"></div>
          </div>
          <div className="h-3 bg-[var(--surface-tertiary)] rounded w-1/3 mt-2"></div>
        </div>
      ))}
    </div>
  );
}

interface FilterSelectProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: { value: string; label: string }[];
}

function FilterSelect({ label, value, onChange, options }: FilterSelectProps) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="text-xs px-2 py-1 bg-[var(--surface-secondary)] border border-[var(--border-default)] rounded text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-default)]"
      aria-label={label}
    >
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  );
}

export function HistorySidebar() {
  const [searchInput, setSearchInput] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  const historyEntries = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.historyEntries);
  const historyTotalCount = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.historyTotalCount);
  const historyFilters = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.historyFilters);
  const historySearchQuery = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.historySearchQuery);
  const isLoadingHistory = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.isLoadingHistory);
  const isLoadingSession = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.isLoadingSession);
  const isSearchingHistory = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.isSearchingHistory);
  const selectedSession = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.selectedSession);
  const loadHistory = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.loadHistory);
  const loadHistorySession = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.loadHistorySession);
  const deleteHistorySession = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.deleteHistorySession);
  const searchHistory = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.searchHistory);
  const setHistoryFilters = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.setHistoryFilters);
  const clearHistorySearch = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.clearHistorySearch);
  const restoreFromSession = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.restoreFromSession);
  const error = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.error);

  // Load history on mount
  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  // Handle search with debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchInput.trim()) {
        searchHistory(searchInput);
      } else if (historySearchQuery) {
        clearHistorySearch();
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchInput, searchHistory, clearHistorySearch, historySearchQuery]);

  const handleDelete = async (sessionId: string) => {
    if (confirm('Are you sure you want to delete this analysis?')) {
      await deleteHistorySession(sessionId);
    }
  };

  const handleLoad = async (sessionId: string) => {
    await loadHistorySession(sessionId);
  };

  // When a session is loaded, restore it to the main view
  useEffect(() => {
    if (selectedSession) {
      restoreFromSession(selectedSession);
    }
  }, [selectedSession, restoreFromSession]);

  const inputTypeOptions = [
    { value: '', label: 'All Types' },
    { value: 'jira', label: 'Jira' },
    { value: 'free_form', label: 'Free-form' },
    { value: 'transcript', label: 'Transcript' },
  ];

  const gradeOptions = [
    { value: '', label: 'All Grades' },
    { value: 'A', label: 'A' },
    { value: 'B', label: 'B' },
    { value: 'C', label: 'C' },
    { value: 'D', label: 'D' },
    { value: 'F', label: 'F' },
  ];

  const readyOptions = [
    { value: '', label: 'All Status' },
    { value: 'ready', label: 'Ready' },
    { value: 'not_ready', label: 'Not Ready' },
  ];

  if (isLoadingHistory && historyEntries.length === 0) {
    return <LoadingSkeleton />;
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
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
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`p-1 rounded hover:bg-[var(--surface-tertiary)] transition-colors ${showFilters ? 'text-[var(--accent-default)]' : 'text-[var(--text-muted)]'}`}
            title="Toggle filters"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
          </button>
          {(isLoadingHistory || isSearchingHistory) && (
            <svg className="w-4 h-4 animate-spin text-[var(--text-muted)]" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          )}
        </div>
      </div>

      {/* Search */}
      <div className="px-3 py-2 border-b border-[var(--border-default)]">
        <div className="relative">
          <svg className="w-4 h-4 absolute left-2.5 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search analyses..."
            className="w-full pl-8 pr-3 py-1.5 text-sm bg-[var(--surface-secondary)] border border-[var(--border-default)] rounded focus:outline-none focus:ring-1 focus:ring-[var(--accent-default)] text-[var(--text-primary)] placeholder:text-[var(--text-muted)]"
          />
          {searchInput && (
            <button
              onClick={() => {
                setSearchInput('');
                clearHistorySearch();
              }}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="px-3 py-2 border-b border-[var(--border-default)] bg-[var(--surface-secondary)]">
          <div className="flex flex-wrap gap-2">
            <FilterSelect
              label="Input Type"
              value={historyFilters.inputType}
              onChange={(value) => setHistoryFilters({ inputType: value })}
              options={inputTypeOptions}
            />
            <FilterSelect
              label="Grade"
              value={historyFilters.qualityGrade}
              onChange={(value) => setHistoryFilters({ qualityGrade: value })}
              options={gradeOptions}
            />
            <FilterSelect
              label="Ready Status"
              value={historyFilters.readyStatus}
              onChange={(value) => setHistoryFilters({ readyStatus: value })}
              options={readyOptions}
            />
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="px-4 py-2 bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800">
          <p className="text-xs text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* History List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {historyEntries.length === 0 ? (
          <div className="text-center py-8">
            <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-[var(--surface-secondary)] flex items-center justify-center">
              <svg className="w-6 h-6 text-[var(--text-muted)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
              </svg>
            </div>
            <p className="text-sm text-[var(--text-muted)]">
              {historySearchQuery ? 'No results found' : 'No history yet'}
            </p>
            <p className="text-xs text-[var(--text-muted)] mt-1">
              {historySearchQuery ? 'Try a different search' : 'Analyzed requirements will appear here'}
            </p>
          </div>
        ) : (
          historyEntries.map((entry) => (
            <HistoryItem
              key={entry.sessionId}
              entry={entry}
              onLoad={handleLoad}
              onDelete={handleDelete}
              isLoading={isLoadingSession}
            />
          ))
        )}
      </div>
    </div>
  );
}
