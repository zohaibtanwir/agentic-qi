'use client';

import { useRequirementAnalysisStore, type RequirementAnalysisStore, type InputType } from '@/lib/stores/requirement-analysis-store';

const inputTypes: { id: InputType; label: string; description: string }[] = [
  { id: 'freeform', label: 'Free Form', description: 'Paste or type any requirement text' },
  { id: 'jira', label: 'Jira Story', description: 'Enter Jira story details' },
  { id: 'transcript', label: 'Transcript', description: 'Analyze meeting transcripts' },
];

export function AnalysisForm() {
  const inputType = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.inputType);
  const setInputType = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.setInputType);
  const freeFormForm = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.freeFormForm);
  const setFreeFormField = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.setFreeFormField);
  const jiraForm = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.jiraForm);
  const setJiraField = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.setJiraField);
  const addJiraAC = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.addJiraAC);
  const removeJiraAC = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.removeJiraAC);
  const updateJiraAC = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.updateJiraAC);
  const transcriptForm = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.transcriptForm);
  const setTranscriptField = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.setTranscriptField);
  const analysisConfig = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.analysisConfig);
  const setConfigField = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.setConfigField);
  const isAnalyzing = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.isAnalyzing);
  const analyzeRequirement = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.analyzeRequirement);

  const canSubmit = () => {
    if (inputType === 'freeform') {
      return freeFormForm.text.trim().length > 20;
    } else if (inputType === 'jira') {
      return jiraForm.key.trim() && jiraForm.summary.trim() && jiraForm.description.trim();
    } else {
      return transcriptForm.transcript.trim().length > 50;
    }
  };

  return (
    <div className="bg-[var(--surface-primary)] rounded-xl border border-[var(--border-default)] overflow-hidden">
      {/* Input Type Tabs */}
      <div className="border-b border-[var(--border-default)]">
        <div className="flex">
          {inputTypes.map((type) => (
            <button
              key={type.id}
              onClick={() => setInputType(type.id)}
              className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                inputType === type.id
                  ? 'bg-purple-50 text-purple-700 border-b-2 border-purple-600'
                  : 'text-[var(--text-secondary)] hover:bg-[var(--surface-secondary)]'
              }`}
            >
              {type.label}
            </button>
          ))}
        </div>
      </div>

      <div className="p-6">
        {/* Free Form Input */}
        {inputType === 'freeform' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[var(--text-primary)] mb-1">
                Title (Optional)
              </label>
              <input
                type="text"
                value={freeFormForm.title}
                onChange={(e) => setFreeFormField('title', e.target.value)}
                placeholder="e.g., Add to Cart Feature"
                className="w-full px-3 py-2 border border-[var(--border-default)] rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text-primary)] mb-1">
                Requirement Text <span className="text-red-500">*</span>
              </label>
              <textarea
                value={freeFormForm.text}
                onChange={(e) => setFreeFormField('text', e.target.value)}
                placeholder="Enter your requirement here. You can use user story format (As a... I want... So that...) or any other format."
                rows={8}
                className="w-full px-3 py-2 border border-[var(--border-default)] rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              />
              <p className="mt-1 text-xs text-[var(--text-muted)]">
                {freeFormForm.text.length} characters (minimum 20)
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text-primary)] mb-1">
                Additional Context (Optional)
              </label>
              <textarea
                value={freeFormForm.context}
                onChange={(e) => setFreeFormField('context', e.target.value)}
                placeholder="Any additional context, constraints, or background information..."
                rows={3}
                className="w-full px-3 py-2 border border-[var(--border-default)] rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              />
            </div>
          </div>
        )}

        {/* Jira Story Input */}
        {inputType === 'jira' && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-[var(--text-primary)] mb-1">
                  Jira Key <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={jiraForm.key}
                  onChange={(e) => setJiraField('key', e.target.value)}
                  placeholder="e.g., ECOM-1234"
                  className="w-full px-3 py-2 border border-[var(--border-default)] rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--text-primary)] mb-1">
                  Priority
                </label>
                <select
                  value={jiraForm.priority}
                  onChange={(e) => setJiraField('priority', e.target.value)}
                  className="w-full px-3 py-2 border border-[var(--border-default)] rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                  <option value="Critical">Critical</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text-primary)] mb-1">
                Summary <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={jiraForm.summary}
                onChange={(e) => setJiraField('summary', e.target.value)}
                placeholder="Story title / summary"
                className="w-full px-3 py-2 border border-[var(--border-default)] rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text-primary)] mb-1">
                Description <span className="text-red-500">*</span>
              </label>
              <textarea
                value={jiraForm.description}
                onChange={(e) => setJiraField('description', e.target.value)}
                placeholder="Full story description..."
                rows={6}
                className="w-full px-3 py-2 border border-[var(--border-default)] rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text-primary)] mb-1">
                Acceptance Criteria
              </label>
              {jiraForm.acceptanceCriteria.map((ac, index) => (
                <div key={index} className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={ac}
                    onChange={(e) => updateJiraAC(index, e.target.value)}
                    placeholder={`Acceptance criterion ${index + 1}`}
                    className="flex-1 px-3 py-2 border border-[var(--border-default)] rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                  {jiraForm.acceptanceCriteria.length > 1 && (
                    <button
                      onClick={() => removeJiraAC(index)}
                      className="px-3 py-2 text-red-500 hover:bg-red-50 rounded-lg"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  )}
                </div>
              ))}
              <button
                onClick={() => addJiraAC('')}
                className="text-sm text-purple-600 hover:text-purple-700 font-medium"
              >
                + Add Acceptance Criterion
              </button>
            </div>
          </div>
        )}

        {/* Transcript Input */}
        {inputType === 'transcript' && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-[var(--text-primary)] mb-1">
                  Meeting Title
                </label>
                <input
                  type="text"
                  value={transcriptForm.meetingTitle}
                  onChange={(e) => setTranscriptField('meetingTitle', e.target.value)}
                  placeholder="e.g., Sprint Planning - Cart Feature"
                  className="w-full px-3 py-2 border border-[var(--border-default)] rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--text-primary)] mb-1">
                  Meeting Date
                </label>
                <input
                  type="date"
                  value={transcriptForm.meetingDate}
                  onChange={(e) => setTranscriptField('meetingDate', e.target.value)}
                  className="w-full px-3 py-2 border border-[var(--border-default)] rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text-primary)] mb-1">
                Transcript <span className="text-red-500">*</span>
              </label>
              <textarea
                value={transcriptForm.transcript}
                onChange={(e) => setTranscriptField('transcript', e.target.value)}
                placeholder="Paste your meeting transcript here. Include speaker labels if available (e.g., 'John: We need to add...')"
                rows={10}
                className="w-full px-3 py-2 border border-[var(--border-default)] rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none font-mono text-sm"
              />
              <p className="mt-1 text-xs text-[var(--text-muted)]">
                {transcriptForm.transcript.length} characters (minimum 50)
              </p>
            </div>
          </div>
        )}

        {/* Analysis Config */}
        <div className="mt-6 pt-6 border-t border-[var(--border-default)]">
          <h3 className="text-sm font-medium text-[var(--text-primary)] mb-3">Analysis Options</h3>
          <div className="grid grid-cols-2 gap-4">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={analysisConfig.includeDomainValidation}
                onChange={(e) => setConfigField('includeDomainValidation', e.target.checked)}
                className="w-4 h-4 text-purple-600 rounded border-gray-300 focus:ring-purple-500"
              />
              <span className="text-sm text-[var(--text-secondary)]">Include domain validation</span>
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={analysisConfig.generateAcceptanceCriteria}
                onChange={(e) => setConfigField('generateAcceptanceCriteria', e.target.checked)}
                className="w-4 h-4 text-purple-600 rounded border-gray-300 focus:ring-purple-500"
              />
              <span className="text-sm text-[var(--text-secondary)]">Generate acceptance criteria</span>
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={analysisConfig.generateQuestions}
                onChange={(e) => setConfigField('generateQuestions', e.target.checked)}
                className="w-4 h-4 text-purple-600 rounded border-gray-300 focus:ring-purple-500"
              />
              <span className="text-sm text-[var(--text-secondary)]">Generate clarifying questions</span>
            </label>
            <div>
              <label className="block text-xs text-[var(--text-muted)] mb-1">Domain</label>
              <select
                value={analysisConfig.domain}
                onChange={(e) => setConfigField('domain', e.target.value)}
                className="w-full px-3 py-1.5 text-sm border border-[var(--border-default)] rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="ecommerce">E-commerce</option>
                <option value="fintech">Fintech</option>
                <option value="healthcare">Healthcare</option>
                <option value="general">General</option>
              </select>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="mt-6">
          <button
            onClick={analyzeRequirement}
            disabled={isAnalyzing || !canSubmit()}
            className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
              isAnalyzing || !canSubmit()
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-purple-600 text-white hover:bg-purple-700'
            }`}
          >
            {isAnalyzing ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Analyzing Requirement...
              </span>
            ) : (
              'Analyze Requirement'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
