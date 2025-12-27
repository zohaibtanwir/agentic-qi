'use client';

import { useEffect, useRef } from 'react';
import { useEcommerceStore } from '@/lib/stores/ecommerce-store';
import { useToastActions } from '@/components/ui/Toast';
import { EcommerceSidebar } from '@/components/ecommerce/EcommerceSidebar';
import { EcommerceDashboard } from '@/components/ecommerce/EcommerceDashboard';
import { EntitiesView } from '@/components/ecommerce/EntitiesView';
import { WorkflowsView } from '@/components/ecommerce/WorkflowsView';
import { KnowledgeView } from '@/components/ecommerce/KnowledgeView';
import { GenerateView } from '@/components/ecommerce/GenerateView';

export default function EcommercePage() {
  const activeView = useEcommerceStore((state) => state.activeView);
  const error = useEcommerceStore((state) => state.error);
  const clearError = useEcommerceStore((state) => state.clearError);
  const loadEntities = useEcommerceStore((state) => state.loadEntities);
  const loadWorkflows = useEcommerceStore((state) => state.loadWorkflows);
  const checkHealth = useEcommerceStore((state) => state.checkHealth);
  const sidebarCollapsed = useEcommerceStore((state) => state.sidebarCollapsed);
  const generatedData = useEcommerceStore((state) => state.generatedData);
  const healthStatus = useEcommerceStore((state) => state.healthStatus);

  const toast = useToastActions();
  const initialLoadRef = useRef(false);
  const prevErrorRef = useRef<string | null>(null);
  const prevGeneratedDataRef = useRef<string>('');
  const prevHealthStatusRef = useRef<string>('unknown');

  useEffect(() => {
    if (!initialLoadRef.current) {
      initialLoadRef.current = true;
      // Initial data load - explicitly load all entities
      loadEntities('all');
      loadWorkflows();
      checkHealth();
    }
  }, [loadEntities, loadWorkflows, checkHealth]);

  // Toast notification for errors
  useEffect(() => {
    if (error && error !== prevErrorRef.current) {
      toast.error(error);
    }
    prevErrorRef.current = error;
  }, [error, toast]);

  // Toast notification for successful generation
  useEffect(() => {
    if (generatedData && generatedData !== prevGeneratedDataRef.current && prevGeneratedDataRef.current !== '') {
      toast.success('Test data generated successfully');
    }
    prevGeneratedDataRef.current = generatedData;
  }, [generatedData, toast]);

  // Toast notification for health status changes
  useEffect(() => {
    if (healthStatus !== prevHealthStatusRef.current && prevHealthStatusRef.current !== 'unknown') {
      if (healthStatus === 'healthy') {
        toast.success('Digital service is healthy');
      } else if (healthStatus === 'unhealthy') {
        toast.warning('Digital service is unhealthy');
      }
    }
    prevHealthStatusRef.current = healthStatus;
  }, [healthStatus, toast]);

  const renderActiveView = () => {
    switch (activeView) {
      case 'dashboard':
        return <EcommerceDashboard />;
      case 'entities':
        return <EntitiesView />;
      case 'workflows':
        return <WorkflowsView />;
      case 'knowledge':
        return <KnowledgeView />;
      case 'generate':
        return <GenerateView />;
      default:
        return <EcommerceDashboard />;
    }
  };

  return (
    <main className="flex h-[calc(100vh-4rem)]">
      {/* Sidebar Navigation */}
      <EcommerceSidebar />

      {/* Main Content Area */}
      <div className={`flex-1 overflow-auto transition-all duration-300 ${sidebarCollapsed ? 'ml-16' : 'ml-64'}`}>
        <div className="max-w-7xl mx-auto px-6 py-8">
          {/* Page Header */}
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-[var(--accent-default)] rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">
                  Digital Domain Agent
                </h1>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                    <span className="w-1.5 h-1.5 bg-green-500 rounded-full mr-1.5"></span>
                    Operational
                  </span>
                  <span className="text-sm text-[var(--text-muted)]">v1.0.0</span>
                </div>
              </div>
            </div>
            <p className="text-[var(--text-secondary)] mt-3 max-w-2xl">
              Explore digital domain knowledge, entities, workflows, and generate
              context-aware test data with business rule intelligence.
            </p>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-red-700">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="font-medium">Error</span>
                </div>
                <button
                  onClick={clearError}
                  className="text-red-500 hover:text-red-700"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <p className="mt-1 text-sm text-red-600">{error}</p>
            </div>
          )}

          {/* Active View Content */}
          {renderActiveView()}
        </div>
      </div>
    </main>
  );
}
