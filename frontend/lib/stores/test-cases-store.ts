import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import {
  testCasesClient,
  type HistorySessionSummary,
  type HistorySession,
} from '../grpc/testCasesClient';
import {
  TestType,
  OutputFormat,
  CoverageLevel,
  type GenerateTestCasesRequest,
  type GenerateTestCasesResponse,
  type TestCase,
} from '../grpc/generated/test_cases';

// ============= Types =============

export interface TestCasesFormState {
  userStory: string;
  acceptanceCriteria: string[];
  domain: string;
  entity: string;
  workflow: string;
  testTypes: TestType[];
  coverageLevel: CoverageLevel;
  outputFormat: OutputFormat;
  maxTestCases: number;
  includeEdgeCases: boolean;
  includeNegativeTests: boolean;
  detailLevel: string;
}

export type GeneratorTab = 'input' | 'config' | 'output';
export type PreviewTab = 'list' | 'gherkin' | 'json';

export interface TestCasesState {
  // Form state
  form: TestCasesFormState;

  // UI state
  activeGeneratorTab: GeneratorTab;
  activePreviewTab: PreviewTab;
  sidebarCollapsed: boolean;

  // Data
  generatedTestCases: TestCase[];
  lastResponse: GenerateTestCasesResponse | null;

  // Loading states
  isGenerating: boolean;
  isLoadingHistory: boolean;
  isLoadingSession: boolean;

  // Errors
  error: string | null;

  // History
  historyEntries: HistorySessionSummary[];
  historyTotalCount: number;
  selectedSession: HistorySession | null;
}

export interface TestCasesActions {
  // Form actions
  setFormField: <K extends keyof TestCasesFormState>(field: K, value: TestCasesFormState[K]) => void;
  addAcceptanceCriterion: (criterion: string) => void;
  removeAcceptanceCriterion: (index: number) => void;
  updateAcceptanceCriterion: (index: number, value: string) => void;
  resetForm: () => void;

  // UI actions
  setActiveGeneratorTab: (tab: GeneratorTab) => void;
  setActivePreviewTab: (tab: PreviewTab) => void;
  toggleSidebar: () => void;

  // Generation actions
  generateTestCases: () => Promise<void>;
  clearGeneratedTestCases: () => void;

  // Error actions
  clearError: () => void;

  // History actions
  loadHistory: (limit?: number, offset?: number) => Promise<void>;
  loadHistorySession: (sessionId: string) => Promise<void>;
  deleteHistorySession: (sessionId: string) => Promise<void>;
  clearSelectedSession: () => void;
}

export type TestCasesStore = TestCasesState & TestCasesActions;

// ============= Default Values =============

const defaultForm: TestCasesFormState = {
  userStory: '',
  acceptanceCriteria: [''],
  domain: 'ecommerce',
  entity: '',
  workflow: '',
  testTypes: [TestType.FUNCTIONAL],
  coverageLevel: CoverageLevel.STANDARD,
  outputFormat: OutputFormat.TRADITIONAL,
  maxTestCases: 10,
  includeEdgeCases: true,
  includeNegativeTests: true,
  detailLevel: 'medium',
};

const initialState: TestCasesState = {
  form: defaultForm,
  activeGeneratorTab: 'input',
  activePreviewTab: 'list',
  sidebarCollapsed: false,
  generatedTestCases: [],
  lastResponse: null,
  isGenerating: false,
  isLoadingHistory: false,
  isLoadingSession: false,
  error: null,
  historyEntries: [],
  historyTotalCount: 0,
  selectedSession: null,
};

// ============= Store =============

