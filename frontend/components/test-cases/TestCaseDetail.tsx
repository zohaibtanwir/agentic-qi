'use client';

import { TestCase, TestType, Priority, OutputFormat } from '@/lib/grpc/generated/test_cases';

interface TestCaseDetailProps {
  testCase: TestCase;
  outputFormat: OutputFormat;
  onClose: () => void;
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

export function TestCaseDetail({ testCase, outputFormat, onClose }: TestCaseDetailProps) {
  const isGherkin = outputFormat === OutputFormat.GHERKIN;

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const exportTestCase = () => {
    const content = isGherkin ? testCase.gherkin : JSON.stringify(testCase, null, 2);
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${testCase.id}.${isGherkin ? 'feature' : 'json'}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-[var(--border-default)]">
          <div className="flex items-center gap-3">
            <span className="text-lg font-mono text-[var(--text-muted)]">{testCase.id}</span>
            <span className={`px-2 py-1 text-sm font-medium rounded ${PRIORITY_COLORS[testCase.priority]}`}>
              {PRIORITY_LABELS[testCase.priority]}
            </span>
            <span className="px-2 py-1 text-sm font-medium rounded bg-[var(--bg-secondary)] text-[var(--text-secondary)]">
              {TEST_TYPE_LABELS[testCase.type]}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={exportTestCase}
              className="px-3 py-1.5 text-sm text-[var(--text-secondary)] hover:text-[var(--accent-default)] flex items-center gap-1"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Export
            </button>
            <button
              onClick={onClose}
              className="p-2 text-[var(--text-muted)] hover:text-[var(--text-primary)] rounded-lg hover:bg-[var(--bg-secondary)]"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Title & Description */}
          <div>
            <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-2">
              {testCase.title}
            </h2>
            <p className="text-[var(--text-secondary)]">{testCase.description}</p>
          </div>

          {/* Tags */}
          {testCase.tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {testCase.tags.map((tag, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 text-sm rounded-full bg-[var(--bg-secondary)] text-[var(--text-secondary)]"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}

          {/* Preconditions */}
          {testCase.preconditions.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-2 uppercase tracking-wide">
                Preconditions
              </h3>
              <ul className="list-disc list-inside space-y-1 text-[var(--text-secondary)]">
                {testCase.preconditions.map((pre, idx) => (
                  <li key={idx}>{pre}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Test Content */}
          {isGherkin && testCase.gherkin ? (
            <div>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-[var(--text-primary)] uppercase tracking-wide">
                  Gherkin Scenario
                </h3>
                <button
                  onClick={() => copyToClipboard(testCase.gherkin)}
                  className="text-xs text-[var(--accent-default)] hover:underline"
                >
                  Copy to clipboard
                </button>
              </div>
              <div className="bg-[var(--bg-secondary)] rounded-lg p-4">
                <pre className="text-sm text-[var(--text-secondary)] font-mono whitespace-pre-wrap">
                  {testCase.gherkin}
                </pre>
              </div>
            </div>
          ) : testCase.steps.length > 0 ? (
            <div>
              <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-3 uppercase tracking-wide">
                Test Steps
              </h3>
              <div className="border border-[var(--border-default)] rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-[var(--bg-secondary)]">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-semibold text-[var(--text-muted)] uppercase w-12">#</th>
                      <th className="px-4 py-2 text-left text-xs font-semibold text-[var(--text-muted)] uppercase">Action</th>
                      <th className="px-4 py-2 text-left text-xs font-semibold text-[var(--text-muted)] uppercase">Expected Result</th>
                      {testCase.steps.some(s => s.testData) && (
                        <th className="px-4 py-2 text-left text-xs font-semibold text-[var(--text-muted)] uppercase">Test Data</th>
                      )}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[var(--border-light)]">
                    {testCase.steps.map((step, idx) => (
                      <tr key={idx} className="hover:bg-[var(--bg-secondary)]">
                        <td className="px-4 py-3 text-sm text-[var(--text-muted)]">{step.order}</td>
                        <td className="px-4 py-3 text-sm text-[var(--text-primary)]">{step.action}</td>
                        <td className="px-4 py-3 text-sm text-[var(--text-secondary)]">{step.expectedResult}</td>
                        {testCase.steps.some(s => s.testData) && (
                          <td className="px-4 py-3 text-sm text-[var(--text-muted)] font-mono">{step.testData || '-'}</td>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : null}

          {/* Expected Result */}
          {testCase.expectedResult && (
            <div>
              <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-2 uppercase tracking-wide">
                Expected Result
              </h3>
              <p className="text-[var(--text-secondary)] bg-green-50 border border-green-200 rounded-lg p-3">
                {testCase.expectedResult}
              </p>
            </div>
          )}

          {/* Test Data */}
          {testCase.testData && testCase.testData.items.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-2 uppercase tracking-wide">
                Test Data
              </h3>
              <div className="border border-[var(--border-default)] rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-[var(--bg-secondary)]">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-semibold text-[var(--text-muted)] uppercase">Field</th>
                      <th className="px-4 py-2 text-left text-xs font-semibold text-[var(--text-muted)] uppercase">Value</th>
                      <th className="px-4 py-2 text-left text-xs font-semibold text-[var(--text-muted)] uppercase">Description</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[var(--border-light)]">
                    {testCase.testData.items.map((item, idx) => (
                      <tr key={idx}>
                        <td className="px-4 py-2 text-sm font-mono text-[var(--text-primary)]">{item.field}</td>
                        <td className="px-4 py-2 text-sm font-mono text-[var(--accent-default)]">{item.value}</td>
                        <td className="px-4 py-2 text-sm text-[var(--text-muted)]">{item.description}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Postconditions */}
          {testCase.postconditions.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-2 uppercase tracking-wide">
                Postconditions
              </h3>
              <ul className="list-disc list-inside space-y-1 text-[var(--text-secondary)]">
                {testCase.postconditions.map((post, idx) => (
                  <li key={idx}>{post}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default TestCaseDetail;
