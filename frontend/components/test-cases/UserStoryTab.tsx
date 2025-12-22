'use client';

interface UserStoryTabProps {
  story: string;
  acceptanceCriteria: string[];
  additionalContext: string;
  onStoryChange: (story: string) => void;
  onAcceptanceCriteriaChange: (criteria: string[]) => void;
  onAdditionalContextChange: (context: string) => void;
}

export function UserStoryTab({
  story,
  acceptanceCriteria,
  additionalContext,
  onStoryChange,
  onAcceptanceCriteriaChange,
  onAdditionalContextChange,
}: UserStoryTabProps) {
  const addCriterion = () => {
    onAcceptanceCriteriaChange([...acceptanceCriteria, '']);
  };

  const removeCriterion = (index: number) => {
    const updated = acceptanceCriteria.filter((_, i) => i !== index);
    onAcceptanceCriteriaChange(updated.length > 0 ? updated : ['']);
  };

  const updateCriterion = (index: number, value: string) => {
    const updated = [...acceptanceCriteria];
    updated[index] = value;
    onAcceptanceCriteriaChange(updated);
  };

  return (
    <div className="space-y-6">
      {/* User Story Input */}
      <div>
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
          User Story <span className="text-red-500">*</span>
        </label>
        <textarea
          value={story}
          onChange={(e) => onStoryChange(e.target.value)}
          placeholder="As a [role], I want to [action] so that [benefit]..."
          className="w-full px-4 py-3 rounded-lg border border-[var(--border-default)] bg-white text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-default)] focus:border-transparent resize-none"
          rows={4}
          required
        />
        <p className="mt-1 text-xs text-[var(--text-muted)]">
          Describe the feature from the user&apos;s perspective using the standard user story format.
        </p>
      </div>

      {/* Acceptance Criteria */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-[var(--text-primary)]">
            Acceptance Criteria
          </label>
          <button
            type="button"
            onClick={addCriterion}
            className="text-sm text-[var(--accent-default)] hover:text-[var(--accent-hover)] font-medium"
          >
            + Add Criterion
          </button>
        </div>
        <div className="space-y-3">
          {acceptanceCriteria.map((criterion, index) => (
            <div key={index} className="flex gap-2">
              <div className="flex-shrink-0 w-6 h-10 flex items-center justify-center text-sm text-[var(--text-muted)]">
                {index + 1}.
              </div>
              <input
                type="text"
                value={criterion}
                onChange={(e) => updateCriterion(index, e.target.value)}
                placeholder={`Acceptance criterion ${index + 1}`}
                className="flex-1 px-4 py-2 rounded-lg border border-[var(--border-default)] bg-white text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-default)] focus:border-transparent"
              />
              {acceptanceCriteria.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeCriterion(index)}
                  className="flex-shrink-0 w-10 h-10 flex items-center justify-center text-[var(--text-muted)] hover:text-red-500 rounded-lg hover:bg-red-50 transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
          ))}
        </div>
        <p className="mt-2 text-xs text-[var(--text-muted)]">
          List the specific conditions that must be met for this story to be considered complete.
        </p>
      </div>

      {/* Additional Context */}
      <div>
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
          Additional Context
        </label>
        <textarea
          value={additionalContext}
          onChange={(e) => onAdditionalContextChange(e.target.value)}
          placeholder="Any additional context, constraints, or technical details..."
          className="w-full px-4 py-3 rounded-lg border border-[var(--border-default)] bg-white text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-default)] focus:border-transparent resize-none"
          rows={3}
        />
        <p className="mt-1 text-xs text-[var(--text-muted)]">
          Optional: Provide any technical constraints, business rules, or edge cases to consider.
        </p>
      </div>
    </div>
  );
}

export default UserStoryTab;