export const useTestCasesStore = create<TestCasesStore>()(
  devtools(
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

      addAcceptanceCriterion: (criterion) => {
        set(
          (state) => ({
            form: {
              ...state.form,
              acceptanceCriteria: [...state.form.acceptanceCriteria, criterion],
            },
          }),
          false,
          'addAcceptanceCriterion'
        );
      },

      removeAcceptanceCriterion: (index) => {
        set(
          (state) => ({
            form: {
              ...state.form,
              acceptanceCriteria: state.form.acceptanceCriteria.filter((_, i) => i !== index),
            },
          }),
          false,
          'removeAcceptanceCriterion'
        );
      },

      updateAcceptanceCriterion: (index, value) => {
        set(
          (state) => ({
            form: {
              ...state.form,
              acceptanceCriteria: state.form.acceptanceCriteria.map((ac, i) =>
                i === index ? value : ac
              ),
            },
          }),
          false,
          'updateAcceptanceCriterion'
        );
      },

      resetForm: () => {
        set({ form: defaultForm, error: null }, false, 'resetForm');
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

      // Generation actions
      generateTestCases: async () => {
        const state = get();
        set({ isGenerating: true, error: null }, false, 'generateTestCases:start');

        try {
          const request: GenerateTestCasesRequest = {
            requestId: `REQ-${Date.now()}`,
            userStory: {
              story: state.form.userStory,
              acceptanceCriteria: state.form.acceptanceCriteria.filter(ac => ac.trim() !== ''),
              additionalContext: '',
            },
            domainConfig: {
              domain: state.form.domain,
              entity: state.form.entity,
              workflow: state.form.workflow,
              includeBusinessRules: true,
              includeEdgeCases: state.form.includeEdgeCases,
            },
            generationConfig: {
              outputFormat: state.form.outputFormat,
              coverageLevel: state.form.coverageLevel,
              testTypes: state.form.testTypes,
              llmProvider: 'anthropic',
              checkDuplicates: true,
              maxTestCases: state.form.maxTestCases,
              priorityFocus: '',
              count: state.form.maxTestCases,
              includeEdgeCases: state.form.includeEdgeCases,
              includeNegativeTests: state.form.includeNegativeTests,
              detailLevel: state.form.detailLevel,
            },
            testDataConfig: {
              generateTestData: false,
              placement: 0,
              samplesPerCase: 0,
            },
          };

          const response = await testCasesClient.generateTestCases(request);

          if (response.success) {
            set(
              {
                generatedTestCases: response.testCases || [],
                lastResponse: response,
                isGenerating: false,
                activeGeneratorTab: 'output',
              },
              false,
              'generateTestCases:success'
            );

            // Reload history to include the new session
            get().loadHistory();
          } else {
            set(
              {
                error: response.errorMessage || 'Generation failed',
                isGenerating: false,
              },
              false,
              'generateTestCases:failed'
            );
          }
        } catch (err) {
          set(
            {
              error: err instanceof Error ? err.message : 'Failed to generate test cases',
              isGenerating: false,
            },
            false,
            'generateTestCases:error'
          );
        }
      },

      clearGeneratedTestCases: () => {
        set(
          { generatedTestCases: [], lastResponse: null },
          false,
          'clearGeneratedTestCases'
        );
      },

      // Error actions
      clearError: () => {
        set({ error: null }, false, 'clearError');
      },

      // History actions
      loadHistory: async (limit = 20, offset = 0) => {
        set({ isLoadingHistory: true, error: null }, false, 'loadHistory:start');

        try {
          const response = await testCasesClient.listHistory({
            limit,
            offset,
            domain: '',
            status: '',
          });

          set(
            {
              historyEntries: response.sessions || [],
              historyTotalCount: response.totalCount,
              isLoadingHistory: false,
            },
            false,
            'loadHistory:success'
          );
        } catch (err) {
          set(
            {
              error: err instanceof Error ? err.message : 'Failed to load history',
              isLoadingHistory: false,
            },
            false,
            'loadHistory:error'
          );
        }
      },

      loadHistorySession: async (sessionId: string) => {
        set({ isLoadingSession: true, error: null }, false, 'loadHistorySession:start');

        try {
          const response = await testCasesClient.getHistorySession({ sessionId });

          if (response.found && response.session) {
            const session = response.session;

            // Update form with session data
            set(
              {
                form: {
                  ...get().form,
                  userStory: session.userStory,
                  acceptanceCriteria: session.acceptanceCriteria?.length
                    ? session.acceptanceCriteria
                    : [''],
                  domain: session.domain,
                },
                generatedTestCases: session.testCases || [],
                selectedSession: session,
                isLoadingSession: false,
                activeGeneratorTab: 'output',
              },
              false,
              'loadHistorySession:success'
            );
          } else {
            set(
              {
                error: 'Session not found',
                isLoadingSession: false,
              },
              false,
              'loadHistorySession:notFound'
            );
          }
        } catch (err) {
          set(
            {
              error: err instanceof Error ? err.message : 'Failed to load session',
              isLoadingSession: false,
            },
            false,
            'loadHistorySession:error'
          );
        }
      },

      deleteHistorySession: async (sessionId: string) => {
        try {
          const response = await testCasesClient.deleteHistorySession({ sessionId });

          if (response.success) {
            // Remove from local state
            set(
              (state) => ({
                historyEntries: state.historyEntries.filter(
                  (entry) => entry.sessionId !== sessionId
                ),
                historyTotalCount: state.historyTotalCount - 1,
                selectedSession:
                  state.selectedSession?.sessionId === sessionId
                    ? null
                    : state.selectedSession,
              }),
              false,
              'deleteHistorySession:success'
            );
          } else {
            set(
              { error: response.message || 'Failed to delete session' },
              false,
              'deleteHistorySession:failed'
            );
          }
        } catch (err) {
          set(
            {
              error: err instanceof Error ? err.message : 'Failed to delete session',
            },
            false,
            'deleteHistorySession:error'
          );
        }
      },

      clearSelectedSession: () => {
        set({ selectedSession: null }, false, 'clearSelectedSession');
      },
    }),
    { name: 'TestCasesStore' }
  )
);

