'use client';

import { useState } from 'react';
import { useEcommerceStore, type GenerationMethod, type HistoryEntry } from '@/lib/stores/ecommerce-store';

const GENERATION_METHODS: { id: GenerationMethod; label: string; description: string }[] = [
  { id: 'LLM', label: 'LLM', description: 'AI-powered intelligent generation using Claude' },
  { id: 'TRADITIONAL', label: 'Traditional', description: 'Rule-based generation using Faker patterns' },
  { id: 'RAG', label: 'RAG', description: 'Knowledge-enhanced generation using domain context' },
  { id: 'HYBRID', label: 'Hybrid', description: 'Combines LLM with traditional methods' },
];

export function GenerateView() {
  const entities = useEcommerceStore((state) => state.entities);
  const workflows = useEcommerceStore((state) => state.workflows);
  const generateForm = useEcommerceStore((state) => state.generateForm);
  const updateGenerateForm = useEcommerceStore((state) => state.updateGenerateForm);
  const generatedData = useEcommerceStore((state) => state.generatedData);
  const isGenerating = useEcommerceStore((state) => state.isGenerating);
  const generateTestData = useEcommerceStore((state) => state.generateTestData);
  const historyEntries = useEcommerceStore((state) => state.historyEntries);
  const deleteHistoryEntry = useEcommerceStore((state) => state.deleteHistoryEntry);

  // State for expanded history entry
  const [expandedEntryId, setExpandedEntryId] = useState<string | null>(null);

  const toggleHistoryEntry = (entryId: string) => {
    setExpandedEntryId(expandedEntryId === entryId ? null : entryId);
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (generateForm.entity) {
      await generateTestData();
    }
  };

  // Helper to format JSON data for display
  const formatJsonData = (data: string): string => {
    try {
      // Parse and re-stringify for pretty formatting
      const parsed = JSON.parse(data);
      return JSON.stringify(parsed, null, 2);
    } catch {
      // If not valid JSON, return as-is
      return data;
    }
  };

  const copyToClipboard = () => {
    if (generatedData) {
      navigator.clipboard.writeText(formatJsonData(generatedData));
    }
  };

  const downloadJson = () => {
    if (generatedData) {
      const blob = new Blob([formatJsonData(generatedData)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${generateForm.entity || 'test-data'}-${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Generation Form */}
        <div className="bg-[var(--surface-primary)] border border-[var(--border-default)] rounded-xl overflow-hidden">
          <div className="p-4 border-b border-[var(--border-default)]">
            <h3 className="font-semibold text-[var(--text-primary)]">Generate Test Data</h3>
          </div>
          <form onSubmit={handleGenerate} className="p-4 space-y-4">
            {/* Entity Selection */}
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                Entity Type <span className="text-red-500">*</span>
              </label>
              <select
                value={generateForm.entity}
                onChange={(e) => updateGenerateForm({ entity: e.target.value })}
                className="w-full px-4 py-2.5 bg-[var(--surface-secondary)] border border-[var(--border-default)] rounded-lg text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-default)] focus:border-transparent"
                required
              >
                <option value="">Select an entity...</option>
                {entities.map((entity) => (
                  <option key={entity.name} value={entity.name}>
                    {entity.name.charAt(0).toUpperCase() + entity.name.slice(1)} - {entity.description}
                  </option>
                ))}
              </select>
            </div>

            {/* Workflow Context (Optional) */}
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                Workflow Context (Optional)
              </label>
              <select
                value={generateForm.workflow || ''}
                onChange={(e) => updateGenerateForm({ workflow: e.target.value || undefined })}
                className="w-full px-4 py-2.5 bg-[var(--surface-secondary)] border border-[var(--border-default)] rounded-lg text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-default)] focus:border-transparent"
              >
                <option value="">No workflow context</option>
                {workflows.map((workflow) => (
                  <option key={workflow.name} value={workflow.name}>
                    {workflow.name.charAt(0).toUpperCase() + workflow.name.slice(1)} Flow
                  </option>
                ))}
              </select>
              <p className="mt-1 text-xs text-[var(--text-muted)]">
                Selecting a workflow will generate data optimized for that business flow
              </p>
            </div>

            {/* Record Count */}
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                Number of Records
              </label>
              <input
                type="number"
                min="1"
                max="100"
                value={generateForm.count}
                onChange={(e) => updateGenerateForm({ count: parseInt(e.target.value) || 1 })}
                className="w-full px-4 py-2.5 bg-[var(--surface-secondary)] border border-[var(--border-default)] rounded-lg text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-default)] focus:border-transparent"
              />
            </div>

            {/* Generation Method */}
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                Generation Method
              </label>
              <div className="grid grid-cols-2 gap-2">
                {GENERATION_METHODS.map((method) => (
                  <button
                    key={method.id}
                    type="button"
                    onClick={() => updateGenerateForm({ generationMethod: method.id })}
                    className={`p-3 text-left rounded-lg border transition-colors ${
                      (generateForm.generationMethod ?? 'LLM') === method.id
                        ? 'bg-[var(--accent-default)]/10 border-[var(--accent-default)] text-[var(--accent-default)]'
                        : 'bg-[var(--surface-secondary)] border-[var(--border-default)] text-[var(--text-secondary)] hover:border-[var(--accent-default)]/50'
                    }`}
                  >
                    <div className="font-medium text-sm">{method.label}</div>
                    <div className="text-xs mt-0.5 opacity-80">{method.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Custom Context */}
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                Additional Context (Optional)
              </label>
              <textarea
                value={generateForm.customContext}
                onChange={(e) => updateGenerateForm({ customContext: e.target.value })}
                rows={3}
                placeholder="Provide additional context for data generation, e.g., 'Generate data for a Black Friday sale scenario with high-value orders'"
                className="w-full px-4 py-2.5 bg-[var(--surface-secondary)] border border-[var(--border-default)] rounded-lg text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-default)] focus:border-transparent resize-none"
              />
              <p className="mt-1 text-xs text-[var(--text-muted)]">
                This context helps the AI generate more relevant and realistic test data
              </p>
            </div>

            {/* Options */}
            <div className="space-y-3">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={generateForm.includeEdgeCases ?? false}
                  onChange={(e) => updateGenerateForm({ includeEdgeCases: e.target.checked })}
                  className="w-4 h-4 rounded border-[var(--border-default)] text-[var(--accent-default)] focus:ring-[var(--accent-default)]"
                />
                <div>
                  <span className="text-sm font-medium text-[var(--text-primary)]">Include Edge Cases</span>
                  <p className="text-xs text-[var(--text-muted)]">Generate data that covers boundary conditions and edge cases</p>
                </div>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={generateForm.includeRelationships ?? false}
                  onChange={(e) => updateGenerateForm({ includeRelationships: e.target.checked })}
                  className="w-4 h-4 rounded border-[var(--border-default)] text-[var(--accent-default)] focus:ring-[var(--accent-default)]"
                />
                <div>
                  <span className="text-sm font-medium text-[var(--text-primary)]">Include Related Entities</span>
                  <p className="text-xs text-[var(--text-muted)]">Generate related entity data with proper references</p>
                </div>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={generateForm.validateRules ?? true}
                  onChange={(e) => updateGenerateForm({ validateRules: e.target.checked })}
                  className="w-4 h-4 rounded border-[var(--border-default)] text-[var(--accent-default)] focus:ring-[var(--accent-default)]"
                />
                <div>
                  <span className="text-sm font-medium text-[var(--text-primary)]">Validate Business Rules</span>
                  <p className="text-xs text-[var(--text-muted)]">Ensure generated data complies with business rules</p>
                </div>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={generateForm.productionLike ?? true}
                  onChange={(e) => updateGenerateForm({ productionLike: e.target.checked })}
                  className="w-4 h-4 rounded border-[var(--border-default)] text-[var(--accent-default)] focus:ring-[var(--accent-default)]"
                />
                <div>
                  <span className="text-sm font-medium text-[var(--text-primary)]">Production-like Distribution</span>
                  <p className="text-xs text-[var(--text-muted)]">Mimic realistic production data patterns and distributions</p>
                </div>
              </label>
            </div>

            {/* Generate Button */}
            <button
              type="submit"
              disabled={isGenerating || !generateForm.entity}
              className="w-full px-6 py-3 bg-[var(--accent-default)] text-white rounded-lg font-medium hover:bg-[var(--accent-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
            >
              {isGenerating ? (
                <>
                  <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Generating...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Generate Test Data
                </>
              )}
            </button>
          </form>
        </div>

        {/* Generated Data Preview */}
        <div className="bg-[var(--surface-primary)] border border-[var(--border-default)] rounded-xl overflow-hidden">
          <div className="p-4 border-b border-[var(--border-default)] flex items-center justify-between">
            <h3 className="font-semibold text-[var(--text-primary)]">Generated Data</h3>
            {generatedData && (
              <div className="flex items-center gap-2">
                <button
                  onClick={copyToClipboard}
                  className="p-2 text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-secondary)] rounded-lg transition-colors"
                  title="Copy to clipboard"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </button>
                <button
                  onClick={downloadJson}
                  className="p-2 text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-secondary)] rounded-lg transition-colors"
                  title="Download JSON"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                </button>
              </div>
            )}
          </div>
          <div className="max-h-[500px] overflow-auto p-4">
            {!generatedData ? (
              <div className="text-center text-[var(--text-muted)] py-8">
                Configure options and click Generate to create test data
              </div>
            ) : (
              <pre className="text-sm text-[var(--text-secondary)] font-mono whitespace-pre-wrap">
                {formatJsonData(generatedData)}
              </pre>
            )}
          </div>
        </div>
      </div>

      {/* Generation History */}
      {historyEntries.length > 0 && (
        <div className="bg-[var(--surface-primary)] border border-[var(--border-default)] rounded-xl overflow-hidden">
          <div className="p-4 border-b border-[var(--border-default)]">
            <h3 className="font-semibold text-[var(--text-primary)]">Generation History</h3>
            <p className="text-xs text-[var(--text-muted)] mt-1">Click on an entry to view details</p>
          </div>
          <div className="divide-y divide-[var(--border-default)]">
            {historyEntries.map((entry) => (
              <div key={entry.id}>
                {/* History Row - Clickable */}
                <div
                  onClick={() => toggleHistoryEntry(entry.id)}
                  className={`flex items-center justify-between px-4 py-3 cursor-pointer transition-colors ${
                    expandedEntryId === entry.id
                      ? 'bg-[var(--accent-default)]/5'
                      : 'hover:bg-[var(--surface-secondary)]'
                  }`}
                >
                  <div className="flex items-center gap-4 flex-1 min-w-0">
                    {/* Expand Icon */}
                    <svg
                      className={`w-4 h-4 text-[var(--text-muted)] transition-transform flex-shrink-0 ${
                        expandedEntryId === entry.id ? 'rotate-90' : ''
                      }`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>

                    {/* Entity */}
                    <span className="text-sm text-[var(--text-primary)] font-medium capitalize min-w-[100px]">
                      {entry.entity}
                    </span>

                    {/* Records */}
                    <span className="text-sm text-[var(--text-secondary)] min-w-[80px]">
                      {entry.recordCount} records
                    </span>

                    {/* Workflow */}
                    <span className="text-sm text-[var(--text-muted)] capitalize min-w-[100px]">
                      {entry.workflow || 'No workflow'}
                    </span>

                    {/* Options Tags */}
                    <div className="flex flex-wrap gap-1 flex-1">
                      {entry.includeEdgeCases && (
                        <span className="text-xs px-2 py-0.5 bg-orange-100 text-orange-700 rounded">Edge Cases</span>
                      )}
                      {entry.includeRelationships && (
                        <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded">Relationships</span>
                      )}
                      {entry.validateRules && (
                        <span className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded">Validated</span>
                      )}
                    </div>
                  </div>

                  {/* Timestamp & Delete */}
                  <div className="flex items-center gap-3 flex-shrink-0">
                    <span className="text-xs text-[var(--text-muted)]">
                      {new Date(entry.timestamp).toLocaleString()}
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteHistoryEntry(entry.id);
                      }}
                      className="p-1 text-[var(--text-muted)] hover:text-red-500 hover:bg-red-50 rounded transition-colors"
                      title="Delete entry"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>

                {/* Expanded Details Panel */}
                {expandedEntryId === entry.id && (
                  <div className="bg-[var(--surface-secondary)] border-t border-[var(--border-default)] p-4">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                      {/* Input Parameters */}
                      <div className="bg-[var(--surface-primary)] rounded-lg p-4 border border-[var(--border-default)]">
                        <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-3 flex items-center gap-2">
                          <svg className="w-4 h-4 text-[var(--accent-default)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                          Input Parameters
                        </h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-[var(--text-muted)]">Entity:</span>
                            <span className="text-[var(--text-primary)] font-medium capitalize">{entry.entity}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-[var(--text-muted)]">Requested Count:</span>
                            <span className="text-[var(--text-primary)]">{entry.count}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-[var(--text-muted)]">Generated Count:</span>
                            <span className="text-[var(--text-primary)]">{entry.recordCount}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-[var(--text-muted)]">Workflow:</span>
                            <span className="text-[var(--text-primary)] capitalize">{entry.workflow || 'None'}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-[var(--text-muted)]">Edge Cases:</span>
                            <span className={entry.includeEdgeCases ? 'text-green-600' : 'text-[var(--text-muted)]'}>
                              {entry.includeEdgeCases ? 'Yes' : 'No'}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-[var(--text-muted)]">Relationships:</span>
                            <span className={entry.includeRelationships ? 'text-green-600' : 'text-[var(--text-muted)]'}>
                              {entry.includeRelationships ? 'Yes' : 'No'}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-[var(--text-muted)]">Validated:</span>
                            <span className={entry.validateRules ? 'text-green-600' : 'text-[var(--text-muted)]'}>
                              {entry.validateRules ? 'Yes' : 'No'}
                            </span>
                          </div>
                          {entry.customContext && (
                            <div className="mt-3 pt-3 border-t border-[var(--border-default)]">
                              <span className="text-[var(--text-muted)] block mb-1">Additional Context:</span>
                              <p className="text-xs text-[var(--text-secondary)] bg-[var(--surface-secondary)] p-2 rounded italic">
                                &ldquo;{entry.customContext}&rdquo;
                              </p>
                            </div>
                          )}
                          {entry.domainContext && (
                            <div className="mt-3 pt-3 border-t border-[var(--border-default)]">
                              <span className="text-[var(--text-muted)] block mb-1">Domain Context:</span>
                              <p className="text-xs text-[var(--text-secondary)] bg-[var(--surface-secondary)] p-2 rounded">
                                {entry.domainContext}
                              </p>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Generated Data */}
                      <div className="bg-[var(--surface-primary)] rounded-lg p-4 border border-[var(--border-default)]">
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="text-sm font-semibold text-[var(--text-primary)] flex items-center gap-2">
                            <svg className="w-4 h-4 text-[var(--accent-default)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                            </svg>
                            Generated Data
                          </h4>
                          <div className="flex items-center gap-1">
                            <button
                              onClick={() => {
                                navigator.clipboard.writeText(formatJsonData(entry.data));
                              }}
                              className="p-1.5 text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-secondary)] rounded transition-colors"
                              title="Copy to clipboard"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                              </svg>
                            </button>
                            <button
                              onClick={() => {
                                const blob = new Blob([formatJsonData(entry.data)], { type: 'application/json' });
                                const url = URL.createObjectURL(blob);
                                const a = document.createElement('a');
                                a.href = url;
                                a.download = `${entry.entity}-${entry.timestamp}.json`;
                                document.body.appendChild(a);
                                a.click();
                                document.body.removeChild(a);
                                URL.revokeObjectURL(url);
                              }}
                              className="p-1.5 text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-secondary)] rounded transition-colors"
                              title="Download JSON"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                              </svg>
                            </button>
                          </div>
                        </div>
                        <div className="max-h-[300px] overflow-auto">
                          <pre className="text-xs text-[var(--text-secondary)] font-mono whitespace-pre-wrap bg-[var(--surface-secondary)] p-3 rounded">
                            {formatJsonData(entry.data)}
                          </pre>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
