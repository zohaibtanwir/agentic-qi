'use client';

import { useState } from 'react';
import { useTestDataStore } from '@/lib/stores/test-data-store';
import { useToastActions } from '@/components/ui/Toast';

type PreviewTab = 'json' | 'table' | 'stats';

export function DataPreview() {
  const {
    generatedData,
    lastResponse,
    isGenerating,
    clearGeneratedData,
    showUnmasked,
    setShowUnmasked,
  } = useTestDataStore();

  const toast = useToastActions();
  const [activeTab, setActiveTab] = useState<PreviewTab>('json');
  const [copied, setCopied] = useState(false);

  // Determine which data to display based on masking toggle
  const dataMasked = lastResponse?.metadata?.dataMasked;
  const displayData = dataMasked && showUnmasked && lastResponse?.unmaskedData
    ? lastResponse.unmaskedData
    : generatedData;

  const handleCopy = async () => {
    if (!displayData) return;
    try {
      await navigator.clipboard.writeText(displayData);
      setCopied(true);
      toast.success('Copied to clipboard');
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error('Failed to copy to clipboard');
    }
  };

  const handleDownload = () => {
    if (!displayData) return;
    try {
      const blob = new Blob([displayData], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const suffix = dataMasked && !showUnmasked ? '-masked' : '';
      a.download = `test-data${suffix}-${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast.success('Download started');
    } catch {
      toast.error('Failed to download file');
    }
  };

  const handleClear = () => {
    clearGeneratedData();
    toast.info('Data cleared');
  };

  // Parse data for table view
  let parsedData: Record<string, unknown>[] = [];
  let parseError = false;
  if (displayData) {
    try {
      parsedData = JSON.parse(displayData);
      if (!Array.isArray(parsedData)) {
        parsedData = [parsedData];
      }
    } catch {
      parseError = true;
    }
  }

  const tabs = [
    { id: 'json' as const, label: 'JSON' },
    { id: 'table' as const, label: 'Table' },
    { id: 'stats' as const, label: 'Stats' },
  ];

  return (
    <div className="bg-white rounded-lg border border-[var(--border-default)] shadow-sm h-full flex flex-col">
      {/* Header */}
      <div className="border-b border-[var(--border-default)]">
        <div className="flex items-center justify-between px-6 pt-4 pb-0">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">Preview</h2>
            {dataMasked && (
              <span className="inline-flex items-center gap-1 text-xs px-2 py-1 bg-[var(--accent-default)]/10 text-[var(--accent-default)] border border-[var(--accent-default)]/20 rounded">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                {lastResponse?.metadata?.fieldsMaskedCount || 0} fields masked
              </span>
            )}
          </div>
          {generatedData && (
            <div className="flex items-center gap-4">
              {/* Masked/Unmasked Toggle */}
              {dataMasked && lastResponse?.unmaskedData && (
                <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-lg">
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={showUnmasked}
                      onChange={(e) => setShowUnmasked(e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-9 h-5 bg-gray-300 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-[var(--accent-default)]/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-orange-500"></div>
                  </label>
                  <span className="text-xs font-medium text-[var(--text-secondary)] flex items-center gap-1">
                    {showUnmasked ? (
                      <>
                        <svg className="w-3 h-3 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                        </svg>
                        Unmasked
                      </>
                    ) : (
                      <>
                        <svg className="w-3 h-3 text-[var(--accent-default)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                        </svg>
                        Masked
                      </>
                    )}
                  </span>
                </div>
              )}
              <div className="flex items-center gap-2">
              <button
                onClick={handleCopy}
                className="p-2 text-gray-500 hover:text-[var(--accent-default)] transition-colors"
                title="Copy to clipboard"
              >
                {copied ? (
                  <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                )}
              </button>
              <button
                onClick={handleDownload}
                className="p-2 text-gray-500 hover:text-[var(--accent-default)] transition-colors"
                title="Download"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
              </button>
              <button
                onClick={handleClear}
                className="p-2 text-gray-500 hover:text-red-500 transition-colors"
                title="Clear"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
              </div>
            </div>
          )}
        </div>

        {/* Tab Navigation */}
        {generatedData && (
          <div className="flex px-6 pt-3">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'text-[var(--accent-default)] border-[var(--accent-default)]'
                    : 'text-[var(--text-secondary)] border-transparent hover:text-[var(--text-primary)] hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {isGenerating ? (
          <div className="flex flex-col items-center justify-center h-full">
            <div className="w-12 h-12 border-4 border-[var(--accent-default)] border-t-transparent rounded-full animate-spin mb-4" />
            <p className="text-sm text-[var(--text-muted)]">Generating test data...</p>
          </div>
        ) : generatedData ? (
          <>
            {activeTab === 'json' && (
              <pre className="bg-gray-50 rounded-lg p-4 overflow-auto max-h-[500px] text-sm font-mono text-[var(--text-secondary)]">
                {displayData}
              </pre>
            )}

            {activeTab === 'table' && !parseError && parsedData.length > 0 && (
              <div className="overflow-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      {Object.keys(parsedData[0])
                        .filter((key) => !key.startsWith('_'))
                        .map((key) => (
                          <th
                            key={key}
                            className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                          >
                            {key}
                          </th>
                        ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {parsedData.slice(0, 50).map((row, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        {Object.entries(row)
                          .filter(([key]) => !key.startsWith('_'))
                          .map(([key, value]) => (
                            <td
                              key={key}
                              className="px-3 py-2 text-sm text-gray-700 whitespace-nowrap max-w-xs truncate"
                              title={String(value)}
                            >
                              {typeof value === 'object'
                                ? JSON.stringify(value).substring(0, 30) + '...'
                                : String(value)}
                            </td>
                          ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
                {parsedData.length > 50 && (
                  <p className="text-center text-sm text-[var(--text-muted)] mt-4">
                    Showing first 50 of {parsedData.length} records
                  </p>
                )}
              </div>
            )}

            {activeTab === 'stats' && lastResponse?.metadata && (
              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="text-3xl font-bold text-[var(--accent-default)]">
                      {lastResponse.recordCount}
                    </div>
                    <div className="text-sm text-[var(--text-muted)] mt-1">
                      Records Generated
                    </div>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="text-3xl font-bold text-[var(--text-primary)]">
                      {(lastResponse.metadata.generationTimeMs / 1000).toFixed(2)}s
                    </div>
                    <div className="text-sm text-[var(--text-muted)] mt-1">
                      Generation Time
                    </div>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="text-3xl font-bold text-green-600">
                      {((lastResponse.metadata.coherenceScore || 0) * 100).toFixed(1)}%
                    </div>
                    <div className="text-sm text-[var(--text-muted)] mt-1">
                      Coherence Score
                    </div>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="text-3xl font-bold text-blue-600">
                      {lastResponse.metadata.generationPath}
                    </div>
                    <div className="text-sm text-[var(--text-muted)] mt-1">
                      Generation Method
                    </div>
                  </div>
                </div>

                {lastResponse.metadata.llmTokensUsed > 0 && (
                  <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                    <div className="flex items-center gap-2 text-blue-800 mb-2">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                      <span className="font-medium">LLM Usage</span>
                    </div>
                    <p className="text-sm text-blue-700">
                      {lastResponse.metadata.llmTokensUsed.toLocaleString()} tokens used
                    </p>
                  </div>
                )}

                {lastResponse.metadata.scenarioCounts &&
                  Object.keys(lastResponse.metadata.scenarioCounts).length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-[var(--text-primary)] mb-3">
                        Scenario Breakdown
                      </h4>
                      <div className="space-y-2">
                        {Object.entries(lastResponse.metadata.scenarioCounts).map(
                          ([name, count]) => (
                            <div
                              key={name}
                              className="flex items-center justify-between bg-gray-50 rounded px-3 py-2"
                            >
                              <span className="text-sm text-[var(--text-secondary)]">
                                {name.replace(/_/g, ' ')}
                              </span>
                              <span className="text-sm font-medium text-[var(--accent-default)]">
                                {count}
                              </span>
                            </div>
                          )
                        )}
                      </div>
                    </div>
                  )}
              </div>
            )}
          </>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <svg
              className="w-20 h-20 text-gray-200 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1}
                d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
              />
            </svg>
            <h3 className="text-lg font-medium text-[var(--text-primary)] mb-1">
              No Data Generated
            </h3>
            <p className="text-sm text-[var(--text-muted)] max-w-xs">
              Configure your options and click &quot;Generate Data&quot; to create test data
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
