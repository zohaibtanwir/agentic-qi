import { act, renderHook } from '@testing-library/react';
import {
  useTestDataStore,
  selectForm,
  selectScenarios,
  selectEntitySchema,
  selectTotalScenarioCount,
  selectIsGenerating,
  selectError,
} from '../test-data-store';
import { GenerationMethod, OutputFormat } from '../../grpc/testDataClient';

// Mock the testDataClient
jest.mock('../../grpc/testDataClient', () => ({
  ...jest.requireActual('../../grpc/testDataClient'),
  testDataClient: {
    getSchemas: jest.fn(),
    generateData: jest.fn(),
  },
}));

import { testDataClient } from '../../grpc/testDataClient';

const mockGetSchemas = testDataClient.getSchemas as jest.Mock;
const mockGenerateData = testDataClient.generateData as jest.Mock;

describe('useTestDataStore', () => {
  beforeEach(() => {
    // Fully reset store state before each test
    useTestDataStore.setState({
      form: {
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
      },
      scenarios: [],
      activeGeneratorTab: 'options',
      activePreviewTab: 'json',
      sidebarCollapsed: false,
      schemas: [],
      generatedData: '',
      lastResponse: null,
      generationStats: {
        totalGenerated: 0,
        lastGenerationTime: 0,
        averageCoherenceScore: 0,
        llmTokensUsed: 0,
      },
      isGenerating: false,
      isLoadingSchemas: false,
      error: null,
      historyEntries: [],
    });
    jest.clearAllMocks();
  });

  describe('form actions', () => {
    it('should have default form values', () => {
      const { result } = renderHook(() => useTestDataStore());

      expect(result.current.form.domain).toBe('ecommerce');
      expect(result.current.form.entity).toBe('cart');
      expect(result.current.form.count).toBe(10);
      expect(result.current.form.outputFormat).toBe(OutputFormat.JSON);
      expect(result.current.form.generationMethod).toBe(GenerationMethod.TRADITIONAL);
    });

    it('should update form field', () => {
      const { result } = renderHook(() => useTestDataStore());

      act(() => {
        result.current.setFormField('entity', 'order');
      });

      expect(result.current.form.entity).toBe('order');
    });

    it('should update count field', () => {
      const { result } = renderHook(() => useTestDataStore());

      act(() => {
        result.current.setFormField('count', 25);
      });

      expect(result.current.form.count).toBe(25);
    });

    it('should update output format', () => {
      const { result } = renderHook(() => useTestDataStore());

      act(() => {
        result.current.setFormField('outputFormat', OutputFormat.CSV);
      });

      expect(result.current.form.outputFormat).toBe(OutputFormat.CSV);
    });

    it('should reset form to defaults', () => {
      const { result } = renderHook(() => useTestDataStore());

      act(() => {
        result.current.setFormField('entity', 'user');
        result.current.setFormField('count', 50);
        result.current.setFormField('context', 'test context');
      });

      expect(result.current.form.entity).toBe('user');

      act(() => {
        result.current.resetForm();
      });

      expect(result.current.form.entity).toBe('cart');
      expect(result.current.form.count).toBe(10);
      expect(result.current.form.context).toBe('');
    });

    it('should clear error when setting form field', () => {
      const { result } = renderHook(() => useTestDataStore());

      // Manually set error state
      act(() => {
        useTestDataStore.setState({ error: 'Test error' });
      });

      expect(result.current.error).toBe('Test error');

      act(() => {
        result.current.setFormField('count', 20);
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('scenario actions', () => {
    it('should add scenario', () => {
      const { result } = renderHook(() => useTestDataStore());

      act(() => {
        result.current.addScenario({
          name: 'happy_path',
          count: 5,
          overrides: {},
          description: 'Happy path scenario',
        });
      });

      expect(result.current.scenarios).toHaveLength(1);
      expect(result.current.scenarios[0].name).toBe('happy_path');
      expect(result.current.scenarios[0].count).toBe(5);
      expect(result.current.scenarios[0].id).toBeDefined();
    });

    it('should add multiple scenarios', () => {
      const { result } = renderHook(() => useTestDataStore());

      act(() => {
        result.current.addScenario({
          name: 'scenario_1',
          count: 3,
          overrides: {},
          description: '',
        });
        result.current.addScenario({
          name: 'scenario_2',
          count: 2,
          overrides: {},
          description: '',
        });
      });

      expect(result.current.scenarios).toHaveLength(2);
    });

    it('should update scenario', () => {
      const { result } = renderHook(() => useTestDataStore());

      act(() => {
        result.current.addScenario({
          name: 'original',
          count: 5,
          overrides: {},
          description: '',
        });
      });

      const scenarioId = result.current.scenarios[0].id;

      act(() => {
        result.current.updateScenario(scenarioId, { name: 'updated', count: 10 });
      });

      expect(result.current.scenarios[0].name).toBe('updated');
      expect(result.current.scenarios[0].count).toBe(10);
    });

    it('should remove scenario', () => {
      const { result } = renderHook(() => useTestDataStore());

      act(() => {
        result.current.addScenario({
          name: 'to_remove',
          count: 5,
          overrides: {},
          description: '',
        });
      });

      expect(result.current.scenarios).toHaveLength(1);
      const scenarioId = result.current.scenarios[0].id;

      act(() => {
        result.current.removeScenario(scenarioId);
      });

      expect(result.current.scenarios).toHaveLength(0);
    });

    it('should clear all scenarios', () => {
      const { result } = renderHook(() => useTestDataStore());

      act(() => {
        result.current.addScenario({ name: 's1', count: 1, overrides: {}, description: '' });
        result.current.addScenario({ name: 's2', count: 2, overrides: {}, description: '' });
        result.current.addScenario({ name: 's3', count: 3, overrides: {}, description: '' });
      });

      expect(result.current.scenarios).toHaveLength(3);

      act(() => {
        result.current.clearScenarios();
      });

      expect(result.current.scenarios).toHaveLength(0);
    });
  });

  describe('UI actions', () => {
    it('should set active generator tab', () => {
      const { result } = renderHook(() => useTestDataStore());

      expect(result.current.activeGeneratorTab).toBe('options');

      act(() => {
        result.current.setActiveGeneratorTab('scenarios');
      });

      expect(result.current.activeGeneratorTab).toBe('scenarios');
    });

    it('should set active preview tab', () => {
      const { result } = renderHook(() => useTestDataStore());

      expect(result.current.activePreviewTab).toBe('json');

      act(() => {
        result.current.setActivePreviewTab('table');
      });

      expect(result.current.activePreviewTab).toBe('table');
    });

    it('should toggle sidebar', () => {
      const { result } = renderHook(() => useTestDataStore());

      expect(result.current.sidebarCollapsed).toBe(false);

      act(() => {
        result.current.toggleSidebar();
      });

      expect(result.current.sidebarCollapsed).toBe(true);

      act(() => {
        result.current.toggleSidebar();
      });

      expect(result.current.sidebarCollapsed).toBe(false);
    });
  });

  describe('loadSchemas', () => {
    it('should load schemas successfully', async () => {
      const mockSchemas = [
        { name: 'cart', domain: 'ecommerce', description: 'Cart', fields: [] },
        { name: 'order', domain: 'ecommerce', description: 'Order', fields: [] },
      ];
      mockGetSchemas.mockResolvedValueOnce({ schemas: mockSchemas });

      const { result } = renderHook(() => useTestDataStore());

      expect(result.current.isLoadingSchemas).toBe(false);

      await act(async () => {
        await result.current.loadSchemas();
      });

      expect(result.current.schemas).toEqual(mockSchemas);
      expect(result.current.isLoadingSchemas).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('should handle schema loading error', async () => {
      mockGetSchemas.mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useTestDataStore());

      await act(async () => {
        await result.current.loadSchemas();
      });

      expect(result.current.schemas).toHaveLength(0);
      expect(result.current.error).toBe('Network error');
      expect(result.current.isLoadingSchemas).toBe(false);
    });

    it('should filter schemas by domain', async () => {
      mockGetSchemas.mockResolvedValueOnce({
        schemas: [{ name: 'cart', domain: 'ecommerce', description: '', fields: [] }],
      });

      const { result } = renderHook(() => useTestDataStore());

      await act(async () => {
        await result.current.loadSchemas('ecommerce');
      });

      expect(mockGetSchemas).toHaveBeenCalledWith('ecommerce');
    });
  });

  describe('generateData', () => {
    it('should generate data successfully', async () => {
      const mockResponse = {
        requestId: 'REQ-123',
        success: true,
        data: '[{"id": 1}]',
        recordCount: 1,
        metadata: {
          generationPath: 'traditional',
          generationTimeMs: 500,
          coherenceScore: 0.95,
          llmTokensUsed: 0,
          scenarioCounts: {},
        },
        error: '',
      };
      mockGenerateData.mockResolvedValueOnce(mockResponse);

      const { result } = renderHook(() => useTestDataStore());

      await act(async () => {
        await result.current.generateData();
      });

      expect(result.current.generatedData).toBe('[{"id": 1}]');
      expect(result.current.lastResponse).toEqual(mockResponse);
      expect(result.current.isGenerating).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.generationStats.totalGenerated).toBe(1);
    });

    it('should handle generation failure response', async () => {
      const mockResponse = {
        success: false,
        data: '',
        recordCount: 0,
        error: 'Generation failed',
      };
      mockGenerateData.mockResolvedValueOnce(mockResponse);

      const { result } = renderHook(() => useTestDataStore());

      await act(async () => {
        await result.current.generateData();
      });

      expect(result.current.generatedData).toBe('');
      expect(result.current.error).toBe('Generation failed');
      expect(result.current.isGenerating).toBe(false);
    });

    it('should handle generation error', async () => {
      mockGenerateData.mockRejectedValueOnce(new Error('API error'));

      const { result } = renderHook(() => useTestDataStore());

      await act(async () => {
        await result.current.generateData();
      });

      expect(result.current.error).toBe('API error');
      expect(result.current.isGenerating).toBe(false);
    });

    it('should update stats after successful generation', async () => {
      const mockResponse = {
        success: true,
        data: '[{"id": 1}]',
        recordCount: 10,
        metadata: {
          generationTimeMs: 1000,
          coherenceScore: 0.9,
          llmTokensUsed: 500,
        },
        error: '',
      };
      mockGenerateData.mockResolvedValueOnce(mockResponse);

      const { result } = renderHook(() => useTestDataStore());

      await act(async () => {
        await result.current.generateData();
      });

      expect(result.current.generationStats.totalGenerated).toBe(10);
      expect(result.current.generationStats.lastGenerationTime).toBe(1000);
      expect(result.current.generationStats.llmTokensUsed).toBe(500);
    });

    it('should include scenarios in request', async () => {
      mockGenerateData.mockResolvedValueOnce({
        success: true,
        data: '[]',
        recordCount: 0,
        error: '',
      });

      const { result } = renderHook(() => useTestDataStore());

      act(() => {
        result.current.addScenario({
          name: 'test_scenario',
          count: 5,
          overrides: { field: 'value' },
          description: 'Test',
        });
      });

      await act(async () => {
        await result.current.generateData();
      });

      expect(mockGenerateData).toHaveBeenCalledWith(
        expect.objectContaining({
          scenarios: [
            {
              name: 'test_scenario',
              count: 5,
              overrides: { field: 'value' },
              description: 'Test',
            },
          ],
        })
      );
    });
  });

  describe('clearGeneratedData', () => {
    it('should clear generated data', async () => {
      mockGenerateData.mockResolvedValueOnce({
        success: true,
        data: '[{"id": 1}]',
        recordCount: 1,
        error: '',
      });

      const { result } = renderHook(() => useTestDataStore());

      await act(async () => {
        await result.current.generateData();
      });

      expect(result.current.generatedData).not.toBe('');

      act(() => {
        result.current.clearGeneratedData();
      });

      expect(result.current.generatedData).toBe('');
      expect(result.current.lastResponse).toBeNull();
    });
  });

  describe('selectors', () => {
    it('selectForm should return form state', () => {
      const { result } = renderHook(() => useTestDataStore());

      act(() => {
        result.current.setFormField('entity', 'order');
      });

      expect(selectForm(result.current)).toEqual(
        expect.objectContaining({ entity: 'order' })
      );
    });

    it('selectScenarios should return scenarios', () => {
      const { result } = renderHook(() => useTestDataStore());

      act(() => {
        result.current.addScenario({ name: 's1', count: 5, overrides: {}, description: '' });
      });

      const scenarios = selectScenarios(result.current);
      expect(scenarios).toHaveLength(1);
      expect(scenarios[0].name).toBe('s1');
    });

    it('selectEntitySchema should return matching schema', async () => {
      const mockSchemas = [
        { name: 'cart', domain: 'ecommerce', description: 'Cart', fields: [] },
        { name: 'order', domain: 'ecommerce', description: 'Order', fields: [] },
      ];
      mockGetSchemas.mockResolvedValueOnce({ schemas: mockSchemas });

      const { result } = renderHook(() => useTestDataStore());

      await act(async () => {
        await result.current.loadSchemas();
      });

      const schema = selectEntitySchema(result.current);
      expect(schema?.name).toBe('cart');
    });

    it('selectTotalScenarioCount should sum scenario counts', () => {
      const { result } = renderHook(() => useTestDataStore());

      act(() => {
        result.current.addScenario({ name: 's1', count: 5, overrides: {}, description: '' });
        result.current.addScenario({ name: 's2', count: 3, overrides: {}, description: '' });
        result.current.addScenario({ name: 's3', count: 2, overrides: {}, description: '' });
      });

      expect(selectTotalScenarioCount(result.current)).toBe(10);
    });

    it('selectIsGenerating should return loading state', () => {
      const { result } = renderHook(() => useTestDataStore());

      expect(selectIsGenerating(result.current)).toBe(false);
    });

    it('selectError should return error state', () => {
      const { result } = renderHook(() => useTestDataStore());

      act(() => {
        useTestDataStore.setState({ error: 'Test error' });
      });

      expect(selectError(result.current)).toBe('Test error');
    });
  });

  describe('edge cases', () => {
    it('should handle generation with empty request id', async () => {
      mockGenerateData.mockResolvedValueOnce({
        success: true,
        data: '[]',
        recordCount: 0,
        requestId: '',
        error: '',
      });

      const { result } = renderHook(() => useTestDataStore());

      await act(async () => {
        await result.current.generateData();
      });

      expect(result.current.isGenerating).toBe(false);
    });

    it('should handle non-Error exception in loadSchemas', async () => {
      mockGetSchemas.mockRejectedValueOnce('string error');

      const { result } = renderHook(() => useTestDataStore());

      await act(async () => {
        await result.current.loadSchemas();
      });

      expect(result.current.error).toBe('Failed to load schemas');
    });

    it('should handle non-Error exception in generateData', async () => {
      mockGenerateData.mockRejectedValueOnce('string error');

      const { result } = renderHook(() => useTestDataStore());

      await act(async () => {
        await result.current.generateData();
      });

      expect(result.current.error).toBe('Failed to generate data');
    });

    it('should handle success response without metadata', async () => {
      mockGenerateData.mockResolvedValueOnce({
        success: true,
        data: '[{"id": 1}]',
        recordCount: 1,
        error: '',
        // No metadata
      });

      const { result } = renderHook(() => useTestDataStore());

      await act(async () => {
        await result.current.generateData();
      });

      expect(result.current.generationStats.lastGenerationTime).toBe(0);
    });

    it('should keep history limited to 20 items', async () => {
      const { result } = renderHook(() => useTestDataStore());

      // Generate 22 times to exceed history limit
      for (let i = 0; i < 22; i++) {
        mockGenerateData.mockResolvedValueOnce({
          success: true,
          data: `[{"iteration": ${i}}]`,
          recordCount: 1,
          metadata: {
            generationPath: 'traditional',
            generationTimeMs: 100,
            coherenceScore: 0.5,
            llmTokensUsed: 0,
            scenarioCounts: {},
          },
          error: '',
        });

        await act(async () => {
          await result.current.generateData();
        });
      }

      // History should be limited to 20 items
      expect(result.current.historyEntries.length).toBeLessThanOrEqual(20);
    });

    it('should not update scenario that does not exist', () => {
      const { result } = renderHook(() => useTestDataStore());

      act(() => {
        result.current.updateScenario('non-existent-id', { count: 10 });
      });

      expect(result.current.scenarios).toHaveLength(0);
    });
  });
});