// ============= Selectors =============

export const selectForm = (state: TestCasesStore) => state.form;
export const selectGeneratedTestCases = (state: TestCasesStore) => state.generatedTestCases;
export const selectIsGenerating = (state: TestCasesStore) => state.isGenerating;
export const selectError = (state: TestCasesStore) => state.error;
export const selectHistoryEntries = (state: TestCasesStore) => state.historyEntries;
export const selectHistoryTotalCount = (state: TestCasesStore) => state.historyTotalCount;
export const selectSelectedSession = (state: TestCasesStore) => state.selectedSession;
export const selectIsLoadingHistory = (state: TestCasesStore) => state.isLoadingHistory;
export const selectIsLoadingSession = (state: TestCasesStore) => state.isLoadingSession;
export const selectActiveGeneratorTab = (state: TestCasesStore) => state.activeGeneratorTab;
export const selectActivePreviewTab = (state: TestCasesStore) => state.activePreviewTab;
export const selectSidebarCollapsed = (state: TestCasesStore) => state.sidebarCollapsed;

export const selectTestCasesByType = (state: TestCasesStore) => {
  const testCases = state.generatedTestCases;
  return {
    functional: testCases.filter((tc) => tc.type === TestType.FUNCTIONAL),
    negative: testCases.filter((tc) => tc.type === TestType.NEGATIVE),
    boundary: testCases.filter((tc) => tc.type === TestType.BOUNDARY),
    edgeCase: testCases.filter((tc) => tc.type === TestType.EDGE_CASE),
    other: testCases.filter(
      (tc) =>
        tc.type !== TestType.FUNCTIONAL &&
        tc.type !== TestType.NEGATIVE &&
        tc.type !== TestType.BOUNDARY &&
        tc.type !== TestType.EDGE_CASE
    ),
  };
};

export const selectTestCaseStats = (state: TestCasesStore) => {
  const response = state.lastResponse;
  if (!response?.metadata) {
    return {
      totalCount: state.generatedTestCases.length,
      generationTimeMs: 0,
      tokensUsed: 0,
      coverage: null,
    };
  }

  return {
    totalCount: response.metadata.testCasesGenerated,
    generationTimeMs: response.metadata.generationTimeMs,
    tokensUsed: response.metadata.llmTokensUsed,
    coverage: response.metadata.coverage,
  };
};

export default useTestCasesStore;
