'use client';

import { useState } from 'react';
import { useTestDataStore, selectTotalScenarioCount } from '@/lib/stores/test-data-store';

const predefinedScenarios = [
  { name: 'happy_path', description: 'Standard successful flow', defaultCount: 5 },
  { name: 'edge_case', description: 'Boundary and edge conditions', defaultCount: 3 },
  { name: 'error_handling', description: 'Error conditions and failures', defaultCount: 2 },
  { name: 'empty_state', description: 'Empty or null values', defaultCount: 2 },
  { name: 'performance', description: 'High-volume stress testing', defaultCount: 10 },
];

export function ScenariosTab() {
  const {
    scenarios,
    addScenario,
    updateScenario,
    removeScenario,
    clearScenarios,
  } = useTestDataStore();

  const totalCount = useTestDataStore(selectTotalScenarioCount);
  const [customName, setCustomName] = useState('');

  const handleAddPredefined = (predefined: typeof predefinedScenarios[0]) => {
    // Check if already added
    if (scenarios.some((s) => s.name === predefined.name)) {
      return;
    }
    addScenario({
      name: predefined.name,
      count: predefined.defaultCount,
      description: predefined.description,
      overrides: {},
    });
  };

  const handleAddCustom = () => {
    if (!customName.trim()) return;

    const name = customName.trim().toLowerCase().replace(/\s+/g, '_');
    if (scenarios.some((s) => s.name === name)) {
      return;
    }

    addScenario({
      name,
      count: 3,
      description: 'Custom scenario',
      overrides: {},
    });
    setCustomName('');
  };

  return (
    <div className="space-y-6">
      {/* Info Banner */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex gap-3">
          <svg className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <p className="text-sm text-blue-800">
              <strong>Scenarios</strong> let you generate data with specific characteristics.
              Each scenario defines how many records of that type to generate.
            </p>
            {scenarios.length > 0 && (
              <p className="text-sm text-blue-700 mt-1">
                Total: <strong>{totalCount}</strong> records across {scenarios.length} scenario(s)
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Quick Add Predefined */}
      <div>
        <h4 className="text-sm font-medium text-[var(--text-primary)] mb-3">
          Quick Add Scenarios
        </h4>
        <div className="flex flex-wrap gap-2">
          {predefinedScenarios.map((predefined) => {
            const isAdded = scenarios.some((s) => s.name === predefined.name);
            return (
              <button
                key={predefined.name}
                onClick={() => handleAddPredefined(predefined)}
                disabled={isAdded}
                className={`px-3 py-1.5 text-sm rounded-full border transition-colors ${
                  isAdded
                    ? 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed'
                    : 'bg-white text-[var(--text-secondary)] border-[var(--border-default)] hover:border-[var(--accent-default)] hover:text-[var(--accent-default)]'
                }`}
              >
                + {predefined.name.replace(/_/g, ' ')}
              </button>
            );
          })}
        </div>
      </div>

      {/* Custom Scenario Input */}
      <div>
        <h4 className="text-sm font-medium text-[var(--text-primary)] mb-2">
          Add Custom Scenario
        </h4>
        <div className="flex gap-2">
          <input
            type="text"
            value={customName}
            onChange={(e) => setCustomName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAddCustom()}
            placeholder="e.g., holiday_sale"
            className="flex-1 px-3 py-2 border border-[var(--border-default)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--accent-default)] focus:border-transparent"
          />
          <button
            onClick={handleAddCustom}
            disabled={!customName.trim()}
            className="px-4 py-2 bg-[var(--accent-default)] text-white rounded-lg font-medium hover:bg-[var(--accent-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Add
          </button>
        </div>
      </div>

      {/* Added Scenarios List */}
      {scenarios.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-[var(--text-primary)]">
              Active Scenarios
            </h4>
            <button
              onClick={clearScenarios}
              className="text-xs text-red-600 hover:text-red-700 font-medium"
            >
              Clear All
            </button>
          </div>

          <div className="space-y-3">
            {scenarios.map((scenario) => (
              <div
                key={scenario.id}
                className="bg-gray-50 rounded-lg p-4 border border-[var(--border-default)]"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-[var(--text-primary)]">
                        {scenario.name.replace(/_/g, ' ')}
                      </span>
                      <span className="text-xs text-[var(--text-muted)]">
                        {scenario.description}
                      </span>
                    </div>

                    {/* Count Slider */}
                    <div className="flex items-center gap-3 mt-2">
                      <span className="text-xs text-[var(--text-muted)] w-16">
                        Count:
                      </span>
                      <input
                        type="range"
                        min={1}
                        max={50}
                        value={scenario.count}
                        onChange={(e) =>
                          updateScenario(scenario.id, {
                            count: parseInt(e.target.value, 10),
                          })
                        }
                        className="flex-1 h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[var(--accent-default)]"
                      />
                      <span className="text-sm font-medium text-[var(--accent-default)] w-8 text-right">
                        {scenario.count}
                      </span>
                    </div>
                  </div>

                  <button
                    onClick={() => removeScenario(scenario.id)}
                    className="p-1.5 text-gray-400 hover:text-red-500 transition-colors"
                    title="Remove scenario"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {scenarios.length === 0 && (
        <div className="text-center py-8 text-[var(--text-muted)]">
          <svg className="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          <p className="text-sm">No scenarios added yet.</p>
          <p className="text-xs mt-1">
            Add scenarios to generate targeted test data.
          </p>
        </div>
      )}
    </div>
  );
}
