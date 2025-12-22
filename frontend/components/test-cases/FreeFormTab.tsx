'use client';

interface FreeFormTabProps {
  requirement: string;
  context: Record<string, string>;
  onRequirementChange: (requirement: string) => void;
  onContextChange: (context: Record<string, string>) => void;
}

export function FreeFormTab({
  requirement,
  context,
  onRequirementChange,
  onContextChange,
}: FreeFormTabProps) {
  const contextEntries = Object.entries(context);

  const addContextEntry = () => {
    const newKey = `context_${Object.keys(context).length + 1}`;
    onContextChange({ ...context, [newKey]: '' });
  };

  const removeContextEntry = (key: string) => {
    const updated = { ...context };
    delete updated[key];
    onContextChange(updated);
  };

  const updateContextKey = (oldKey: string, newKey: string) => {
    if (oldKey === newKey) return;
    const updated: Record<string, string> = {};
    for (const [k, v] of Object.entries(context)) {
      if (k === oldKey) {
        updated[newKey] = v;
      } else {
        updated[k] = v;
      }
    }
    onContextChange(updated);
  };

  const updateContextValue = (key: string, value: string) => {
    onContextChange({ ...context, [key]: value });
  };

  return (
    <div className="space-y-6">
      {/* Free Form Requirement */}
      <div>
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
          Requirement Description <span className="text-red-500">*</span>
        </label>
        <textarea
          value={requirement}
          onChange={(e) => onRequirementChange(e.target.value)}
          placeholder="Describe the feature, functionality, or requirement you want to test. Be as detailed as possible to generate comprehensive test cases.

Example:
The checkout process should allow users to:
- Add items to cart with quantity selection
- Apply promotional codes and discounts
- Select shipping method (standard, express, same-day)
- Pay using credit card, PayPal, or gift card
- Receive order confirmation email"
          className="w-full px-4 py-3 rounded-lg border border-[var(--border-default)] bg-white text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-default)] focus:border-transparent resize-none"
          rows={10}
          required
        />
        <p className="mt-1 text-xs text-[var(--text-muted)]">
          Describe your requirements in any format. The more detail you provide, the better the generated test cases.
        </p>
      </div>

      {/* Context Key-Value Pairs */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-[var(--text-primary)]">
            Additional Context (Optional)
          </label>
          <button
            type="button"
            onClick={addContextEntry}
            className="text-sm text-[var(--accent-default)] hover:text-[var(--accent-hover)] font-medium"
          >
            + Add Context
          </button>
        </div>
        {contextEntries.length > 0 && (
          <div className="space-y-3">
            {contextEntries.map(([key, value], index) => (
              <div key={index} className="flex gap-2">
                <input
                  type="text"
                  value={key}
                  onChange={(e) => updateContextKey(key, e.target.value)}
                  placeholder="Key (e.g., domain)"
                  className="w-1/3 px-3 py-2 rounded-lg border border-[var(--border-default)] bg-white text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-default)] focus:border-transparent text-sm"
                />
                <input
                  type="text"
                  value={value}
                  onChange={(e) => updateContextValue(key, e.target.value)}
                  placeholder="Value (e.g., ecommerce)"
                  className="flex-1 px-3 py-2 rounded-lg border border-[var(--border-default)] bg-white text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-default)] focus:border-transparent text-sm"
                />
                <button
                  type="button"
                  onClick={() => removeContextEntry(key)}
                  className="flex-shrink-0 w-10 h-10 flex items-center justify-center text-[var(--text-muted)] hover:text-red-500 rounded-lg hover:bg-red-50 transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}
        <p className="mt-2 text-xs text-[var(--text-muted)]">
          Add key-value pairs to provide additional context like domain, technology stack, or business rules.
        </p>
      </div>

      {/* Suggestions */}
      <div className="bg-[var(--bg-secondary)] rounded-lg p-4">
        <h4 className="text-sm font-medium text-[var(--text-primary)] mb-2">Tips for better results:</h4>
        <ul className="text-xs text-[var(--text-muted)] space-y-1">
          <li>• Include specific user workflows and interactions</li>
          <li>• Mention any validation rules or business constraints</li>
          <li>• Describe expected error scenarios</li>
          <li>• Specify any integration points with other systems</li>
          <li>• Include non-functional requirements (performance, security)</li>
        </ul>
      </div>
    </div>
  );
}

export default FreeFormTab;
