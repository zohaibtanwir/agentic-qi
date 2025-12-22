'use client';

import { OutputFormat, CoverageLevel, TestType } from '@/lib/grpc/generated/test_cases';

interface ConfigPanelProps {
  outputFormat: OutputFormat;
  coverageLevel: CoverageLevel;
  testTypes: TestType[];
  maxTestCases: number;
  onOutputFormatChange: (format: OutputFormat) => void;
  onCoverageLevelChange: (level: CoverageLevel) => void;
  onTestTypesChange: (types: TestType[]) => void;
  onMaxTestCasesChange: (max: number) => void;
}

const TEST_TYPE_OPTIONS: { value: TestType; label: string; category: string }[] = [
  // Functional
  { value: TestType.FUNCTIONAL, label: 'Functional', category: 'Functional' },
  { value: TestType.ACCEPTANCE, label: 'Acceptance', category: 'Functional' },
  { value: TestType.SMOKE, label: 'Smoke', category: 'Functional' },
  { value: TestType.REGRESSION, label: 'Regression', category: 'Functional' },
  // Risk-Based
  { value: TestType.NEGATIVE, label: 'Negative', category: 'Risk-Based' },
  { value: TestType.BOUNDARY, label: 'Boundary', category: 'Risk-Based' },
  { value: TestType.EDGE_CASE, label: 'Edge Case', category: 'Risk-Based' },
  // Technical
  { value: TestType.UNIT, label: 'Unit', category: 'Technical' },
  { value: TestType.INTEGRATION, label: 'Integration', category: 'Technical' },
  { value: TestType.API, label: 'API', category: 'Technical' },
  { value: TestType.DATABASE, label: 'Database', category: 'Technical' },
  // Quality
  { value: TestType.SECURITY, label: 'Security', category: 'Quality' },
  { value: TestType.USABILITY, label: 'Usability', category: 'Quality' },
  { value: TestType.ACCESSIBILITY, label: 'Accessibility', category: 'Quality' },
  { value: TestType.LOCALIZATION, label: 'Localization', category: 'Quality' },
  // Performance
  { value: TestType.PERFORMANCE, label: 'Performance', category: 'Performance' },
  { value: TestType.LOAD, label: 'Load', category: 'Performance' },
  { value: TestType.STRESS, label: 'Stress', category: 'Performance' },
  { value: TestType.RECOVERY, label: 'Recovery', category: 'Performance' },
  // Compatibility
  { value: TestType.COMPATIBILITY, label: 'Compatibility', category: 'Compatibility' },
];

const categories = ['Functional', 'Risk-Based', 'Technical', 'Quality', 'Performance', 'Compatibility'];

