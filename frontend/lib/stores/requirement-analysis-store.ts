import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import {
  requirementAnalysisClient,
  type AnalyzeRequest,
  type AnalyzeResponse,
  type QualityScore,
  type Gap,
  type ClarifyingQuestion,
  type GeneratedAC,
  type ExtractedRequirement,
} from '../grpc/requirementAnalysisClient';

// ============= Types =============

export type InputType = 'jira' | 'freeform' | 'transcript';

export interface JiraFormState {
  key: string;
  summary: string;
  description: string;
  acceptanceCriteria: string[];
  storyPoints: number;
  labels: string[];
  components: string[];
  priority: string;
}

export interface FreeFormFormState {
  title: string;
  text: string;
  context: string;
}

export interface TranscriptFormState {
  meetingTitle: string;
  meetingDate: string;
  transcript: string;
  participants: string[];
}

export interface AnalysisConfigState {
  includeDomainValidation: boolean;
  generateAcceptanceCriteria: boolean;
  generateQuestions: boolean;
  domain: string;
}

export type GeneratorTab = 'input' | 'results' | 'refine';

export interface AnsweredQuestion {
  questionId: string;
  answer: string;
}

export interface RequirementAnalysisState {
  // Input type
  inputType: InputType;

  // Form states
  jiraForm: JiraFormState;
  freeFormForm: FreeFormFormState;
  transcriptForm: TranscriptFormState;
  analysisConfig: AnalysisConfigState;

  // UI state
  activeTab: GeneratorTab;
  sidebarCollapsed: boolean;

  // Analysis results
  analysisResult: AnalyzeResponse | null;
  qualityScore: QualityScore | null;
  gaps: Gap[];
  questions: ClarifyingQuestion[];
  generatedACs: GeneratedAC[];
  extractedRequirement: ExtractedRequirement | null;

  // Refinement state
  answeredQuestions: AnsweredQuestion[];
  acceptedACs: string[];
  updatedTitle: string;
  updatedDescription: string;
  updatedACs: string[];

  // Loading states
  isAnalyzing: boolean;
  isReanalyzing: boolean;
  isExporting: boolean;

  // Errors
  error: string | null;
}

export interface RequirementAnalysisActions {
  // Input type actions
  setInputType: (type: InputType) => void;

  // Jira form actions
  setJiraField: <K extends keyof JiraFormState>(field: K, value: JiraFormState[K]) => void;
  addJiraAC: (criterion: string) => void;
  removeJiraAC: (index: number) => void;
  updateJiraAC: (index: number, value: string) => void;

  // FreeForm actions
  setFreeFormField: <K extends keyof FreeFormFormState>(field: K, value: FreeFormFormState[K]) => void;

  // Transcript actions
  setTranscriptField: <K extends keyof TranscriptFormState>(field: K, value: TranscriptFormState[K]) => void;
  addParticipant: (participant: string) => void;
  removeParticipant: (index: number) => void;

  // Config actions
  setConfigField: <K extends keyof AnalysisConfigState>(field: K, value: AnalysisConfigState[K]) => void;

  // UI actions
  setActiveTab: (tab: GeneratorTab) => void;
  toggleSidebar: () => void;

  // Analysis actions
  analyzeRequirement: () => Promise<void>;
  reanalyzeRequirement: () => Promise<void>;
  exportAnalysis: (format: 'json' | 'text') => Promise<string | null>;
  clearAnalysis: () => void;

  // Refinement actions
  answerQuestion: (questionId: string, answer: string) => void;
  toggleACAcceptance: (acId: string) => void;
  setUpdatedTitle: (title: string) => void;
  setUpdatedDescription: (description: string) => void;
  addUpdatedAC: (ac: string) => void;
  removeUpdatedAC: (index: number) => void;
  updateUpdatedAC: (index: number, value: string) => void;

  // Reset actions
  resetForm: () => void;
  clearError: () => void;
}

export type RequirementAnalysisStore = RequirementAnalysisState & RequirementAnalysisActions;

// ============= Default Values =============

const defaultJiraForm: JiraFormState = {
  key: '',
  summary: '',
  description: '',
  acceptanceCriteria: [''],
  storyPoints: 0,
  labels: [],
  components: [],
  priority: 'Medium',
};

const defaultFreeFormForm: FreeFormFormState = {
  title: '',
  text: '',
  context: '',
};

const defaultTranscriptForm: TranscriptFormState = {
  meetingTitle: '',
  meetingDate: '',
  transcript: '',
  participants: [],
};

const defaultAnalysisConfig: AnalysisConfigState = {
  includeDomainValidation: true,
  generateAcceptanceCriteria: true,
  generateQuestions: true,
  domain: 'ecommerce',
};

