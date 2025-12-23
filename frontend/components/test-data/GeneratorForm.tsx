'use client';

import { useTestDataStore } from '@/lib/stores/test-data-store';
import { BasicConfigTab } from './BasicConfigTab';
import { ScenariosTab } from './ScenariosTab';
import { OutputTab } from './OutputTab';

const tabs = [
  { id: 'options' as const, label: 'Options' },
  { id: 'scenarios' as const, label: 'Scenarios' },
  { id: 'output' as const, label: 'Output' },
];

export function GeneratorForm() {
  const {
    activeGeneratorTab,
    setActiveGeneratorTab,
    generateData,
    isGenerating,
    scenarios,
  } = useTestDataStore();

  const scenarioCount = scenarios.length;

  return (
    <div className="bg-white rounded-lg border border-[var(--border-default)] shadow-sm h-full flex flex-col">
      {/* Header with Tabs */}
      <div className="border-b border-[var(--border-default)]">
        <div className="flex items-center justify-between px-6 pt-4 pb-0">
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">
            Configuration
          </h2>
        </div>

        {/* Tab Navigation */}
        <div className="flex px-6 pt-3">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveGeneratorTab(tab.id)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors relative ${
                activeGeneratorTab === tab.id
                  ? 'text-[var(--accent-default)] border-[var(--accent-default)]'
                  : 'text-[var(--text-secondary)] border-transparent hover:text-[var(--text-primary)] hover:border-gray-300'
              }`}
            >
              {tab.label}
              {tab.id === 'scenarios' && scenarioCount > 0 && (
                <span className="ml-2 px-1.5 py-0.5 text-xs bg-[var(--accent-default)] text-white rounded-full">
                  {scenarioCount}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-auto p-6">
        {activeGeneratorTab === 'options' && <BasicConfigTab />}
        {activeGeneratorTab === 'scenarios' && <ScenariosTab />}
        {activeGeneratorTab === 'output' && <OutputTab />}
      </div>

      {/* Generate Button */}
      <div className="p-6 border-t border-[var(--border-default)]">
        <button
          onClick={() => generateData()}
          disabled={isGenerating}
          className="w-full py-3 px-4 bg-[var(--accent-default)] text-white font-semibold rounded-lg hover:bg-[var(--accent-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
        >
          {isGenerating ? (
            <>
              <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Generating...
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Generate Data
            </>
          )}
        </button>
      </div>
    </div>
  );
}
