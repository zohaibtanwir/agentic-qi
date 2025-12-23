'use client';

import { useTestDataStore, type HistoryEntry } from '@/lib/stores/test-data-store';
import { GenerationMethod, OutputFormat } from '@/lib/grpc/testDataClient';

function formatTimestamp(timestamp: number): string {
  const date = new Date(timestamp);
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

function getMethodLabel(method: GenerationMethod): string {
  switch (method) {
    case GenerationMethod.TRADITIONAL:
      return 'Traditional';
    case GenerationMethod.LLM:
      return 'LLM';
    case GenerationMethod.RAG:
      return 'RAG';
    case GenerationMethod.HYBRID:
      return 'Hybrid';
    default:
      return 'Unknown';
  }
}

function getFormatLabel(format: OutputFormat): string {
  switch (format) {
    case OutputFormat.JSON:
      return 'JSON';
    case OutputFormat.CSV:
      return 'CSV';
    case OutputFormat.SQL:
      return 'SQL';
    default:
      return 'Unknown';
  }
}

interface HistoryItemProps {
  entry: HistoryEntry;
  onLoad: (id: string) => void;
  onDelete: (id: string) => void;
}

function HistoryItem({ entry, onLoad, onDelete }: HistoryItemProps) {
  return (
    <div
      className="p-3 bg-[var(--surface-secondary)] rounded-lg border border-[var(--border-default)] hover:border-[var(--accent-default)] transition-colors cursor-pointer group"
      onClick={() => onLoad(entry.id)}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-medium text-[var(--text-primary)] capitalize truncate">
              {entry.entity}
            </span>
            <span className="text-xs px-1.5 py-0.5 bg-[var(--surface-tertiary)] rounded text-[var(--text-muted)]">
              {entry.recordCount}
            </span>
          </div>
          <div className="flex items-center gap-2 mt-1 text-xs text-[var(--text-muted)]">
            <span>{getMethodLabel(entry.generationMethod)}</span>
            <span>•</span>
            <span>{getFormatLabel(entry.outputFormat)}</span>
          </div>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete(entry.id);
          }}
          className="opacity-0 group-hover:opacity-100 p-1 text-[var(--text-muted)] hover:text-red-500 transition-all"
          title="Delete"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
      <div className="flex items-center justify-between mt-2 text-xs text-[var(--text-muted)]">
        <span>{formatTimestamp(entry.timestamp)}</span>
        {entry.coherenceScore > 0 && (
          <span className="text-green-600">{Math.round(entry.coherenceScore * 100)}% coherent</span>
        )}
      </div>
    </div>
  );
}

export function HistorySidebar() {
  const historyEntries = useTestDataStore((state) => state.historyEntries);
  const loadHistoryEntry = useTestDataStore((state) => state.loadHistoryEntry);
  const deleteHistoryEntry = useTestDataStore((state) => state.deleteHistoryEntry);
  const clearHistory = useTestDataStore((state) => state.clearHistory);

  if (historyEntries.length === 0) {
    return (
      <div className="p-4 text-center">
        <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-[var(--surface-secondary)] flex items-center justify-center">
          <svg className="w-6 h-6 text-[var(--text-muted)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <p className="text-sm text-[var(--text-muted)]">No history yet</p>
        <p className="text-xs text-[var(--text-muted)] mt-1">Generated data will appear here</p>
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
            {historyEntries.length}
          </span>
        </div>
        <button
          onClick={clearHistory}
          className="text-xs text-[var(--text-muted)] hover:text-red-500 transition-colors"
          title="Clear all history"
        >
          Clear
        </button>
      </div>
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {historyEntries.map((entry) => (
          <HistoryItem
            key={entry.id}
            entry={entry}
            onLoad={loadHistoryEntry}
            onDelete={deleteHistoryEntry}
          />
        ))}
      </div>
    </div>
  );
}