const initialState: RequirementAnalysisState = {
  inputType: 'freeform',
  jiraForm: defaultJiraForm,
  freeFormForm: defaultFreeFormForm,
  transcriptForm: defaultTranscriptForm,
  analysisConfig: defaultAnalysisConfig,
  activeTab: 'input',
  sidebarCollapsed: false,
  analysisResult: null,
  qualityScore: null,
  gaps: [],
  questions: [],
  generatedACs: [],
  extractedRequirement: null,
  answeredQuestions: [],
  acceptedACs: [],
  updatedTitle: '',
  updatedDescription: '',
  updatedACs: [],
  isAnalyzing: false,
  isReanalyzing: false,
  isExporting: false,
  error: null,
};

// ============= Store =============

export const useRequirementAnalysisStore = create<RequirementAnalysisStore>()(
  devtools(
    (set, get) => ({
      ...initialState,

      // Input type actions
      setInputType: (type) => {
        set({ inputType: type, error: null }, false, 'setInputType');
      },

      // Jira form actions
      setJiraField: (field, value) => {
        set(
          (state) => ({
            jiraForm: { ...state.jiraForm, [field]: value },
            error: null,
          }),
          false,
          `setJiraField:${field}`
        );
      },

      addJiraAC: (criterion) => {
        set(
          (state) => ({
            jiraForm: {
              ...state.jiraForm,
              acceptanceCriteria: [...state.jiraForm.acceptanceCriteria, criterion],
            },
          }),
          false,
          'addJiraAC'
        );
      },

      removeJiraAC: (index) => {
        set(
          (state) => ({
            jiraForm: {
              ...state.jiraForm,
              acceptanceCriteria: state.jiraForm.acceptanceCriteria.filter((_, i) => i !== index),
            },
          }),
          false,
          'removeJiraAC'
        );
      },

      updateJiraAC: (index, value) => {
        set(
          (state) => ({
            jiraForm: {
              ...state.jiraForm,
              acceptanceCriteria: state.jiraForm.acceptanceCriteria.map((ac, i) =>
                i === index ? value : ac
              ),
            },
          }),
          false,
          'updateJiraAC'
        );
      },

      // FreeForm actions
      setFreeFormField: (field, value) => {
        set(
          (state) => ({
            freeFormForm: { ...state.freeFormForm, [field]: value },
            error: null,
          }),
          false,
          `setFreeFormField:${field}`
        );
      },

      // Transcript actions
      setTranscriptField: (field, value) => {
        set(
          (state) => ({
            transcriptForm: { ...state.transcriptForm, [field]: value },
            error: null,
          }),
          false,
          `setTranscriptField:${field}`
        );
      },

      addParticipant: (participant) => {
        set(
          (state) => ({
            transcriptForm: {
              ...state.transcriptForm,
              participants: [...state.transcriptForm.participants, participant],
            },
          }),
          false,
          'addParticipant'
        );
      },

      removeParticipant: (index) => {
        set(
          (state) => ({
            transcriptForm: {
              ...state.transcriptForm,
              participants: state.transcriptForm.participants.filter((_, i) => i !== index),
            },
          }),
          false,
          'removeParticipant'
        );
      },

      // Config actions
      setConfigField: (field, value) => {
        set(
          (state) => ({
            analysisConfig: { ...state.analysisConfig, [field]: value },
          }),
          false,
          `setConfigField:${field}`
        );
      },

      // UI actions
      setActiveTab: (tab) => {
        set({ activeTab: tab }, false, 'setActiveTab');
      },

      toggleSidebar: () => {
        set(
          (state) => ({ sidebarCollapsed: !state.sidebarCollapsed }),
          false,
          'toggleSidebar'
        );
      },

      // Analysis actions
      analyzeRequirement: async () => {
        const state = get();
        set({ isAnalyzing: true, error: null }, false, 'analyzeRequirement:start');

        try {
          const config = state.analysisConfig;
          const request: AnalyzeRequest = {
            requestId: `REQ-${Date.now()}`,
            config: {
              includeDomainValidation: config.includeDomainValidation,
              generateAcceptanceCriteria: config.generateAcceptanceCriteria,
              generateQuestions: config.generateQuestions,
              llmProvider: 'anthropic',
              domain: config.domain,
            },
          };

          // Set input based on type
          if (state.inputType === 'jira') {
            request.jiraStory = {
              key: state.jiraForm.key,
              summary: state.jiraForm.summary,
              description: state.jiraForm.description,
              acceptanceCriteria: state.jiraForm.acceptanceCriteria.filter(ac => ac.trim() !== ''),
              storyPoints: state.jiraForm.storyPoints,
              labels: state.jiraForm.labels,
              components: state.jiraForm.components,
              priority: state.jiraForm.priority,
              reporter: '',
              assignee: '',
              rawJson: '',
            };
          } else if (state.inputType === 'freeform') {
            request.freeForm = {
              title: state.freeFormForm.title,
              text: state.freeFormForm.text,
              context: state.freeFormForm.context,
            };
          } else {
            request.transcript = {
              transcript: state.transcriptForm.transcript,
              meetingTitle: state.transcriptForm.meetingTitle,
              meetingDate: state.transcriptForm.meetingDate,
              participants: state.transcriptForm.participants,
            };
          }

          const response = await requirementAnalysisClient.analyzeRequirement(request);

          if (response.success) {
            set(
              {
                analysisResult: response,
                qualityScore: response.qualityScore || null,
                gaps: response.gaps || [],
                questions: response.questions || [],
                generatedACs: response.generatedAcs || [],
                extractedRequirement: response.extractedRequirement || null,
                updatedTitle: response.extractedRequirement?.title || '',
                updatedDescription: response.extractedRequirement?.description || '',
                updatedACs: response.extractedRequirement?.originalAcs || [],
                isAnalyzing: false,
                activeTab: 'results',
              },
              false,
              'analyzeRequirement:success'
            );
          } else {
            set(
              {
                error: response.error || 'Analysis failed',
                isAnalyzing: false,
              },
              false,
              'analyzeRequirement:failed'
            );
          }
        } catch (err) {
          set(
            {
              error: err instanceof Error ? err.message : 'Failed to analyze requirement',
              isAnalyzing: false,
            },
            false,
            'analyzeRequirement:error'
          );
        }
      },

      reanalyzeRequirement: async () => {
        const state = get();
        if (!state.analysisResult) return;

        set({ isReanalyzing: true, error: null }, false, 'reanalyzeRequirement:start');

        try {
          const response = await requirementAnalysisClient.reanalyzeRequirement({
            requestId: `REANA-${Date.now()}`,
            originalRequestId: state.analysisResult.requestId,
            updatedTitle: state.updatedTitle,
            updatedDescription: state.updatedDescription,
            updatedAcs: state.updatedACs,
            answeredQuestions: state.answeredQuestions.map(aq => ({
              questionId: aq.questionId,
              answer: aq.answer,
            })),
            acDecisions: state.generatedACs.map(ac => ({
              acId: ac.id,
              accepted: state.acceptedACs.includes(ac.id),
              modifiedText: '',
            })),
            additionalContext: '',
            config: {
              includeDomainValidation: state.analysisConfig.includeDomainValidation,
              generateAcceptanceCriteria: state.analysisConfig.generateAcceptanceCriteria,
              generateQuestions: state.analysisConfig.generateQuestions,
              llmProvider: 'anthropic',
              domain: state.analysisConfig.domain,
            },
          });

          if (response.success) {
            set(
              {
                analysisResult: response,
                qualityScore: response.qualityScore || null,
                gaps: response.gaps || [],
                questions: response.questions || [],
                generatedACs: response.generatedAcs || [],
                extractedRequirement: response.extractedRequirement || null,
                isReanalyzing: false,
                activeTab: 'results',
              },
              false,
              'reanalyzeRequirement:success'
            );
          } else {
            set(
              {
                error: response.error || 'Reanalysis failed',
                isReanalyzing: false,
              },
              false,
              'reanalyzeRequirement:failed'
            );
          }
        } catch (err) {
          set(
            {
              error: err instanceof Error ? err.message : 'Failed to reanalyze requirement',
              isReanalyzing: false,
            },
            false,
            'reanalyzeRequirement:error'
          );
        }
      },

      exportAnalysis: async (format) => {
        const state = get();
        if (!state.analysisResult) return null;

        set({ isExporting: true, error: null }, false, 'exportAnalysis:start');

        try {
          const response = await requirementAnalysisClient.exportAnalysis({
            requestId: `EXP-${Date.now()}`,
            analysisRequestId: state.analysisResult.requestId,
            format,
            includeRecommendations: true,
            includeGeneratedAcs: true,
          });

          set({ isExporting: false }, false, 'exportAnalysis:complete');

          if (response.success) {
            return response.content;
          } else {
            set({ error: response.error || 'Export failed' }, false, 'exportAnalysis:failed');
            return null;
          }
        } catch (err) {
          set(
            {
              error: err instanceof Error ? err.message : 'Failed to export analysis',
              isExporting: false,
            },
            false,
            'exportAnalysis:error'
          );
          return null;
        }
      },

      clearAnalysis: () => {
        set(
          {
            analysisResult: null,
            qualityScore: null,
            gaps: [],
            questions: [],
            generatedACs: [],
            extractedRequirement: null,
            answeredQuestions: [],
            acceptedACs: [],
            updatedTitle: '',
            updatedDescription: '',
            updatedACs: [],
            activeTab: 'input',
          },
          false,
          'clearAnalysis'
        );
      },

      // Refinement actions
      answerQuestion: (questionId, answer) => {
        set(
          (state) => {
            const existing = state.answeredQuestions.find(aq => aq.questionId === questionId);
            if (existing) {
              return {
                answeredQuestions: state.answeredQuestions.map(aq =>
                  aq.questionId === questionId ? { ...aq, answer } : aq
                ),
              };
            }
            return {
              answeredQuestions: [...state.answeredQuestions, { questionId, answer }],
            };
          },
          false,
          'answerQuestion'
        );
      },

      toggleACAcceptance: (acId) => {
        set(
          (state) => {
            if (state.acceptedACs.includes(acId)) {
              return { acceptedACs: state.acceptedACs.filter(id => id !== acId) };
            }
            return { acceptedACs: [...state.acceptedACs, acId] };
          },
          false,
          'toggleACAcceptance'
        );
      },

      setUpdatedTitle: (title) => {
        set({ updatedTitle: title }, false, 'setUpdatedTitle');
      },

      setUpdatedDescription: (description) => {
        set({ updatedDescription: description }, false, 'setUpdatedDescription');
      },

      addUpdatedAC: (ac) => {
        set(
          (state) => ({ updatedACs: [...state.updatedACs, ac] }),
          false,
          'addUpdatedAC'
        );
      },

      removeUpdatedAC: (index) => {
        set(
          (state) => ({ updatedACs: state.updatedACs.filter((_, i) => i !== index) }),
          false,
          'removeUpdatedAC'
        );
      },

      updateUpdatedAC: (index, value) => {
        set(
          (state) => ({
            updatedACs: state.updatedACs.map((ac, i) => (i === index ? value : ac)),
          }),
          false,
          'updateUpdatedAC'
        );
      },

      // Reset actions
      resetForm: () => {
        set(
          {
            jiraForm: defaultJiraForm,
            freeFormForm: defaultFreeFormForm,
            transcriptForm: defaultTranscriptForm,
            error: null,
          },
          false,
          'resetForm'
        );
      },

      clearError: () => {
        set({ error: null }, false, 'clearError');
      },
    }),
    { name: 'RequirementAnalysisStore' }
  )
);

