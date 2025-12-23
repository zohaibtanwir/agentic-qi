import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import {
  testDataClient,
  GenerationMethod,
  OutputFormat,
  type GenerateRequest,
  type GenerateResponse,
  type SchemaInfo,
  type Scenario,
} from '../grpc/testDataClient';

// ============= Types =============

export interface GeneratorFormState {
  domain: string;
  entity: string;
  count: number;
  outputFormat: OutputFormat;
  generationMethod: GenerationMethod;
  context: string;
  customSchema: string;
  useCache: boolean;
  productionLike: boolean;
  defectTriggering: boolean;
}

export interface ScenarioItem extends Scenario {
  id: string;
}

export type GeneratorTab = 'options' | 'scenarios' | 'schema' | 'output';
export type PreviewTab = 'json' | 'table' | 'stats';

export interface GenerationStats {
  totalGenerated: number;
  lastGenerationTime: number;
  averageCoherenceScore: number;
  llmTokensUsed: number;
}

export interface TestDataState {
  // Form state
  form: GeneratorFormState;

  // Scenarios
  scenarios: ScenarioItem[];

  // UI state
  activeGeneratorTab: GeneratorTab;
  activePreviewTab: PreviewTab;
  sidebarCollapsed: boolean;

  // Data
  schemas: SchemaInfo[];
  generatedData: string;
  lastResponse: GenerateResponse | null;
  generationStats: GenerationStats;

  // Loading states
  isGenerating: boolean;
  isLoadingSchemas: boolean;

  // Errors
  error: string | null;

  // History for undo
  history: string[];
}

export interface TestDataActions {
  // Form actions
  setFormField: <K extends keyof GeneratorFormState>(field: K, value: GeneratorFormState[K]) => void;
  resetForm: () => void;

  // Scenario actions
  addScenario: (scenario: Omit<ScenarioItem, 'id'>) => void;
  updateScenario: (id: string, updates: Partial<ScenarioItem>) => void;
  removeScenario: (id: string) => void;
  clearScenarios: () => void;

  // UI actions
  setActiveGeneratorTab: (tab: GeneratorTab) => void;
  setActivePreviewTab: (tab: PreviewTab) => void;
  toggleSidebar: () => void;

  // Data actions
  loadSchemas: (domain?: string) => Promise<void>;
  generateData: () => Promise<void>;
  clearGeneratedData: () => void;

  // Error actions
  clearError: () => void;
}

export type TestDataStore = TestDataState & TestDataActions;

// ============= Default Values =============

const defaultForm: GeneratorFormState = {
  domain: 'ecommerce',
  entity: 'cart',
  count: 10,
  outputFormat: OutputFormat.JSON,
  generationMethod: GenerationMethod.TRADITIONAL,
  context: '',
  customSchema: '',
  useCache: false,
  productionLike: false,
  defectTriggering: false,
};

const defaultStats: GenerationStats = {
  totalGenerated: 0,
  lastGenerationTime: 0,
  averageCoherenceScore: 0,
  llmTokensUsed: 0,
};

const initialState: TestDataState = {
  form: defaultForm,
  scenarios: [],
  activeGeneratorTab: 'options',
  activePreviewTab: 'json',
  sidebarCollapsed: false,
  schemas: [],
  generatedData: '',
  lastResponse: null,
  generationStats: defaultStats,
  isGenerating: false,
  isLoadingSchemas: false,
  error: null,
  history: [],
};

// ============= Store =============

