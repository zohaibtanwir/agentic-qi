'use client';

import { useEcommerceStore, type EcommerceView } from '@/lib/stores/ecommerce-store';

interface NavItem {
  id: EcommerceView;
  label: string;
  icon: React.ReactNode;
  description: string;
}

const navItems: NavItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    description: 'Overview & health status',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
      </svg>
    ),
  },
  {
    id: 'entities',
    label: 'Entities',
    description: 'Browse domain entities',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
    ),
  },
  {
    id: 'workflows',
    label: 'Workflows',
    description: 'Explore business flows',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
      </svg>
    ),
  },
  {
    id: 'knowledge',
    label: 'Knowledge',
    description: 'Search domain knowledge',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
    ),
  },
  {
    id: 'generate',
    label: 'Generate',
    description: 'Create test data',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
  },
];

export function EcommerceSidebar() {
  const activeView = useEcommerceStore((state) => state.activeView);
  const setActiveView = useEcommerceStore((state) => state.setActiveView);
  const sidebarCollapsed = useEcommerceStore((state) => state.sidebarCollapsed);
  const toggleSidebar = useEcommerceStore((state) => state.toggleSidebar);
  const healthStatus = useEcommerceStore((state) => state.healthStatus);
  const entities = useEcommerceStore((state) => state.entities);
  const workflows = useEcommerceStore((state) => state.workflows);

  return (
    <aside
      className={`fixed left-0 top-16 h-[calc(100vh-4rem)] bg-[var(--surface-primary)] border-r border-[var(--border-default)] transition-all duration-300 z-10 ${
        sidebarCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      <div className="flex flex-col h-full">
        {/* Toggle Button */}
        <div className="p-3 border-b border-[var(--border-default)]">
          <button
            onClick={toggleSidebar}
            className="w-full flex items-center justify-center p-2 rounded-lg hover:bg-[var(--surface-secondary)] transition-colors"
            title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            <svg
              className={`w-5 h-5 text-[var(--text-muted)] transition-transform ${sidebarCollapsed ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
            </svg>
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = activeView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveView(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                  isActive
                    ? 'bg-[var(--accent-default)] text-white'
                    : 'text-[var(--text-secondary)] hover:bg-[var(--surface-secondary)] hover:text-[var(--text-primary)]'
                }`}
                title={sidebarCollapsed ? item.label : undefined}
              >
                <span className={`flex-shrink-0 ${isActive ? 'text-white' : ''}`}>
                  {item.icon}
                </span>
                {!sidebarCollapsed && (
                  <div className="flex-1 text-left">
                    <div className="text-sm font-medium">{item.label}</div>
                    <div className={`text-xs ${isActive ? 'text-white/70' : 'text-[var(--text-muted)]'}`}>
                      {item.description}
                    </div>
                  </div>
                )}
              </button>
            );
          })}
        </nav>

        {/* Stats Footer */}
        {!sidebarCollapsed && (
          <div className="p-4 border-t border-[var(--border-default)]">
            <div className="space-y-3">
              {/* Health Status */}
              <div className="flex items-center justify-between text-sm">
                <span className="text-[var(--text-muted)]">Status</span>
                <span className={`flex items-center gap-1.5 ${
                  healthStatus === 'healthy' ? 'text-green-600' :
                  healthStatus === 'unhealthy' ? 'text-red-600' : 'text-gray-400'
                }`}>
                  <span className={`w-2 h-2 rounded-full ${
                    healthStatus === 'healthy' ? 'bg-green-500' :
                    healthStatus === 'unhealthy' ? 'bg-red-500' : 'bg-gray-400'
                  }`}></span>
                  {healthStatus === 'healthy' ? 'Healthy' :
                   healthStatus === 'unhealthy' ? 'Unhealthy' : 'Unknown'}
                </span>
              </div>

              {/* Entity Count */}
              <div className="flex items-center justify-between text-sm">
                <span className="text-[var(--text-muted)]">Entities</span>
                <span className="text-[var(--text-primary)] font-medium">{entities.length}</span>
              </div>

              {/* Workflow Count */}
              <div className="flex items-center justify-between text-sm">
                <span className="text-[var(--text-muted)]">Workflows</span>
                <span className="text-[var(--text-primary)] font-medium">{workflows.length}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
