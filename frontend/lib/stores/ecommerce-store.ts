import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import {
  ecommerceClient,
  GenerationMethod as ProtoGenerationMethod,
  type Entity,
  type EntitySummary,
  type Workflow,
  type WorkflowSummary,
  type KnowledgeItem,
  type EdgeCase,
  type GenerateTestDataResponse,
} from '../grpc/ecommerceClient';

// Map frontend generation method to proto enum
const generationMethodToProto: Record<GenerationMethod, ProtoGenerationMethod> = {
  'TRADITIONAL': ProtoGenerationMethod.GENERATION_METHOD_TRADITIONAL,
  'LLM': ProtoGenerationMethod.GENERATION_METHOD_LLM,
  'RAG': ProtoGenerationMethod.GENERATION_METHOD_RAG,
  'HYBRID': ProtoGenerationMethod.GENERATION_METHOD_HYBRID,
};

// ============= Types =============

export type EcommerceView = 'dashboard' | 'entities' | 'workflows' | 'knowledge' | 'generate';
export type EntityCategory = 'all' | 'core' | 'transactional' | 'financial' | 'catalog' | 'fulfillment';

// Generation method types matching backend proto
export type GenerationMethod = 'TRADITIONAL' | 'LLM' | 'RAG' | 'HYBRID';

export interface GenerateFormState {
  entity: string;
  workflow?: string;
  count: number;
  includeEdgeCases: boolean;
  includeRelationships: boolean;
  validateRules: boolean;
  customContext: string;
  generationMethod: GenerationMethod;
  productionLike: boolean;
}

export interface HistoryEntry {
  id: string;
  timestamp: number;
  entity: string;
  workflow?: string;
  count: number;
  recordCount: number;
  includeEdgeCases: boolean;
  includeRelationships: boolean;
  validateRules: boolean;
  customContext: string;
  data: string;
  domainContext: string;
}

export interface KnowledgeSearchState {
  query: string;
  categories: string[];
  maxResults: number;
}

export interface EcommerceState {
  // Navigation
  activeView: EcommerceView;
  sidebarCollapsed: boolean;

  // Entities
  entities: EntitySummary[];
  selectedEntityName: string | null;
  selectedEntity: Entity | null;
  entityCategory: EntityCategory;
  isLoadingEntities: boolean;
  isLoadingEntityDetails: boolean;

  // Workflows
  workflows: WorkflowSummary[];
  selectedWorkflowName: string | null;
  selectedWorkflow: Workflow | null;
  isLoadingWorkflows: boolean;
  isLoadingWorkflowDetails: boolean;

  // Knowledge
  knowledgeSearch: KnowledgeSearchState;
  knowledgeItems: KnowledgeItem[];
  knowledgeSummary: string;
  isSearchingKnowledge: boolean;

  // Edge Cases
  edgeCases: EdgeCase[];
  isLoadingEdgeCases: boolean;

  // Generation
  generateForm: GenerateFormState;
  generatedData: string;
  lastGenerateResponse: GenerateTestDataResponse | null;
  isGenerating: boolean;
  historyEntries: HistoryEntry[];

  // Health
  healthStatus: 'unknown' | 'healthy' | 'unhealthy';

  // Errors
  error: string | null;
}

export interface EcommerceActions {
  // Navigation
  setActiveView: (view: EcommerceView) => void;
  toggleSidebar: () => void;

  // Entity actions
  loadEntities: (category?: string) => Promise<void>;
  setEntityCategory: (category: EntityCategory) => void;
  selectEntity: (entityName: string) => Promise<void>;
  clearSelectedEntity: () => void;

  // Workflow actions
  loadWorkflows: () => Promise<void>;
  selectWorkflow: (workflowName: string) => Promise<void>;
  clearSelectedWorkflow: () => void;