export const useTestDataStore = create<TestDataStore>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        // Form actions
        setFormField: (field, value) => {
          set(
            (state) => ({
              form: { ...state.form, [field]: value },
              error: null,
            }),
            false,
            `setFormField:${field}`
          );
        },

        resetForm: () => {
          set({ form: defaultForm, scenarios: [], error: null }, false, 'resetForm');
        },

        // Scenario actions
        addScenario: (scenario) => {
          const id = `scenario-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
          set(
            (state) => ({
              scenarios: [...state.scenarios, { ...scenario, id }],
            }),
            false,
            'addScenario'
          );
        },

        updateScenario: (id, updates) => {
          set(
            (state) => ({
              scenarios: state.scenarios.map((s) =>
                s.id === id ? { ...s, ...updates } : s
              ),
            }),
            false,
            'updateScenario'
          );
        },

        removeScenario: (id) => {
          set(
            (state) => ({
              scenarios: state.scenarios.filter((s) => s.id !== id),
            }),
            false,
            'removeScenario'
          );
        },

        clearScenarios: () => {
          set({ scenarios: [] }, false, 'clearScenarios');
        },

        // UI actions
        setActiveGeneratorTab: (tab) => {
          set({ activeGeneratorTab: tab }, false, 'setActiveGeneratorTab');
        },

        setActivePreviewTab: (tab) => {
          set({ activePreviewTab: tab }, false, 'setActivePreviewTab');
        },

        toggleSidebar: () => {
          set(
            (state) => ({ sidebarCollapsed: !state.sidebarCollapsed }),
            false,
            'toggleSidebar'
          );
        },

        // Data actions
        loadSchemas: async (domain) => {
          set({ isLoadingSchemas: true, error: null }, false, 'loadSchemas:start');
          try {
            const response = await testDataClient.getSchemas(domain);
            set(
              { schemas: response.schemas, isLoadingSchemas: false },
              false,
              'loadSchemas:success'
            );
          } catch (err) {
            set(
              {
                error: err instanceof Error ? err.message : 'Failed to load schemas',
                isLoadingSchemas: false,
              },
              false,
              'loadSchemas:error'
            );
          }
        },

        generateData: async () => {
          const state = get();
          set({ isGenerating: true, error: null }, false, 'generateData:start');

          try {
            const request: GenerateRequest = {
              requestId: `REQ-${Date.now()}`,
              domain: state.form.domain,
              entity: state.form.entity,
              schema: undefined,
              constraints: undefined,
              scenarios: state.scenarios.map((s) => ({
                name: s.name,
                count: s.count,
                overrides: s.overrides,
                description: s.description,
              })),
              context: state.form.context,
              hints: [],
              outputFormat: state.form.outputFormat,
              count: state.form.count,
              useCache: state.form.useCache,
              learnFromHistory: false,
              defectTriggering: state.form.defectTriggering,
              productionLike: state.form.productionLike,
              inlineSchema: '',
              generationMethod: state.form.generationMethod,
              customSchema: state.form.customSchema,
            };

            const response = await testDataClient.generateData(request);

            if (response.success) {
              const newStats: GenerationStats = {
                totalGenerated: state.generationStats.totalGenerated + response.recordCount,
                lastGenerationTime: response.metadata?.generationTimeMs || 0,
                averageCoherenceScore: response.metadata?.coherenceScore || 0,
                llmTokensUsed: state.generationStats.llmTokensUsed + (response.metadata?.llmTokensUsed || 0),
              };

              set(
                {
                  generatedData: response.data,
                  lastResponse: response,
                  generationStats: newStats,
                  isGenerating: false,
                  history: state.generatedData
                    ? [...state.history.slice(-9), state.generatedData]
                    : state.history,
                },
                false,
                'generateData:success'
              );
            } else {
              set(
                {
                  error: response.error || 'Generation failed',
                  isGenerating: false,
                },
                false,
                'generateData:failed'
              );
            }
          } catch (err) {
            set(
              {
                error: err instanceof Error ? err.message : 'Failed to generate data',
                isGenerating: false,
              },
              false,
              'generateData:error'
            );
          }
        },

        clearGeneratedData: () => {
          set(
            { generatedData: '', lastResponse: null },
            false,
            'clearGeneratedData'
          );
        },

        // Error actions
        clearError: () => {
          set({ error: null }, false, 'clearError');
        },
      }),
      {
        name: 'test-data-store',
        partialize: (state) => ({
          form: state.form,
          sidebarCollapsed: state.sidebarCollapsed,
          generationStats: state.generationStats,
        }),
      }
    ),
    { name: 'TestDataStore' }
  )
);

// ============= Selectors =============

export const selectForm = (state: TestDataStore) => state.form;
export const selectScenarios = (state: TestDataStore) => state.scenarios;
export const selectSchemas = (state: TestDataStore) => state.schemas;
export const selectGeneratedData = (state: TestDataStore) => state.generatedData;
export const selectIsGenerating = (state: TestDataStore) => state.isGenerating;
export const selectError = (state: TestDataStore) => state.error;
export const selectStats = (state: TestDataStore) => state.generationStats;

export const selectEntitySchema = (state: TestDataStore) => {
  const { entity } = state.form;
  return state.schemas.find((s) => s.name === entity);
};

export const selectTotalScenarioCount = (state: TestDataStore) => {
  return state.scenarios.reduce((sum, s) => sum + s.count, 0);
};

export default useTestDataStore;