// ============= Selectors =============

export const selectInputType = (state: RequirementAnalysisStore) => state.inputType;
export const selectJiraForm = (state: RequirementAnalysisStore) => state.jiraForm;
export const selectFreeFormForm = (state: RequirementAnalysisStore) => state.freeFormForm;
export const selectTranscriptForm = (state: RequirementAnalysisStore) => state.transcriptForm;
export const selectAnalysisConfig = (state: RequirementAnalysisStore) => state.analysisConfig;
export const selectActiveTab = (state: RequirementAnalysisStore) => state.activeTab;
export const selectAnalysisResult = (state: RequirementAnalysisStore) => state.analysisResult;
export const selectQualityScore = (state: RequirementAnalysisStore) => state.qualityScore;
export const selectGaps = (state: RequirementAnalysisStore) => state.gaps;
export const selectQuestions = (state: RequirementAnalysisStore) => state.questions;
export const selectGeneratedACs = (state: RequirementAnalysisStore) => state.generatedACs;
export const selectIsAnalyzing = (state: RequirementAnalysisStore) => state.isAnalyzing;
export const selectError = (state: RequirementAnalysisStore) => state.error;

export const selectGapsByType = (state: RequirementAnalysisStore) => {
  const gaps = state.gaps;
  return {
    high: gaps.filter(g => g.severity === 'high'),
    medium: gaps.filter(g => g.severity === 'medium'),
    low: gaps.filter(g => g.severity === 'low'),
  };
};

export const selectQualityStats = (state: RequirementAnalysisStore) => {
  const result = state.analysisResult;
  if (!result) return null;

  return {
    overallScore: result.qualityScore?.overallScore || 0,
    overallGrade: result.qualityScore?.overallGrade || 'N/A',
    gapsCount: result.gaps?.length || 0,
    questionsCount: result.questions?.length || 0,
    generatedACsCount: result.generatedAcs?.length || 0,
    readyForTestGeneration: result.readyForTestGeneration,
    blockers: result.blockers || [],
  };
};

export default useRequirementAnalysisStore;
