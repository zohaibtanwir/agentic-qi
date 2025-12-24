'use client';

import { useState } from 'react';
import { useEcommerceStore } from '@/lib/stores/ecommerce-store';

export function KnowledgeView() {
  const knowledgeItems = useEcommerceStore((state) => state.knowledgeItems);
  const edgeCases = useEcommerceStore((state) => state.edgeCases);
  const isSearchingKnowledge = useEcommerceStore((state) => state.isSearchingKnowledge);
  const isLoadingEdgeCases = useEcommerceStore((state) => state.isLoadingEdgeCases);
  const setKnowledgeQuery = useEcommerceStore((state) => state.setKnowledgeQuery);
  const searchKnowledge = useEcommerceStore((state) => state.searchKnowledge);
  const loadEdgeCases = useEcommerceStore((state) => state.loadEdgeCases);

  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'search' | 'edge-cases'>('search');
  const [edgeCaseEntity, setEdgeCaseEntity] = useState('');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setKnowledgeQuery(searchQuery.trim());
      await searchKnowledge();
    }
  };

  const performQuickSearch = async (term: string) => {
    setSearchQuery(term);
    setKnowledgeQuery(term);
    await searchKnowledge();
  };

  const handleLoadEdgeCases = async () => {
    if (edgeCaseEntity.trim()) {
      await loadEdgeCases(edgeCaseEntity.trim());
    }
  };

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-[var(--border-default)]">
        <button
          onClick={() => setActiveTab('search')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'search'
              ? 'border-[var(--accent-default)] text-[var(--accent-default)]'
              : 'border-transparent text-[var(--text-muted)] hover:text-[var(--text-primary)]'
          }`}
        >
          Knowledge Search
        </button>
        <button
          onClick={() => setActiveTab('edge-cases')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'edge-cases'
              ? 'border-[var(--accent-default)] text-[var(--accent-default)]'
              : 'border-transparent text-[var(--text-muted)] hover:text-[var(--text-primary)]'
          }`}
        >
          Edge Cases
        </button>
      </div>

      {activeTab === 'search' && (
        <div className="space-y-6">
          {/* Search Form */}
          <div className="bg-[var(--surface-primary)] border border-[var(--border-default)] rounded-xl p-6">
            <h3 className="font-semibold text-[var(--text-primary)] mb-4">Search Domain Knowledge</h3>
            <form onSubmit={handleSearch} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                  Search Query
                </label>
                <div className="flex gap-3">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="e.g., checkout validation rules, cart limits, payment processing..."
                    className="flex-1 px-4 py-2.5 bg-[var(--surface-secondary)] border border-[var(--border-default)] rounded-lg text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-default)] focus:border-transparent"
                  />
                  <button
                    type="submit"
                    disabled={isSearchingKnowledge || !searchQuery.trim()}
                    className="px-6 py-2.5 bg-[var(--accent-default)] text-white rounded-lg font-medium hover:bg-[var(--accent-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                  >
                    {isSearchingKnowledge ? (
                      <>
                        <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Searching...
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                        Search
                      </>
                    )}
                  </button>
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                <span className="text-sm text-[var(--text-muted)]">Quick searches:</span>
                {['checkout rules', 'payment validation', 'inventory management', 'return policy'].map((term) => (
                  <button
                    key={term}
                    type="button"
                    onClick={() => performQuickSearch(term)}
                    className="text-xs px-3 py-1 bg-[var(--surface-secondary)] text-[var(--text-secondary)] rounded-full hover:bg-[var(--accent-default)] hover:text-white transition-colors"
                  >
                    {term}
                  </button>
                ))}
              </div>
            </form>
          </div>

          {/* Search Results */}
          <div className="bg-[var(--surface-primary)] border border-[var(--border-default)] rounded-xl overflow-hidden">
            <div className="p-4 border-b border-[var(--border-default)]">
              <h3 className="font-semibold text-[var(--text-primary)]">
                Search Results ({knowledgeItems.length})
              </h3>
            </div>
            <div className="max-h-[500px] overflow-y-auto">
              {knowledgeItems.length === 0 ? (
                <div className="p-8 text-center text-[var(--text-muted)]">
                  {searchQuery ? 'No results found. Try a different search term.' : 'Enter a search query to find domain knowledge.'}
                </div>
              ) : (
                <div className="divide-y divide-[var(--border-default)]">
                  {knowledgeItems.map((item, idx) => (
                    <div key={idx} className="p-4 hover:bg-[var(--surface-secondary)] transition-colors">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span className={`text-xs px-2 py-0.5 rounded ${
                              item.category === 'entity' ? 'bg-blue-100 text-blue-700' :
                              item.category === 'workflow' ? 'bg-purple-100 text-purple-700' :
                              item.category === 'rule' ? 'bg-orange-100 text-orange-700' :
                              'bg-gray-100 text-gray-700'
                            }`}>
                              {item.category}
                            </span>
                            {item.relevanceScore > 0 && (
                              <span className="text-xs text-[var(--text-muted)]">
                                {Math.round(item.relevanceScore * 100)}% relevant
                              </span>
                            )}
                          </div>
                          <h4 className="font-medium text-[var(--text-primary)]">{item.title}</h4>
                          <p className="text-sm text-[var(--text-muted)] mt-1">{item.content}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'edge-cases' && (
        <div className="space-y-6">
          {/* Edge Case Loader */}
          <div className="bg-[var(--surface-primary)] border border-[var(--border-default)] rounded-xl p-6">
            <h3 className="font-semibold text-[var(--text-primary)] mb-4">Load Entity Edge Cases</h3>
            <div className="flex gap-3">
              <input
                type="text"
                value={edgeCaseEntity}
                onChange={(e) => setEdgeCaseEntity(e.target.value)}
                placeholder="Enter entity name (e.g., cart, order, payment)"
                className="flex-1 px-4 py-2.5 bg-[var(--surface-secondary)] border border-[var(--border-default)] rounded-lg text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-default)] focus:border-transparent"
              />
              <button
                onClick={handleLoadEdgeCases}
                disabled={isLoadingEdgeCases || !edgeCaseEntity.trim()}
                className="px-6 py-2.5 bg-[var(--accent-default)] text-white rounded-lg font-medium hover:bg-[var(--accent-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              >
                {isLoadingEdgeCases ? (
                  <>
                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Loading...
                  </>
                ) : (
                  'Load Edge Cases'
                )}
              </button>
            </div>

            <div className="flex flex-wrap gap-2 mt-4">
              <span className="text-sm text-[var(--text-muted)]">Common entities:</span>
              {['cart', 'order', 'payment', 'inventory', 'shipping'].map((entity) => (
                <button
                  key={entity}
                  type="button"
                  onClick={() => {
                    setEdgeCaseEntity(entity);
                    loadEdgeCases(entity);
                  }}
                  className="text-xs px-3 py-1 bg-[var(--surface-secondary)] text-[var(--text-secondary)] rounded-full hover:bg-[var(--accent-default)] hover:text-white transition-colors capitalize"
                >
                  {entity}
                </button>
              ))}
            </div>
          </div>

          {/* Edge Cases List */}
          <div className="bg-[var(--surface-primary)] border border-[var(--border-default)] rounded-xl overflow-hidden">
            <div className="p-4 border-b border-[var(--border-default)]">
              <h3 className="font-semibold text-[var(--text-primary)]">
                Edge Cases ({edgeCases.length})
              </h3>
            </div>
            <div className="max-h-[500px] overflow-y-auto">
              {edgeCases.length === 0 ? (
                <div className="p-8 text-center text-[var(--text-muted)]">
                  Select an entity to view its edge cases and test scenarios.
                </div>
              ) : (
                <div className="divide-y divide-[var(--border-default)]">
                  {edgeCases.map((edgeCase, idx) => (
                    <div key={edgeCase.id || idx} className="p-4 hover:bg-[var(--surface-secondary)] transition-colors">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 bg-orange-100 text-orange-600">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                          </svg>
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-medium text-[var(--text-primary)]">{edgeCase.name}</h4>
                            <span className="text-xs px-2 py-0.5 rounded capitalize bg-blue-100 text-blue-700">
                              {edgeCase.category}
                            </span>
                          </div>
                          <p className="text-sm text-[var(--text-muted)]">{edgeCase.description}</p>
                          {edgeCase.testApproach && (
                            <div className="mt-2 p-2 bg-[var(--surface-tertiary)] rounded text-sm">
                              <span className="text-[var(--text-muted)]">Test Approach: </span>
                              <span className="text-[var(--text-secondary)]">{edgeCase.testApproach}</span>
                            </div>
                          )}
                          {edgeCase.expectedBehavior && (
                            <div className="mt-2 p-2 bg-[var(--surface-tertiary)] rounded text-sm">
                              <span className="text-[var(--text-muted)]">Expected Behavior: </span>
                              <span className="text-[var(--text-secondary)]">{edgeCase.expectedBehavior}</span>
                            </div>
                          )}
                          {edgeCase.entity && (
                            <div className="flex flex-wrap gap-1.5 mt-2">
                              <span className="text-xs px-2 py-0.5 bg-[var(--accent-default)]/10 text-[var(--accent-default)] rounded capitalize">
                                {edgeCase.entity}
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
