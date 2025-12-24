'use client';

import { useEcommerceStore, type EntityCategory } from '@/lib/stores/ecommerce-store';

const CATEGORIES: { id: EntityCategory; label: string }[] = [
  { id: 'all', label: 'All Entities' },
  { id: 'core', label: 'Core' },
  { id: 'transactional', label: 'Transactional' },
  { id: 'financial', label: 'Financial' },
  { id: 'catalog', label: 'Catalog' },
  { id: 'fulfillment', label: 'Fulfillment' },
];

export function EntitiesView() {
  const entities = useEcommerceStore((state) => state.entities);
  const entityCategory = useEcommerceStore((state) => state.entityCategory);
  const setEntityCategory = useEcommerceStore((state) => state.setEntityCategory);
  const selectedEntity = useEcommerceStore((state) => state.selectedEntity);
  const selectedEntityName = useEcommerceStore((state) => state.selectedEntityName);
  const selectEntity = useEcommerceStore((state) => state.selectEntity);
  const clearSelectedEntity = useEcommerceStore((state) => state.clearSelectedEntity);
  const isLoadingEntities = useEcommerceStore((state) => state.isLoadingEntities);
  const isLoadingEntityDetails = useEcommerceStore((state) => state.isLoadingEntityDetails);

  const filteredEntities = entityCategory === 'all'
    ? entities
    : entities.filter(e => e.category === entityCategory);

  return (
    <div className="space-y-6">
      {/* Category Filter */}
      <div className="flex flex-wrap gap-2">
        {CATEGORIES.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setEntityCategory(cat.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              entityCategory === cat.id
                ? 'bg-[var(--accent-default)] text-white'
                : 'bg-[var(--surface-secondary)] text-[var(--text-secondary)] hover:bg-[var(--surface-tertiary)]'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Entity List */}
        <div className="bg-[var(--surface-primary)] border border-[var(--border-default)] rounded-xl overflow-hidden">
          <div className="p-4 border-b border-[var(--border-default)]">
            <h3 className="font-semibold text-[var(--text-primary)]">
              Entities ({filteredEntities.length})
            </h3>
          </div>
          <div className="max-h-[500px] overflow-y-auto">
            {isLoadingEntities ? (
              <div className="p-8 text-center text-[var(--text-muted)]">
                Loading entities...
              </div>
            ) : filteredEntities.length === 0 ? (
              <div className="p-8 text-center text-[var(--text-muted)]">
                No entities found
              </div>
            ) : (
              <div className="divide-y divide-[var(--border-default)]">
                {filteredEntities.map((entity) => (
                  <button
                    key={entity.name}
                    onClick={() => selectEntity(entity.name)}
                    className={`w-full p-4 text-left hover:bg-[var(--surface-secondary)] transition-colors ${
                      selectedEntityName === entity.name ? 'bg-[var(--surface-secondary)]' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-[var(--text-primary)] capitalize">{entity.name}</h4>
                        <p className="text-sm text-[var(--text-muted)] mt-0.5">{entity.description}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs px-2 py-1 bg-[var(--surface-tertiary)] rounded text-[var(--text-muted)]">
                          {entity.fieldCount} fields
                        </span>
                        <span className="text-xs px-2 py-1 bg-[var(--accent-default)]/10 text-[var(--accent-default)] rounded capitalize">
                          {entity.category}
                        </span>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Entity Details */}
        <div className="bg-[var(--surface-primary)] border border-[var(--border-default)] rounded-xl overflow-hidden">
          <div className="p-4 border-b border-[var(--border-default)] flex items-center justify-between">
            <h3 className="font-semibold text-[var(--text-primary)]">
              {selectedEntity ? (
                <span className="capitalize">{selectedEntity.name} Details</span>
              ) : (
                'Select an Entity'
              )}
            </h3>
            {selectedEntity && (
              <button
                onClick={clearSelectedEntity}
                className="text-[var(--text-muted)] hover:text-[var(--text-primary)]"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
          <div className="max-h-[500px] overflow-y-auto p-4">
            {isLoadingEntityDetails ? (
              <div className="text-center text-[var(--text-muted)] py-8">
                Loading entity details...
              </div>
            ) : !selectedEntity ? (
              <div className="text-center text-[var(--text-muted)] py-8">
                Click on an entity to view its details
              </div>
            ) : (
              <div className="space-y-6">
                {/* Description */}
                <div>
                  <p className="text-[var(--text-secondary)]">{selectedEntity.description}</p>
                </div>

                {/* Fields */}
                {selectedEntity.fields.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-3">Fields</h4>
                    <div className="space-y-2">
                      {selectedEntity.fields.map((field) => (
                        <div key={field.name} className="p-3 bg-[var(--surface-secondary)] rounded-lg">
                          <div className="flex items-center justify-between">
                            <span className="font-medium text-[var(--text-primary)]">{field.name}</span>
                            <div className="flex items-center gap-2">
                              <span className="text-xs px-2 py-0.5 bg-[var(--surface-tertiary)] rounded text-[var(--text-muted)]">
                                {field.type}
                              </span>
                              {field.required && (
                                <span className="text-xs px-2 py-0.5 bg-[var(--accent-default)] text-white rounded">
                                  required
                                </span>
                              )}
                            </div>
                          </div>
                          <p className="text-sm text-[var(--text-muted)] mt-1">{field.description}</p>
                          {field.example && (
                            <p className="text-xs text-[var(--text-muted)] mt-1">
                              Example: <code className="bg-[var(--surface-tertiary)] px-1 rounded">{field.example}</code>
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Relationships */}
                {selectedEntity.relationships.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-3">Relationships</h4>
                    <div className="space-y-2">
                      {selectedEntity.relationships.map((rel, idx) => (
                        <div key={idx} className="p-3 bg-[var(--surface-secondary)] rounded-lg">
                          <div className="flex items-center gap-2">
                            <span className="text-[var(--text-primary)] capitalize">{rel.sourceEntity}</span>
                            <svg className="w-4 h-4 text-[var(--text-muted)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                            </svg>
                            <span className="text-[var(--text-primary)] capitalize">{rel.targetEntity}</span>
                            <span className="text-xs px-2 py-0.5 bg-[var(--surface-tertiary)] rounded text-[var(--text-muted)]">
                              {rel.relationshipType.replace('_', ' ')}
                            </span>
                          </div>
                          <p className="text-sm text-[var(--text-muted)] mt-1">{rel.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Business Rules */}
                {selectedEntity.rules.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-3">Business Rules</h4>
                    <div className="space-y-2">
                      {selectedEntity.rules.map((rule) => (
                        <div key={rule.id} className="p-3 bg-[var(--surface-secondary)] rounded-lg">
                          <div className="flex items-center justify-between">
                            <span className="font-medium text-[var(--text-primary)]">{rule.name}</span>
                            <span className={`text-xs px-2 py-0.5 rounded ${
                              rule.severity === 'error' ? 'bg-red-100 text-red-700' :
                              rule.severity === 'warning' ? 'bg-yellow-100 text-yellow-700' :
                              'bg-blue-100 text-blue-700'
                            }`}>
                              {rule.severity}
                            </span>
                          </div>
                          <p className="text-sm text-[var(--text-muted)] mt-1">{rule.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Edge Cases */}
                {selectedEntity.edgeCases.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-3">Edge Cases</h4>
                    <ul className="space-y-1">
                      {selectedEntity.edgeCases.map((edgeCase, idx) => (
                        <li key={idx} className="text-sm text-[var(--text-secondary)] flex items-start gap-2">
                          <svg className="w-4 h-4 text-[var(--accent-default)] mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                          </svg>
                          {edgeCase}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Test Scenarios */}
                {selectedEntity.testScenarios.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-3">Test Scenarios</h4>
                    <ul className="space-y-1">
                      {selectedEntity.testScenarios.map((scenario, idx) => (
                        <li key={idx} className="text-sm text-[var(--text-secondary)] flex items-start gap-2">
                          <svg className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          {scenario}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
