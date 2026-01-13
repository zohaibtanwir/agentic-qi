'use client';

import { useTestDataStore } from '@/lib/stores/test-data-store';

// Common PII field patterns to suggest for masking
const PII_SUGGESTIONS = [
  { fieldName: 'email', piiType: 'Email', description: 'Email addresses' },
  { fieldName: 'phone', piiType: 'Phone', description: 'Phone numbers' },
  { fieldName: 'name', piiType: 'Name', description: 'Personal names' },
  { fieldName: 'first_name', piiType: 'Name', description: 'First names' },
  { fieldName: 'last_name', piiType: 'Name', description: 'Last names' },
  { fieldName: 'address', piiType: 'Address', description: 'Physical addresses' },
  { fieldName: 'street', piiType: 'Address', description: 'Street addresses' },
  { fieldName: 'ssn', piiType: 'SSN', description: 'Social security numbers' },
  { fieldName: 'credit_card', piiType: 'Credit Card', description: 'Credit card numbers' },
  { fieldName: 'card_number', piiType: 'Credit Card', description: 'Card numbers' },
  { fieldName: 'dob', piiType: 'DOB', description: 'Date of birth' },
  { fieldName: 'date_of_birth', piiType: 'DOB', description: 'Date of birth' },
  { fieldName: 'ip_address', piiType: 'IP', description: 'IP addresses' },
];

export function MaskingTab() {
  const form = useTestDataStore((state) => state.form);
  const setMaskingEnabled = useTestDataStore((state) => state.setMaskingEnabled);
  const toggleFieldMasking = useTestDataStore((state) => state.toggleFieldMasking);
  const clearMaskedFields = useTestDataStore((state) => state.clearMaskedFields);
  const schemas = useTestDataStore((state) => state.schemas);

  const selectedSchema = schemas.find((s) => s.name === form.entity);
  const schemaFields = selectedSchema?.fields || [];

  // Check if a field name matches any PII pattern
  const isPIIField = (fieldName: string): string | null => {
    const lowerName = fieldName.toLowerCase();
    for (const suggestion of PII_SUGGESTIONS) {
      if (lowerName.includes(suggestion.fieldName)) {
        return suggestion.piiType;
      }
    }
    return null;
  };

  // Get suggested PII fields from schema
  const suggestedPIIFields = schemaFields
    .filter((field) => isPIIField(field.name))
    .map((field) => ({
      name: field.name,
      piiType: isPIIField(field.name),
    }));

  return (
    <div className="space-y-6">
      {/* Global Toggle */}
      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
        <div>
          <h3 className="text-sm font-medium text-[var(--text-primary)]">
            Enable Data Masking
          </h3>
          <p className="text-xs text-[var(--text-muted)] mt-1">
            Mask sensitive fields in generated data
          </p>
        </div>
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={form.maskingConfig.enabled}
            onChange={(e) => setMaskingEnabled(e.target.checked)}
            className="sr-only peer"
          />
          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-[var(--accent-default)]/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[var(--accent-default)]"></div>
        </label>
      </div>

      {/* Masking Strategy Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <svg className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h4 className="text-sm font-medium text-blue-800">Partial Masking</h4>
            <p className="text-xs text-blue-600 mt-1">
              Data is partially masked to preserve format while hiding sensitive content.
              Examples: j***@e****.com, 555-***-**67, J*** D**
            </p>
          </div>
        </div>
      </div>

      {form.maskingConfig.enabled && (
        <>
          {/* Suggested PII Fields */}
          {suggestedPIIFields.length > 0 && (
            <div className="border border-[var(--border-default)] rounded-lg overflow-hidden">
              <div className="bg-orange-50 px-4 py-3 border-b border-orange-200">
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <h4 className="text-sm font-medium text-orange-800">Suggested PII Fields</h4>
                </div>
                <p className="text-xs text-orange-600 mt-1">
                  These fields were detected as potentially containing personal information
                </p>
              </div>
              <div className="p-4 space-y-2">
                {suggestedPIIFields.map((field) => (
                  <label
                    key={field.name}
                    className="flex items-center justify-between p-2 hover:bg-gray-50 rounded cursor-pointer"
                  >
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={form.maskingConfig.maskedFields.includes(field.name)}
                        onChange={() => toggleFieldMasking(field.name)}
                        className="w-4 h-4 rounded border-gray-300 text-[var(--accent-default)] focus:ring-[var(--accent-default)]"
                      />
                      <span className="text-sm text-[var(--text-primary)]">{field.name}</span>
                    </div>
                    <span className="text-xs px-2 py-1 bg-orange-100 text-orange-700 rounded">
                      {field.piiType}
                    </span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* All Schema Fields */}
          {schemaFields.length > 0 && (
            <div className="border border-[var(--border-default)] rounded-lg overflow-hidden">
              <div className="bg-gray-50 px-4 py-3 border-b border-[var(--border-default)] flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium text-[var(--text-primary)]">All Fields</h4>
                  <p className="text-xs text-[var(--text-muted)] mt-0.5">
                    Select any field to mask in generated data
                  </p>
                </div>
                {form.maskingConfig.maskedFields.length > 0 && (
                  <button
                    onClick={clearMaskedFields}
                    className="text-xs text-[var(--accent-default)] hover:underline"
                  >
                    Clear all
                  </button>
                )}
              </div>
              <div className="p-4 space-y-1 max-h-64 overflow-y-auto">
                {schemaFields.map((field) => {
                  const piiType = isPIIField(field.name);
                  return (
                    <label
                      key={field.name}
                      className="flex items-center justify-between p-2 hover:bg-gray-50 rounded cursor-pointer"
                    >
                      <div className="flex items-center gap-3">
                        <input
                          type="checkbox"
                          checked={form.maskingConfig.maskedFields.includes(field.name)}
                          onChange={() => toggleFieldMasking(field.name)}
                          className="w-4 h-4 rounded border-gray-300 text-[var(--accent-default)] focus:ring-[var(--accent-default)]"
                        />
                        <span className="text-sm text-[var(--text-primary)]">{field.name}</span>
                        <span className="text-xs text-[var(--text-muted)]">({field.type})</span>
                      </div>
                      {piiType && (
                        <span className="text-xs px-2 py-0.5 bg-orange-100 text-orange-700 rounded">
                          PII
                        </span>
                      )}
                    </label>
                  );
                })}
              </div>
            </div>
          )}

          {/* Selected Fields Summary */}
          {form.maskingConfig.maskedFields.length > 0 && (
            <div className="bg-[var(--accent-default)]/5 border border-[var(--accent-default)]/20 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <svg className="w-4 h-4 text-[var(--accent-default)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                <span className="text-sm font-medium text-[var(--accent-default)]">
                  {form.maskingConfig.maskedFields.length} field(s) will be masked
                </span>
              </div>
              <div className="flex flex-wrap gap-2">
                {form.maskingConfig.maskedFields.map((field) => (
                  <span
                    key={field}
                    className="inline-flex items-center gap-1 text-xs px-2 py-1 bg-white border border-[var(--accent-default)]/30 rounded text-[var(--text-secondary)]"
                  >
                    {field}
                    <button
                      onClick={() => toggleFieldMasking(field)}
                      className="hover:text-red-500"
                    >
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* No schema loaded message */}
          {schemaFields.length === 0 && (
            <div className="text-center py-8 text-[var(--text-muted)]">
              <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-sm">Select an entity to see available fields for masking</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
