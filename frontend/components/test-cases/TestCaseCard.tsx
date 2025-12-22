'use client';

import { TestCase, TestType, Priority, OutputFormat } from '@/lib/grpc/generated/test_cases';

interface TestCaseCardProps {
  testCase: TestCase;
  outputFormat: OutputFormat;
  onSelect?: (testCase: TestCase) => void;
  isSelected?: boolean;
}

const PRIORITY_COLORS: Record<Priority, string> = {
  [Priority.PRIORITY_UNSPECIFIED]: 'bg-gray-100 text-gray-600',
  [Priority.CRITICAL]: 'bg-red-100 text-red-700',
  [Priority.HIGH]: 'bg-orange-100 text-orange-700',
  [Priority.MEDIUM]: 'bg-yellow-100 text-yellow-700',
  [Priority.LOW]: 'bg-green-100 text-green-700',
  [Priority.UNRECOGNIZED]: 'bg-gray-100 text-gray-600',
};

const PRIORITY_LABELS: Record<Priority, string> = {
  [Priority.PRIORITY_UNSPECIFIED]: 'Unspecified',
  [Priority.CRITICAL]: 'Critical',
  [Priority.HIGH]: 'High',
  [Priority.MEDIUM]: 'Medium',
  [Priority.LOW]: 'Low',
  [Priority.UNRECOGNIZED]: 'Unknown',
};

const TEST_TYPE_LABELS: Record<TestType, string> = {
  [TestType.TEST_TYPE_UNSPECIFIED]: 'Unspecified',
  [TestType.FUNCTIONAL]: 'Functional',
  [TestType.NEGATIVE]: 'Negative',
  [TestType.BOUNDARY]: 'Boundary',
  [TestType.EDGE_CASE]: 'Edge Case',
  [TestType.SECURITY]: 'Security',
  [TestType.PERFORMANCE]: 'Performance',
  [TestType.INTEGRATION]: 'Integration',
  [TestType.UNIT]: 'Unit',
  [TestType.USABILITY]: 'Usability',
  [TestType.REGRESSION]: 'Regression',
  [TestType.SMOKE]: 'Smoke',
  [TestType.ACCEPTANCE]: 'Acceptance',
  [TestType.COMPATIBILITY]: 'Compatibility',
  [TestType.ACCESSIBILITY]: 'Accessibility',
  [TestType.LOCALIZATION]: 'Localization',
  [TestType.API]: 'API',
  [TestType.DATABASE]: 'Database',
  [TestType.LOAD]: 'Load',
  [TestType.STRESS]: 'Stress',
  [TestType.RECOVERY]: 'Recovery',
  [TestType.UNRECOGNIZED]: 'Unknown',
};

export function TestCaseCard({ testCase, outputFormat, onSelect, isSelected }: TestCaseCardProps) {
  const isGherkin = outputFormat === OutputFormat.GHERKIN;

  return (
    <div
      onClick={() => onSelect?.(testCase)}
      className={`bg-white rounded-lg border p-5 transition-all cursor-pointer ${
        isSelected
          ? 'border-[var(--accent-default)] ring-2 ring-[var(--accent-default)] ring-opacity-20'
          : 'border-[var(--border-default)] hover:border-[var(--accent-default)] hover:shadow-sm'
      }`}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-sm font-mono text-[var(--text-muted)]">{testCase.id}</span>
          <span className={`px-2 py-0.5 text-xs font-medium rounded ${PRIORITY_COLORS[testCase.priority]}`}>
            {PRIORITY_LABELS[testCase.priority]}
          </span>
        </div>
        <span className="px-2 py-0.5 text-xs font-medium rounded bg-[var(--bg-secondary)] text-[var(--text-secondary)]">
          {TEST_TYPE_LABELS[testCase.type]}
        </span>
      </div>

      {/* Title */}
      <h4 className="text-base font-medium text-[var(--text-primary)] mb-2">
        {testCase.title}
      </h4>

      {/* Description */}
      <p className="text-sm text-[var(--text-secondary)] mb-4 line-clamp-2">
        {testCase.description}
      </p>

      {/* Content Preview */}
      {isGherkin && testCase.gherkin ? (
        <div className="bg-[var(--bg-secondary)] rounded p-3 mb-4">
          <pre className="text-xs text-[var(--text-secondary)] font-mono whitespace-pre-wrap line-clamp-4">
            {testCase.gherkin}
          </pre>
        </div>
      ) : testCase.steps.length > 0 ? (
        <div className="space-y-2 mb-4">
          {testCase.steps.slice(0, 2).map((step, idx) => (
            <div key={idx} className="flex gap-2 text-sm">
              <span className="flex-shrink-0 w-5 h-5 rounded-full bg-[var(--bg-secondary)] text-[var(--text-muted)] flex items-center justify-center text-xs">
                {step.order}
              </span>
              <span className="text-[var(--text-secondary)] line-clamp-1">{step.action}</span>
            </div>
          ))}
          {testCase.steps.length > 2 && (
            <p className="text-xs text-[var(--text-muted)] pl-7">
              +{testCase.steps.length - 2} more steps
            </p>
          )}
        </div>
      ) : null}

      {/* Tags */}
      {testCase.tags.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {testCase.tags.slice(0, 4).map((tag, idx) => (
            <span
              key={idx}
              className="px-2 py-0.5 text-xs rounded bg-[var(--bg-secondary)] text-[var(--text-muted)]"
            >
              {tag}
            </span>
          ))}
          {testCase.tags.length > 4 && (
            <span className="px-2 py-0.5 text-xs text-[var(--text-muted)]">
              +{testCase.tags.length - 4}
            </span>
          )}
        </div>
      )}
    </div>
  );
}

export default TestCaseCard;