export function ConfigPanel({
  outputFormat,
  coverageLevel,
  testTypes,
  maxTestCases,
  onOutputFormatChange,
  onCoverageLevelChange,
  onTestTypesChange,
  onMaxTestCasesChange,
}: ConfigPanelProps) {
  const toggleTestType = (type: TestType) => {
    if (testTypes.includes(type)) {
      onTestTypesChange(testTypes.filter(t => t !== type));
    } else {
      onTestTypesChange([...testTypes, type]);
    }
  };

  const selectAllInCategory = (category: string) => {
    const categoryTypes = TEST_TYPE_OPTIONS.filter(t => t.category === category).map(t => t.value);
    const allSelected = categoryTypes.every(t => testTypes.includes(t));

    if (allSelected) {
      onTestTypesChange(testTypes.filter(t => !categoryTypes.includes(t)));
    } else {
      const newTypes = [...testTypes];
      categoryTypes.forEach(t => {
        if (!newTypes.includes(t)) newTypes.push(t);
      });
      onTestTypesChange(newTypes);
    }
  };

  return (
    <div className="bg-[var(--bg-secondary)] rounded-lg p-6 space-y-6">
      <h3 className="text-lg font-semibold text-[var(--text-primary)]">Generation Settings</h3>

      {/* Output Format */}
      <div>
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-3">
          Output Format
        </label>
        <div className="grid grid-cols-3 gap-2">
          {[
            { value: OutputFormat.TRADITIONAL, label: 'Traditional', desc: 'Step-by-step format' },
            { value: OutputFormat.GHERKIN, label: 'Gherkin', desc: 'BDD format (Given/When/Then)' },
            { value: OutputFormat.JSON, label: 'JSON', desc: 'Machine-readable format' },
          ].map(option => (
            <button
              key={option.value}
              type="button"
              onClick={() => onOutputFormatChange(option.value)}
              className={`p-3 rounded-lg border text-left transition-all ${
                outputFormat === option.value
                  ? 'border-[var(--accent-default)] bg-white ring-2 ring-[var(--accent-default)] ring-opacity-20'
                  : 'border-[var(--border-default)] bg-white hover:border-[var(--accent-default)]'
              }`}
            >
              <div className="text-sm font-medium text-[var(--text-primary)]">{option.label}</div>
              <div className="text-xs text-[var(--text-muted)] mt-1">{option.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Coverage Level */}
      <div>
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-3">
          Coverage Level
        </label>
        <div className="grid grid-cols-3 gap-2">
          {[
            { value: CoverageLevel.QUICK, label: 'Quick', desc: 'Happy path + critical negatives' },
            { value: CoverageLevel.STANDARD, label: 'Standard', desc: 'Comprehensive coverage' },
            { value: CoverageLevel.EXHAUSTIVE, label: 'Exhaustive', desc: 'All scenarios & edge cases' },
          ].map(option => (
            <button
              key={option.value}
              type="button"
              onClick={() => onCoverageLevelChange(option.value)}
              className={`p-3 rounded-lg border text-left transition-all ${
                coverageLevel === option.value
                  ? 'border-[var(--accent-default)] bg-white ring-2 ring-[var(--accent-default)] ring-opacity-20'
                  : 'border-[var(--border-default)] bg-white hover:border-[var(--accent-default)]'
              }`}
            >
              <div className="text-sm font-medium text-[var(--text-primary)]">{option.label}</div>
              <div className="text-xs text-[var(--text-muted)] mt-1">{option.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Max Test Cases */}
      <div>
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
          Maximum Test Cases: <span className="text-[var(--accent-default)]">{maxTestCases}</span>
        </label>
        <input
          type="range"
          min={1}
          max={50}
          value={maxTestCases}
          onChange={(e) => onMaxTestCasesChange(parseInt(e.target.value))}
          className="w-full h-2 bg-[var(--border-default)] rounded-lg appearance-none cursor-pointer accent-[var(--accent-default)]"
        />
        <div className="flex justify-between text-xs text-[var(--text-muted)] mt-1">
          <span>1</span>
          <span>25</span>
          <span>50</span>
        </div>
      </div>

      {/* Test Types */}
      <div>
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-3">
          Test Types ({testTypes.length} selected)
        </label>
        <div className="space-y-4">
          {categories.map(category => {
            const categoryTypes = TEST_TYPE_OPTIONS.filter(t => t.category === category);
            const selectedCount = categoryTypes.filter(t => testTypes.includes(t.value)).length;

            return (
              <div key={category}>
                <button
                  type="button"
                  onClick={() => selectAllInCategory(category)}
                  className="text-xs font-medium text-[var(--text-muted)] hover:text-[var(--accent-default)] mb-2 flex items-center gap-1"
                >
                  {category}
                  <span className="text-[var(--accent-default)]">
                    ({selectedCount}/{categoryTypes.length})
                  </span>
                </button>
                <div className="flex flex-wrap gap-2">
                  {categoryTypes.map(option => (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => toggleTestType(option.value)}
                      className={`px-3 py-1.5 text-sm rounded-full border transition-all ${
                        testTypes.includes(option.value)
                          ? 'bg-[var(--accent-default)] text-white border-[var(--accent-default)]'
                          : 'bg-white text-[var(--text-secondary)] border-[var(--border-default)] hover:border-[var(--accent-default)]'
                      }`}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default ConfigPanel;
