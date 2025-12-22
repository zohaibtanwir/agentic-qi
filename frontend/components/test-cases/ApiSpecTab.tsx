'use client';

interface ApiSpecTabProps {
  apiSpec: string;
  specFormat: 'openapi' | 'graphql';
  endpoints: string[];
  onApiSpecChange: (spec: string) => void;
  onSpecFormatChange: (format: 'openapi' | 'graphql') => void;
  onEndpointsChange: (endpoints: string[]) => void;
}

export function ApiSpecTab({
  apiSpec,
  specFormat,
  endpoints,
  onApiSpecChange,
  onSpecFormatChange,
  onEndpointsChange,
}: ApiSpecTabProps) {
  const addEndpoint = () => {
    onEndpointsChange([...endpoints, '']);
  };

  const removeEndpoint = (index: number) => {
    const updated = endpoints.filter((_, i) => i !== index);
    onEndpointsChange(updated);
  };

  const updateEndpoint = (index: number, value: string) => {
    const updated = [...endpoints];
    updated[index] = value;
    onEndpointsChange(updated);
  };

  return (
    <div className="space-y-6">
      {/* Spec Format Selection */}
      <div>
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
          Specification Format
        </label>
        <div className="flex gap-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="specFormat"
              value="openapi"
              checked={specFormat === 'openapi'}
              onChange={() => onSpecFormatChange('openapi')}
              className="w-4 h-4 text-[var(--accent-default)] border-[var(--border-default)] focus:ring-[var(--accent-default)]"
            />
            <span className="text-sm text-[var(--text-primary)]">OpenAPI / Swagger</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="specFormat"
              value="graphql"
              checked={specFormat === 'graphql'}
              onChange={() => onSpecFormatChange('graphql')}
              className="w-4 h-4 text-[var(--accent-default)] border-[var(--border-default)] focus:ring-[var(--accent-default)]"
            />
            <span className="text-sm text-[var(--text-primary)]">GraphQL Schema</span>
          </label>
        </div>
      </div>

      {/* API Spec Input */}
      <div>
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
          API Specification <span className="text-red-500">*</span>
        </label>
        <textarea
          value={apiSpec}
          onChange={(e) => onApiSpecChange(e.target.value)}
          placeholder={specFormat === 'openapi'
            ? `openapi: "3.0.0"
info:
  title: Sample API
  version: "1.0"
paths:
  /users:
    get:
      summary: Get all users
      responses:
        200:
          description: Success`
            : `type Query {
  users: [User!]!
  user(id: ID!): User
}

type User {
  id: ID!
  name: String!
  email: String!
}`
          }
          className="w-full px-4 py-3 rounded-lg border border-[var(--border-default)] bg-white text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-default)] focus:border-transparent font-mono text-sm resize-none"
          rows={12}
          required
        />
        <p className="mt-1 text-xs text-[var(--text-muted)]">
          Paste your {specFormat === 'openapi' ? 'OpenAPI/Swagger' : 'GraphQL'} specification in YAML or JSON format.
        </p>
      </div>

      {/* Specific Endpoints (Optional) */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-[var(--text-primary)]">
            Focus on Specific Endpoints (Optional)
          </label>
          <button
            type="button"
            onClick={addEndpoint}
            className="text-sm text-[var(--accent-default)] hover:text-[var(--accent-hover)] font-medium"
          >
            + Add Endpoint
          </button>
        </div>
        {endpoints.length > 0 && (
          <div className="space-y-2">
            {endpoints.map((endpoint, index) => (
              <div key={index} className="flex gap-2">
                <input
                  type="text"
                  value={endpoint}
                  onChange={(e) => updateEndpoint(index, e.target.value)}
                  placeholder={specFormat === 'openapi' ? '/api/users' : 'users, user'}
                  className="flex-1 px-4 py-2 rounded-lg border border-[var(--border-default)] bg-white text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-default)] focus:border-transparent font-mono text-sm"
                />
                <button
                  type="button"
                  onClick={() => removeEndpoint(index)}
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
          Leave empty to generate test cases for all endpoints, or specify which ones to focus on.
        </p>
      </div>
    </div>
  );
}

export default ApiSpecTab;