  // Knowledge actions
  setKnowledgeQuery: (query: string) => void;
  setKnowledgeCategories: (categories: string[]) => void;
  searchKnowledge: () => Promise<void>;
  clearKnowledgeResults: () => void;

  // Edge case actions
  loadEdgeCases: (entity?: string, workflow?: string) => Promise<void>;

  // Generation actions
  setGenerateFormField: <K extends keyof GenerateFormState>(field: K, value: GenerateFormState[K]) => void;
  updateGenerateForm: (updates: Partial<GenerateFormState>) => void;
  generateTestData: () => Promise<void>;
  clearGeneratedData: () => void;
  loadHistoryEntry: (id: string) => void;
  deleteHistoryEntry: (id: string) => void;
  clearHistory: () => void;

  // Health actions
  checkHealth: () => Promise<void>;

  // Error actions
  clearError: () => void;
}

export type EcommerceStore = EcommerceState & EcommerceActions;

// ============= Default Values =============

const defaultKnowledgeSearch: KnowledgeSearchState = {
  query: '',
  categories: [],
  maxResults: 10,
};

const defaultGenerateForm: GenerateFormState = {
  entity: '',
  workflow: undefined,
  count: 10,
  includeEdgeCases: false,
  includeRelationships: false,
  validateRules: true,
  customContext: '',
  generationMethod: 'LLM',
  productionLike: true,
};

const initialState: EcommerceState = {
  activeView: 'dashboard',
  sidebarCollapsed: false,

  entities: [],
  selectedEntityName: null,
  selectedEntity: null,
  entityCategory: 'all',
  isLoadingEntities: false,
  isLoadingEntityDetails: false,

  workflows: [],
  selectedWorkflowName: null,
  selectedWorkflow: null,
  isLoadingWorkflows: false,
  isLoadingWorkflowDetails: false,

  knowledgeSearch: defaultKnowledgeSearch,
  knowledgeItems: [],
  knowledgeSummary: '',
  isSearchingKnowledge: false,

  edgeCases: [],
  isLoadingEdgeCases: false,

  generateForm: defaultGenerateForm,
  generatedData: '',
  lastGenerateResponse: null,
  isGenerating: false,
  historyEntries: [],

  healthStatus: 'unknown',
  error: null,
};

// ============= Store =============

