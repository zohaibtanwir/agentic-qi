'use client';

import { useTestDataStore } from '@/lib/stores/test-data-store';
import { GenerationMethod } from '@/lib/grpc/testDataClient';

const generationMethods = [
  { id: GenerationMethod.TRADITIONAL, label: 'Traditional', description: 'Fast, template-based generation' },
  { id: GenerationMethod.LLM, label: 'LLM', description: 'AI-powered with context awareness' },
  { id: GenerationMethod.RAG, label: 'RAG', description: 'Retrieval-augmented generation' },
  { id: GenerationMethod.HYBRID, label: 'Hybrid', description: 'Best of both worlds' },
];

export function BasicConfigTab() {
  const form = useTestDataStore((state) => state.form);
  const setFormField = useTestDataStore((state) => state.setFormField);
  const schemas = useTestDataStore((state) => state.schemas);
  const isLoadingSchemas = useTestDataStore((state) => state.isLoadingSchemas);

  // Schemas are loaded by the parent page component
  const selectedSchema = schemas.find((s) => s.name === form.entity);

  return (
    <div className="space-y-6">
      {/* Entity Selection */}
      <div>
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
          Entity Type
        </label>
        <select
          value={form.entity}
          onChange={(e) => setFormField('entity', e.target.value)}
          className="w-full px-3 py-2 border border-[var(--border-default)] rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-[var(--accent-default)] focus:border-transparent text-[var(--text-primary)]"
        >
          {isLoadingSchemas ? (
            <option>Loading schemas...</option>
          ) : schemas.length > 0 ? (
            <>
              {schemas.map((schema) => (
                <option key={schema.name} value={schema.name}>
                  {schema.name.charAt(0).toUpperCase() + schema.name.slice(1)}
                </option>
              ))}
              <option value="custom">Custom Schema</option>
            </>
          ) : (
            <>
              {/* Fallback options while schemas load */}
              <option value="cart">Cart</option>
              <option value="order">Order</option>
              <option value="user">User</option>
              <option value="product">Product</option>
              <option value="payment">Payment</option>
              <option value="review">Review</option>
              <option value="custom">Custom Schema</option>
            </>
          )}
        </select>
        {selectedSchema?.description && (
          <p className="mt-1.5 text-sm text-[var(--text-muted)]">
            {selectedSchema.description}
          </p>
        )}
      </div>

      {/* Schema Fields Preview */}
      {selectedSchema && selectedSchema.fields.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-[var(--text-primary)] mb-2">
            Schema Fields
          </h4>
          <div className="flex flex-wrap gap-2">
            {selectedSchema.fields.map((field) => (
              <span
                key={field.name}
                className={`inline-flex items-center px-2 py-1 rounded text-xs ${
                  field.required
                    ? 'bg-[var(--accent-default)] text-white'
                    : 'bg-gray-200 text-gray-700'
                }`}
              >
                {field.name}
                <span className={`ml-1 ${field.required ? 'text-white/70' : 'text-gray-400'}`}>({field.type})</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Record Count Slider */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="text-sm font-medium text-[var(--text-primary)]">
            Record Count
          </label>
          <span className="text-sm font-bold text-[var(--accent-default)]">
            {form.count}
          </span>
        </div>
        <input
          type="range"
          min={1}
          max={100}
          value={form.count}
          onChange={(e) => setFormField('count', parseInt(e.target.value, 10))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[var(--accent-default)]"
        />
        <div className="flex justify-between text-xs text-[var(--text-muted)] mt-1">
          <span>1</span>
          <span>25</span>
          <span>50</span>
          <span>75</span>
          <span>100</span>
        </div>
      </div>

      {/* Generation Method */}
      <div>
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
          Generation Method
        </label>
        <div className="grid grid-cols-2 gap-2">
          {generationMethods.map((method) => {
            const isSelected = form.generationMethod === method.id;
            return (
              <button
                key={method.id}
                onClick={() => setFormField('generationMethod', method.id)}
                className={`p-3 rounded-lg border text-left transition-all ${
                  isSelected
                    ? 'border-[var(--accent-default)] bg-white ring-2 ring-[var(--accent-default)]'
                    : 'border-[var(--border-default)] hover:border-gray-300 bg-white'
                }`}
              >
                <div className={`text-sm font-medium ${
                  isSelected
                    ? 'text-[var(--accent-default)]'
                    : 'text-[var(--text-primary)]'
                }`}>
                  {method.label}
                </div>
                <div className={`text-xs mt-0.5 ${
                  isSelected
                    ? 'text-[var(--text-secondary)]'
                    : 'text-[var(--text-muted)]'
                }`}>
                  {method.description}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Context Input (shown when not Traditional) */}
      {form.generationMethod !== GenerationMethod.TRADITIONAL && (
        <div>
          <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
            Context
          </label>
          <textarea
            value={form.context}
            onChange={(e) => setFormField('context', e.target.value)}
            placeholder="Describe your testing scenario, e.g., 'Generate data for ApplePay checkout testing with various cart sizes...'"
            rows={4}
            className="w-full px-3 py-2 border border-[var(--border-default)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--accent-default)] focus:border-transparent resize-none"
          />
          <p className="mt-1.5 text-xs text-[var(--text-muted)]">
            Provide context to guide AI-powered data generation
          </p>
        </div>
      )}

      {/* Advanced Options */}
      <div className="border-t border-[var(--border-default)] pt-4">
        <h4 className="text-sm font-medium text-[var(--text-primary)] mb-3">
          Advanced Options
        </h4>
        <div className="space-y-3">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={form.productionLike}
              onChange={(e) => setFormField('productionLike', e.target.checked)}
              className="w-4 h-4 rounded border-gray-300 text-[var(--accent-default)] focus:ring-[var(--accent-default)]"
            />
            <div>
              <span className="text-sm text-[var(--text-primary)]">Production-like Data</span>
              <p className="text-xs text-[var(--text-muted)]">Generate realistic data patterns</p>
            </div>
          </label>

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={form.defectTriggering}
              onChange={(e) => setFormField('defectTriggering', e.target.checked)}
              className="w-4 h-4 rounded border-gray-300 text-[var(--accent-default)] focus:ring-[var(--accent-default)]"
            />
            <div>
              <span className="text-sm text-[var(--text-primary)]">Defect-Triggering</span>
              <p className="text-xs text-[var(--text-muted)]">Include edge cases and boundary values</p>
            </div>
          </label>

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={form.useCache}
              onChange={(e) => setFormField('useCache', e.target.checked)}
              className="w-4 h-4 rounded border-gray-300 text-[var(--accent-default)] focus:ring-[var(--accent-default)]"
            />
            <div>
              <span className="text-sm text-[var(--text-primary)]">Use Cache</span>
              <p className="text-xs text-[var(--text-muted)]">Faster generation with cached results</p>
            </div>
          </label>
        </div>
      </div>
    </div>
  );
}
