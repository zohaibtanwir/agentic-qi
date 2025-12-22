'use client';

import { useState } from 'react';
import { OutputFormat, CoverageLevel, TestType, TestCase } from '@/lib/grpc/generated/test_cases';
import { useGenerateTestCases, InputType, GenerateFormData } from '@/hooks/useGenerateTestCases';
import { UserStoryTab } from './UserStoryTab';
import { ApiSpecTab } from './ApiSpecTab';
import { FreeFormTab } from './FreeFormTab';
import { ConfigPanel } from './ConfigPanel';
import { TestCaseCard } from './TestCaseCard';
import { TestCaseDetail } from './TestCaseDetail';

const INPUT_TABS: { id: InputType; label: string; description: string }[] = [
  { id: 'user_story', label: 'User Story', description: 'Generate test cases from user stories and acceptance criteria' },
  { id: 'api_spec', label: 'API Specification', description: 'Generate test cases from OpenAPI or GraphQL specs' },
  { id: 'free_form', label: 'Free Form', description: 'Generate test cases from any requirement description' },
];

export function GenerationForm() {
  const { generateTestCases, loading, error, testCases, metadata, reset } = useGenerateTestCases();

  // Input type state
  const [inputType, setInputType] = useState<InputType>('user_story');

  // User Story state
  const [story, setStory] = useState('');
  const [acceptanceCriteria, setAcceptanceCriteria] = useState<string[]>(['']);
  const [additionalContext, setAdditionalContext] = useState('');

  // API Spec state
  const [apiSpec, setApiSpec] = useState('');
  const [specFormat, setSpecFormat] = useState<'openapi' | 'graphql'>('openapi');
  const [endpoints, setEndpoints] = useState<string[]>([]);

  // Free Form state
  const [freeFormText, setFreeFormText] = useState('');
  const [freeFormContext, setFreeFormContext] = useState<Record<string, string>>({});

  // Config state
  const [outputFormat, setOutputFormat] = useState<OutputFormat>(OutputFormat.TRADITIONAL);
  const [coverageLevel, setCoverageLevel] = useState<CoverageLevel>(CoverageLevel.STANDARD);
  const [testTypes, setTestTypes] = useState<TestType[]>([TestType.FUNCTIONAL, TestType.NEGATIVE]);
  const [maxTestCases, setMaxTestCases] = useState(10);

  // Results state
  const [selectedTestCase, setSelectedTestCase] = useState<TestCase | null>(null);
  const [showConfig, setShowConfig] = useState(true);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const formData: GenerateFormData = {
      inputType,
      story,
      acceptanceCriteria,
      additionalContext,
      apiSpec,
      specFormat,
      endpoints,
      freeFormText,
      freeFormContext,
      outputFormat,
      coverageLevel,
      testTypes,
      maxTestCases,
    };

    await generateTestCases(formData);
  };

  const isFormValid = () => {
    if (testTypes.length === 0) return false;

    switch (inputType) {
      case 'user_story':
        return story.trim().length > 0;
      case 'api_spec':
        return apiSpec.trim().length > 0;
      case 'free_form':
        return freeFormText.trim().length > 0;
      default:
        return false;
    }
  };

  return (
    <div className="space-y-8">
      <form onSubmit={handleSubmit}>
        {/* Input Type Tabs */}
        <div className="mb-6">
          <div className="border-b border-[var(--border-default)]">
            <nav className="-mb-px flex space-x-8">
              {INPUT_TABS.map(tab => (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setInputType(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                    inputType === tab.id
                      ? 'border-[var(--accent-default)] text-[var(--accent-default)]'
                      : 'border-transparent text-[var(--text-muted)] hover:text-[var(--text-secondary)] hover:border-[var(--border-default)]'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
          <p className="mt-2 text-sm text-[var(--text-muted)]">
            {INPUT_TABS.find(t => t.id === inputType)?.description}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Input Form */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg border border-[var(--border-default)] p-6">
              {inputType === 'user_story' && (
                <UserStoryTab
                  story={story}
                  acceptanceCriteria={acceptanceCriteria}
                  additionalContext={additionalContext}
                  onStoryChange={setStory}
                  onAcceptanceCriteriaChange={setAcceptanceCriteria}
                  onAdditionalContextChange={setAdditionalContext}
                />
              )}
              {inputType === 'api_spec' && (
                <ApiSpecTab
                  apiSpec={apiSpec}
                  specFormat={specFormat}
                  endpoints={endpoints}
                  onApiSpecChange={setApiSpec}
                  onSpecFormatChange={setSpecFormat}
                  onEndpointsChange={setEndpoints}
                />
              )}
              {inputType === 'free_form' && (
                <FreeFormTab
                  requirement={freeFormText}
                  context={freeFormContext}
                  onRequirementChange={setFreeFormText}
                  onContextChange={setFreeFormContext}
                />
              )}

              {/* Submit Button */}
              <div className="mt-6 pt-6 border-t border-[var(--border-light)]">
                <button
                  type="submit"
                  disabled={loading || !isFormValid()}
                  className="w-full sm:w-auto px-8 py-3 bg-[var(--accent-default)] text-white font-medium rounded-lg hover:bg-[var(--accent-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Generating Test Cases...
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      Generate Test Cases
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Config Panel */}
          <div className="lg:col-span-1">
            <div className="lg:sticky lg:top-24">
              <button
                type="button"
                onClick={() => setShowConfig(!showConfig)}
                className="lg:hidden w-full flex items-center justify-between p-4 bg-[var(--bg-secondary)] rounded-lg mb-4"
              >
                <span className="font-medium text-[var(--text-primary)]">Generation Settings</span>
                <svg
                  className={`w-5 h-5 transition-transform ${showConfig ? 'rotate-180' : ''}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              <div className={`${showConfig ? 'block' : 'hidden'} lg:block`}>
                <ConfigPanel
                  outputFormat={outputFormat}
                  coverageLevel={coverageLevel}
                  testTypes={testTypes}
                  maxTestCases={maxTestCases}
                  onOutputFormatChange={setOutputFormat}
                  onCoverageLevelChange={setCoverageLevel}
                  onTestTypesChange={setTestTypes}
                  onMaxTestCasesChange={setMaxTestCases}
                />
              </div>
            </div>
          </div>
        </div>
      </form>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <svg className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h4 className="font-medium text-red-800">Generation Failed</h4>
            <p className="text-sm text-red-600 mt-1">{error}</p>
          </div>
          <button
            onClick={reset}
            className="ml-auto text-sm text-red-600 hover:text-red-800 underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Results Section */}
      {testCases.length > 0 && (
        <div className="space-y-6">
          {/* Results Header */}
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-[var(--text-primary)]">
                Generated Test Cases
              </h2>
              <p className="text-sm text-[var(--text-muted)] mt-1">
                {testCases.length} test cases generated
              </p>
            </div>
            <button
              onClick={reset}
              className="px-4 py-2 text-sm text-[var(--text-secondary)] hover:text-[var(--accent-default)] border border-[var(--border-default)] rounded-lg hover:border-[var(--accent-default)] transition-colors"
            >
              Clear Results
            </button>
          </div>

          {/* Metadata */}
          {metadata && (
            <div className="bg-[var(--bg-secondary)] rounded-lg p-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-[var(--text-muted)]">Model</p>
                  <p className="font-medium text-[var(--text-primary)]">
                    {metadata.llmProvider} / {metadata.llmModel}
                  </p>
                </div>
                <div>
                  <p className="text-[var(--text-muted)]">Tokens Used</p>
                  <p className="font-medium text-[var(--text-primary)]">
                    {metadata.llmTokensUsed.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-[var(--text-muted)]">Generation Time</p>
                  <p className="font-medium text-[var(--text-primary)]">
                    {(metadata.generationTimeMs / 1000).toFixed(2)}s
                  </p>
                </div>
                <div>
                  <p className="text-[var(--text-muted)]">Test Cases</p>
                  <p className="font-medium text-[var(--text-primary)]">
                    {metadata.testCasesGenerated}
                  </p>
                </div>
              </div>
              {metadata.coverage && (
                <div className="mt-4 pt-4 border-t border-[var(--border-light)]">
                  <p className="text-xs font-medium text-[var(--text-muted)] mb-2">Coverage Breakdown</p>
                  <div className="flex gap-4 text-sm">
                    <span>Functional: {metadata.coverage.functionalCount}</span>
                    <span>Negative: {metadata.coverage.negativeCount}</span>
                    <span>Boundary: {metadata.coverage.boundaryCount}</span>
                    <span>Edge Cases: {metadata.coverage.edgeCaseCount}</span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Test Case Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {testCases.map((tc) => (
              <TestCaseCard
                key={tc.id}
                testCase={tc}
                outputFormat={outputFormat}
                onSelect={setSelectedTestCase}
                isSelected={selectedTestCase?.id === tc.id}
              />
            ))}
          </div>
        </div>
      )}

      {/* Test Case Detail Modal */}
      {selectedTestCase && (
        <TestCaseDetail
          testCase={selectedTestCase}
          outputFormat={outputFormat}
          onClose={() => setSelectedTestCase(null)}
        />
      )}
    </div>
  );
}

export default GenerationForm;