export const useEcommerceStore = create<EcommerceStore>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        // Navigation actions
        setActiveView: (view) => {
          set({ activeView: view, error: null }, false, 'setActiveView');
        },

        toggleSidebar: () => {
          set(
            (state) => ({ sidebarCollapsed: !state.sidebarCollapsed }),
            false,
            'toggleSidebar'
          );
        },

        // Entity actions
        loadEntities: async (category) => {
          set({ isLoadingEntities: true, error: null }, false, 'loadEntities:start');
          try {
            const response = await ecommerceClient.listEntities({
              category: category === 'all' ? '' : category || '',
            });
            set(
              { entities: response.entities, isLoadingEntities: false },
              false,
              'loadEntities:success'
            );
          } catch (err) {
            set(
              {
                error: err instanceof Error ? err.message : 'Failed to load entities',
                isLoadingEntities: false,
              },
              false,
              'loadEntities:error'
            );
          }
        },

        setEntityCategory: (category) => {
          set({ entityCategory: category }, false, 'setEntityCategory');
          get().loadEntities(category === 'all' ? '' : category);
        },

        selectEntity: async (entityName) => {
          set(
            { selectedEntityName: entityName, isLoadingEntityDetails: true, error: null },
            false,
            'selectEntity:start'
          );
          try {
            const response = await ecommerceClient.getEntity({
              entityName,
              includeRelationships: true,
              includeRules: true,
              includeEdgeCases: true,
            });
            set(
              {
                selectedEntity: response.entity || null,
                isLoadingEntityDetails: false,
              },
              false,
              'selectEntity:success'
            );
          } catch (err) {
            set(
              {
                error: err instanceof Error ? err.message : 'Failed to load entity details',
                isLoadingEntityDetails: false,
              },
              false,
              'selectEntity:error'
            );
          }
        },

        clearSelectedEntity: () => {
          set(
            { selectedEntityName: null, selectedEntity: null },
            false,
            'clearSelectedEntity'
          );
        },

        // Workflow actions
        loadWorkflows: async () => {
          set({ isLoadingWorkflows: true, error: null }, false, 'loadWorkflows:start');
          try {
            const response = await ecommerceClient.listWorkflows({});
            set(
              { workflows: response.workflows, isLoadingWorkflows: false },
              false,
              'loadWorkflows:success'
            );
          } catch (err) {
            set(
              {
                error: err instanceof Error ? err.message : 'Failed to load workflows',
                isLoadingWorkflows: false,
              },
              false,
              'loadWorkflows:error'
            );
          }
        },

        selectWorkflow: async (workflowName) => {
          set(
            { selectedWorkflowName: workflowName, isLoadingWorkflowDetails: true, error: null },
            false,
            'selectWorkflow:start'
          );
          try {
            const response = await ecommerceClient.getWorkflow({
              workflowName,
              includeSteps: true,
              includeEdgeCases: true,
            });
            set(
              {
                selectedWorkflow: response.workflow || null,
                isLoadingWorkflowDetails: false,
              },
              false,
              'selectWorkflow:success'
            );
          } catch (err) {
            set(
              {
                error: err instanceof Error ? err.message : 'Failed to load workflow details',
                isLoadingWorkflowDetails: false,
              },
              false,
              'selectWorkflow:error'
            );
          }
        },

        clearSelectedWorkflow: () => {
          set(
            { selectedWorkflowName: null, selectedWorkflow: null },
            false,
            'clearSelectedWorkflow'
          );
        },

        // Knowledge actions
        setKnowledgeQuery: (query) => {
          set(
            (state) => ({
              knowledgeSearch: { ...state.knowledgeSearch, query },
            }),
            false,
            'setKnowledgeQuery'
          );
        },

        setKnowledgeCategories: (categories) => {
          set(
            (state) => ({
              knowledgeSearch: { ...state.knowledgeSearch, categories },
            }),
            false,
            'setKnowledgeCategories'
          );
        },

        searchKnowledge: async () => {
          const { knowledgeSearch } = get();
          if (!knowledgeSearch.query.trim()) return;

          set({ isSearchingKnowledge: true, error: null }, false, 'searchKnowledge:start');
          try {
            const response = await ecommerceClient.queryKnowledge({
              requestId: `KNW-${Date.now()}`,
              query: knowledgeSearch.query,
              categories: knowledgeSearch.categories,
              maxResults: knowledgeSearch.maxResults,
            });
            set(
              {
                knowledgeItems: response.items,
                knowledgeSummary: response.summary,
                isSearchingKnowledge: false,
              },
              false,
              'searchKnowledge:success'
            );
          } catch (err) {
            set(
              {
                error: err instanceof Error ? err.message : 'Failed to search knowledge base',
                isSearchingKnowledge: false,
              },
              false,
              'searchKnowledge:error'
            );
          }
        },

        clearKnowledgeResults: () => {
          set(
            {
              knowledgeItems: [],
              knowledgeSummary: '',
              knowledgeSearch: defaultKnowledgeSearch,
            },
            false,
            'clearKnowledgeResults'
          );
        },

        // Edge case actions
        loadEdgeCases: async (entity, workflow) => {
          set({ isLoadingEdgeCases: true, error: null }, false, 'loadEdgeCases:start');
          try {
            const response = await ecommerceClient.getEdgeCases({
              entity: entity || '',
              workflow: workflow || '',
              category: '',
            });
            set(
              { edgeCases: response.edgeCases, isLoadingEdgeCases: false },
              false,
              'loadEdgeCases:success'
            );
          } catch (err) {
            set(
              {
                error: err instanceof Error ? err.message : 'Failed to load edge cases',
                isLoadingEdgeCases: false,
              },
              false,
              'loadEdgeCases:error'
            );
          }
        },

        // Generation actions
        setGenerateFormField: (field, value) => {
          set(
            (state) => ({
              generateForm: { ...state.generateForm, [field]: value },
              error: null,
            }),
            false,
            `setGenerateFormField:${field}`
          );
        },

        updateGenerateForm: (updates) => {
          set(
            (state) => ({
              generateForm: { ...state.generateForm, ...updates },
              error: null,
            }),
            false,
            'updateGenerateForm'
          );
        },

        generateTestData: async () => {
          const state = get();
          set({ isGenerating: true, error: null }, false, 'generateTestData:start');

          try {
            const response = await ecommerceClient.generateTestData({
              requestId: `GEN-${Date.now()}`,
              entity: state.generateForm.entity,
              count: state.generateForm.count,
              workflowContext: state.generateForm.workflow || '',
              scenarios: [],
              includeEdgeCases: state.generateForm.includeEdgeCases ?? false,
              customContext: state.generateForm.customContext || '',
              outputFormat: 'JSON',
              scenarioCounts: {},
              generationMethod: generationMethodToProto[state.generateForm.generationMethod ?? 'LLM'],
              productionLike: state.generateForm.productionLike ?? true,
              useCache: true,
            });

            if (response.success) {
              const historyEntry: HistoryEntry = {
                id: `history-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
                timestamp: Date.now(),
                entity: state.generateForm.entity,
                workflow: state.generateForm.workflow,
                count: state.generateForm.count,
                recordCount: response.recordCount,
                includeEdgeCases: state.generateForm.includeEdgeCases,
                includeRelationships: state.generateForm.includeRelationships,
                validateRules: state.generateForm.validateRules,
                customContext: state.generateForm.customContext || '',
                data: response.data,
                domainContext: response.metadata?.domainContextUsed || '',
              };

              set(
                {
                  generatedData: response.data,
                  lastGenerateResponse: response,
                  isGenerating: false,
                  historyEntries: [historyEntry, ...state.historyEntries.slice(0, 19)],
                },
                false,
                'generateTestData:success'
              );
            } else {
              set(
                {
                  error: response.error || 'Generation failed',
                  isGenerating: false,
                },
                false,
                'generateTestData:failed'
              );
            }
          } catch (err) {
            set(
              {
                error: err instanceof Error ? err.message : 'Failed to generate test data',
                isGenerating: false,
              },
              false,
              'generateTestData:error'
            );
          }
        },

        clearGeneratedData: () => {
          set(
            { generatedData: '', lastGenerateResponse: null },
            false,
            'clearGeneratedData'
          );
        },

        loadHistoryEntry: (id) => {
          const state = get();
          const entry = state.historyEntries.find((e) => e.id === id);
          if (entry) {
            set(
              {
                generateForm: {
                  ...state.generateForm,
                  entity: entry.entity,
                  workflow: entry.workflow,
                  count: entry.count,
                },
                generatedData: entry.data,
                lastGenerateResponse: {
                  requestId: entry.id,
                  success: true,
                  data: entry.data,
                  recordCount: entry.recordCount,
                  metadata: {
                    generationPath: 'history',
                    llmTokensUsed: 0,
                    generationTimeMs: 0,
                    coherenceScore: 0,
                    domainContextUsed: entry.domainContext,
                    scenarioCounts: {},
                  },
                  error: '',
                },
              },
              false,
              'loadHistoryEntry'
            );
          }
        },

        deleteHistoryEntry: (id) => {
          set(
            (state) => ({
              historyEntries: state.historyEntries.filter((e) => e.id !== id),
            }),
            false,
            'deleteHistoryEntry'
          );
        },

        clearHistory: () => {
          set({ historyEntries: [] }, false, 'clearHistory');
        },

        // Health actions
        checkHealth: async () => {
          try {
            const response = await ecommerceClient.healthCheck();
            set(
              { healthStatus: response.status === 'healthy' ? 'healthy' : 'unhealthy' },
              false,
              'checkHealth:success'
            );
          } catch {
            set({ healthStatus: 'unhealthy' }, false, 'checkHealth:error');
          }
        },

        // Error actions
        clearError: () => {
          set({ error: null }, false, 'clearError');
        },
      }),
      {
        name: 'ecommerce-store',
        version: 1, // Increment when schema changes
        partialize: (state) => ({
          sidebarCollapsed: state.sidebarCollapsed,
          entityCategory: state.entityCategory,
          generateForm: state.generateForm,
          historyEntries: state.historyEntries,
        }),
        migrate: (persistedState, version) => {
          // Handle migration from older versions
          type PersistedState = {
            sidebarCollapsed: boolean;
            entityCategory: EntityCategory;
            generateForm: GenerateFormState;
            historyEntries: HistoryEntry[];
          };
          const state = persistedState as Partial<PersistedState>;

          if (version === 0) {
            // Migration from version 0 to 1
            // Ensure all generateForm fields exist with defaults
            return {
              sidebarCollapsed: state.sidebarCollapsed ?? false,
              entityCategory: 'all' as EntityCategory,
              generateForm: {
                ...defaultGenerateForm,
                ...(state.generateForm || {}),
              },
              historyEntries: state.historyEntries ?? [],
            };
          }

          // Return with defaults for any missing fields
          return {
            sidebarCollapsed: state.sidebarCollapsed ?? false,
            entityCategory: state.entityCategory ?? 'all',
            generateForm: {
              ...defaultGenerateForm,
              ...(state.generateForm || {}),
            },
            historyEntries: state.historyEntries ?? [],
          };
        },
        merge: (persistedState, currentState) => {
          // Deep merge persisted state with defaults to handle missing fields
          const persisted = persistedState as Partial<EcommerceState>;
          return {
            ...currentState,
            ...persisted,
            // Ensure generateForm has all required fields with defaults
            generateForm: {
              ...defaultGenerateForm,
              ...(persisted.generateForm || {}),
            },
            // Reset entityCategory to 'all' to ensure all entities are visible
            entityCategory: 'all' as EntityCategory,
          };
        },
      }
    ),
    { name: 'EcommerceStore' }
  )
);

// ============= Selectors =============

export const selectActiveView = (state: EcommerceStore) => state.activeView;
export const selectEntities = (state: EcommerceStore) => state.entities;
export const selectSelectedEntity = (state: EcommerceStore) => state.selectedEntity;
export const selectWorkflows = (state: EcommerceStore) => state.workflows;
export const selectSelectedWorkflow = (state: EcommerceStore) => state.selectedWorkflow;
export const selectKnowledgeItems = (state: EcommerceStore) => state.knowledgeItems;
export const selectEdgeCases = (state: EcommerceStore) => state.edgeCases;
export const selectGeneratedData = (state: EcommerceStore) => state.generatedData;
export const selectIsGenerating = (state: EcommerceStore) => state.isGenerating;
export const selectHealthStatus = (state: EcommerceStore) => state.healthStatus;
export const selectError = (state: EcommerceStore) => state.error;
export const selectHistoryEntries = (state: EcommerceStore) => state.historyEntries;

export const selectEntitiesByCategory = (state: EcommerceStore) => {
  if (state.entityCategory === 'all') return state.entities;
  return state.entities.filter((e) => e.category === state.entityCategory);
};

export const selectEntityCategories = (state: EcommerceStore): EntityCategory[] => {
  const categories = new Set(state.entities.map((e) => e.category));
  return ['all', ...Array.from(categories)] as EntityCategory[];
};

export default useEcommerceStore;
