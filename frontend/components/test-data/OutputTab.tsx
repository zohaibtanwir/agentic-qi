'use client';

import { useTestDataStore } from '@/lib/stores/test-data-store';
import { OutputFormat } from '@/lib/grpc/testDataClient';

const outputFormats = [
  {
    id: OutputFormat.JSON,
    label: 'JSON',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
      </svg>
    ),
    description: 'Standard JSON format for API testing',
    example: '{ "id": 1, "name": "..." }',
  },
  {
    id: OutputFormat.CSV,
    label: 'CSV',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
      </svg>
    ),
    description: 'Comma-separated values for spreadsheets',
    example: 'id,name,email\\n1,"John Doe",...',
  },
  {
    id: OutputFormat.SQL,
    label: 'SQL',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
      </svg>
    ),
    description: 'INSERT statements for database seeding',
    example: 'INSERT INTO users (id, name) VALUES ...',
  },
];

// Additional formats in a less prominent section
const additionalFormats = [
  { id: 3, label: 'YAML', description: 'YAML configuration format' },
  { id: 4, label: 'XML', description: 'XML document format' },
];

export function OutputTab() {
  const { form, setFormField, generationStats } = useTestDataStore();

  return (
    <div className="space-y-6">
      {/* Primary Formats */}
      <div>
        <h4 className="text-sm font-medium text-[var(--text-primary)] mb-3">
          Output Format
        </h4>
        <div className="grid gap-3">
          {outputFormats.map((format) => (
            <button
              key={format.id}
              onClick={() => setFormField('outputFormat', format.id)}
              className={`p-4 rounded-lg border text-left transition-all ${
                form.outputFormat === format.id
                  ? 'border-[var(--accent-default)] bg-[var(--accent-default)] bg-opacity-5 ring-1 ring-[var(--accent-default)]'
                  : 'border-[var(--border-default)] hover:border-gray-300 bg-white'
              }`}
            >
              <div className="flex items-start gap-3">
                <div className={`p-2 rounded-lg ${
                  form.outputFormat === format.id
                    ? 'bg-[var(--accent-default)] text-white'
                    : 'bg-gray-100 text-gray-500'
                }`}>
                  {format.icon}
                </div>
                <div className="flex-1">
                  <div className={`font-medium ${
                    form.outputFormat === format.id
                      ? 'text-[var(--accent-default)]'
                      : 'text-[var(--text-primary)]'
                  }`}>
                    {format.label}
                  </div>
                  <div className="text-sm text-[var(--text-muted)] mt-0.5">
                    {format.description}
                  </div>
                  <code className="text-xs text-gray-500 mt-2 block font-mono">
                    {format.example}
                  </code>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Additional Formats */}
      <div>
        <h4 className="text-sm font-medium text-[var(--text-primary)] mb-2">
          Other Formats
        </h4>
        <div className="flex gap-2">
          {additionalFormats.map((format) => (
            <button
              key={format.id}
              onClick={() => setFormField('outputFormat', format.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                form.outputFormat === format.id
                  ? 'bg-[var(--accent-default)] text-white'
                  : 'bg-gray-100 text-[var(--text-secondary)] hover:bg-gray-200'
              }`}
            >
              {format.label}
            </button>
          ))}
        </div>
      </div>

      {/* Custom Schema (for custom entity) */}
      {form.entity === 'custom' && (
        <div className="border-t border-[var(--border-default)] pt-4">
          <h4 className="text-sm font-medium text-[var(--text-primary)] mb-2">
            Custom Schema Definition
          </h4>
          <textarea
            value={form.customSchema}
            onChange={(e) => setFormField('customSchema', e.target.value)}
            placeholder={`{
  "fields": [
    { "name": "id", "type": "uuid" },
    { "name": "email", "type": "email" },
    { "name": "amount", "type": "float", "min": 0, "max": 1000 }
  ]
}`}
            rows={8}
            className="w-full px-3 py-2 border border-[var(--border-default)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--accent-default)] focus:border-transparent resize-none font-mono text-sm"
          />
          <p className="mt-1.5 text-xs text-[var(--text-muted)]">
            Define your custom schema in JSON format
          </p>
        </div>
      )}

      {/* Generation Stats */}
      {generationStats.totalGenerated > 0 && (
        <div className="bg-gray-50 rounded-lg p-4 border border-[var(--border-default)]">
          <h4 className="text-sm font-medium text-[var(--text-primary)] mb-3">
            Session Statistics
          </h4>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-2xl font-bold text-[var(--accent-default)]">
                {generationStats.totalGenerated}
              </div>
              <div className="text-xs text-[var(--text-muted)]">
                Total Records Generated
              </div>
            </div>
            <div>
              <div className="text-2xl font-bold text-[var(--text-primary)]">
                {generationStats.lastGenerationTime}ms
              </div>
              <div className="text-xs text-[var(--text-muted)]">
                Last Generation Time
              </div>
            </div>
            {generationStats.llmTokensUsed > 0 && (
              <>
                <div>
                  <div className="text-2xl font-bold text-[var(--text-primary)]">
                    {generationStats.llmTokensUsed.toLocaleString()}
                  </div>
                  <div className="text-xs text-[var(--text-muted)]">
                    LLM Tokens Used
                  </div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-green-600">
                    {(generationStats.averageCoherenceScore * 100).toFixed(1)}%
                  </div>
                  <div className="text-xs text-[var(--text-muted)]">
                    Coherence Score
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
