'use client';

import { useEcommerceStore } from '@/lib/stores/ecommerce-store';

interface FeatureCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  count?: number;
  countLabel?: string;
  onClick: () => void;
}

function FeatureCard({ title, description, icon, count, countLabel, onClick }: FeatureCardProps) {
  return (
    <button
      onClick={onClick}
      className="bg-[var(--surface-primary)] border border-[var(--border-default)] rounded-xl p-6 text-left hover:border-[var(--accent-default)] hover:shadow-lg transition-all group"
    >
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 bg-[var(--accent-default)]/10 rounded-lg flex items-center justify-center text-[var(--accent-default)] group-hover:bg-[var(--accent-default)] group-hover:text-white transition-colors">
          {icon}
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-[var(--text-primary)]">{title}</h3>
          <p className="text-sm text-[var(--text-muted)] mt-1">{description}</p>
          {count !== undefined && (
            <div className="mt-3 flex items-center gap-2">
              <span className="text-2xl font-bold text-[var(--accent-default)]">{count}</span>
              <span className="text-sm text-[var(--text-muted)]">{countLabel}</span>
            </div>
          )}
        </div>
      </div>
    </button>
  );
}

interface QuickActionProps {
  title: string;
  icon: React.ReactNode;
  onClick: () => void;
}

function QuickAction({ title, icon, onClick }: QuickActionProps) {
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-2 px-4 py-2 bg-[var(--surface-secondary)] rounded-lg hover:bg-[var(--accent-default)] hover:text-white transition-colors text-[var(--text-secondary)]"
    >
      {icon}
      <span className="text-sm font-medium">{title}</span>
    </button>
  );
}

export function EcommerceDashboard() {
  const setActiveView = useEcommerceStore((state) => state.setActiveView);
  const entities = useEcommerceStore((state) => state.entities);
  const workflows = useEcommerceStore((state) => state.workflows);
  const healthStatus = useEcommerceStore((state) => state.healthStatus);
  const historyEntries = useEcommerceStore((state) => state.historyEntries);

  const recentGenerations = historyEntries.slice(0, 3);

  return (
    <div className="space-y-8">
      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-[var(--surface-primary)] border border-[var(--border-default)] rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-[var(--text-muted)]">Domain Entities</span>
            <svg className="w-5 h-5 text-[var(--accent-default)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <div className="mt-2 text-2xl font-bold text-[var(--text-primary)]">{entities.length}</div>
        </div>

        <div className="bg-[var(--surface-primary)] border border-[var(--border-default)] rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-[var(--text-muted)]">Workflows</span>
            <svg className="w-5 h-5 text-[var(--accent-default)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
            </svg>
          </div>
          <div className="mt-2 text-2xl font-bold text-[var(--text-primary)]">{workflows.length}</div>
        </div>

        <div className="bg-[var(--surface-primary)] border border-[var(--border-default)] rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-[var(--text-muted)]">Generations</span>
            <svg className="w-5 h-5 text-[var(--accent-default)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div className="mt-2 text-2xl font-bold text-[var(--text-primary)]">{historyEntries.length}</div>
        </div>

        <div className="bg-[var(--surface-primary)] border border-[var(--border-default)] rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-[var(--text-muted)]">Service Status</span>
            <span className={`w-3 h-3 rounded-full ${
              healthStatus === 'healthy' ? 'bg-green-500' :
              healthStatus === 'unhealthy' ? 'bg-red-500' : 'bg-gray-400'
            }`}></span>
          </div>
          <div className={`mt-2 text-2xl font-bold ${
            healthStatus === 'healthy' ? 'text-green-600' :
            healthStatus === 'unhealthy' ? 'text-red-600' : 'text-gray-500'
          }`}>
            {healthStatus === 'healthy' ? 'Healthy' :
             healthStatus === 'unhealthy' ? 'Unhealthy' : 'Unknown'}
          </div>
        </div>
      </div>

      {/* Feature Cards */}
      <div>
        <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Explore Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FeatureCard
            title="Domain Entities"
            description="Browse 35+ digital domain entities with fields, relationships, and business rules"
            icon={
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            }
            count={entities.length}
            countLabel="entities available"
            onClick={() => setActiveView('entities')}
          />

          <FeatureCard
            title="Business Workflows"
            description="Explore checkout, return, and other business flows with step-by-step details"
            icon={
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
              </svg>
            }
            count={workflows.length}
            countLabel="workflows defined"
            onClick={() => setActiveView('workflows')}
          />

          <FeatureCard
            title="Knowledge Base"
            description="Search domain knowledge including business rules, edge cases, and test patterns"
            icon={
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            }
            onClick={() => setActiveView('knowledge')}
          />

          <FeatureCard
            title="Test Data Generation"
            description="Generate context-aware test data with domain intelligence and edge case coverage"
            icon={
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            }
            onClick={() => setActiveView('generate')}
          />
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Quick Actions</h2>
        <div className="flex flex-wrap gap-3">
          <QuickAction
            title="Generate Cart Data"
            icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" /></svg>}
            onClick={() => setActiveView('generate')}
          />
          <QuickAction
            title="View Checkout Flow"
            icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>}
            onClick={() => setActiveView('workflows')}
          />
          <QuickAction
            title="Search Business Rules"
            icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>}
            onClick={() => setActiveView('knowledge')}
          />
          <QuickAction
            title="Browse Order Entity"
            icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>}
            onClick={() => setActiveView('entities')}
          />
        </div>
      </div>

      {/* Recent Generations */}
      {recentGenerations.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Recent Generations</h2>
          <div className="bg-[var(--surface-primary)] border border-[var(--border-default)] rounded-xl overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="bg-[var(--surface-secondary)]">
                  <th className="text-left px-4 py-3 text-sm font-medium text-[var(--text-muted)]">Entity</th>
                  <th className="text-left px-4 py-3 text-sm font-medium text-[var(--text-muted)]">Records</th>
                  <th className="text-left px-4 py-3 text-sm font-medium text-[var(--text-muted)]">Workflow</th>
                  <th className="text-left px-4 py-3 text-sm font-medium text-[var(--text-muted)]">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border-default)]">
                {recentGenerations.map((entry) => (
                  <tr key={entry.id} className="hover:bg-[var(--surface-secondary)]">
                    <td className="px-4 py-3 text-sm text-[var(--text-primary)] font-medium capitalize">{entry.entity}</td>
                    <td className="px-4 py-3 text-sm text-[var(--text-secondary)]">{entry.recordCount}</td>
                    <td className="px-4 py-3 text-sm text-[var(--text-secondary)]">{entry.workflow || '-'}</td>
                    <td className="px-4 py-3 text-sm text-[var(--text-muted)]">
                      {new Date(entry.timestamp).toLocaleTimeString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
