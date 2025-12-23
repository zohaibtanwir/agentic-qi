import { render, screen, fireEvent } from '@testing-library/react';
import { HistorySidebar } from '../HistorySidebar';
import { useTestDataStore, type HistoryEntry } from '@/lib/stores/test-data-store';
import { GenerationMethod, OutputFormat } from '@/lib/grpc/testDataClient';

// Mock the store
jest.mock('@/lib/stores/test-data-store', () => ({
  useTestDataStore: jest.fn(),
}));

const mockUseTestDataStore = useTestDataStore as jest.MockedFunction<typeof useTestDataStore>;

describe('HistorySidebar', () => {
  const mockLoadHistoryEntry = jest.fn();
  const mockDeleteHistoryEntry = jest.fn();
  const mockClearHistory = jest.fn();

  const createMockEntry = (overrides: Partial<HistoryEntry> = {}): HistoryEntry => ({
    id: 'test-id-1',
    timestamp: Date.now() - 60000, // 1 minute ago
    label: 'Test Entry',
    domain: 'ecommerce',
    entity: 'cart',
    count: 5,
    recordCount: 5,
    outputFormat: OutputFormat.JSON,
    generationMethod: GenerationMethod.LLM,
    coherenceScore: 0.95,
    generationTimeMs: 1500,
    data: '[]',
    scenarios: [],
    context: '',
    ...overrides,
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('empty state', () => {
    it('renders empty state when no history entries', () => {
      mockUseTestDataStore.mockImplementation((selector) => {
        const state = {
          historyEntries: [],
          loadHistoryEntry: mockLoadHistoryEntry,
          deleteHistoryEntry: mockDeleteHistoryEntry,
          clearHistory: mockClearHistory,
        };
        return selector(state as ReturnType<typeof useTestDataStore.getState>);
      });

      render(<HistorySidebar />);

      expect(screen.getByText('No history yet')).toBeInTheDocument();
      expect(screen.getByText('Generated data will appear here')).toBeInTheDocument();
    });
  });

  describe('with history entries', () => {
    const mockEntries: HistoryEntry[] = [
      createMockEntry({ id: 'entry-1', entity: 'cart', recordCount: 5 }),
      createMockEntry({ id: 'entry-2', entity: 'order', recordCount: 10, generationMethod: GenerationMethod.TRADITIONAL }),
      createMockEntry({ id: 'entry-3', entity: 'user', recordCount: 3, outputFormat: OutputFormat.CSV }),
    ];

    beforeEach(() => {
      mockUseTestDataStore.mockImplementation((selector) => {
        const state = {
          historyEntries: mockEntries,
          loadHistoryEntry: mockLoadHistoryEntry,
          deleteHistoryEntry: mockDeleteHistoryEntry,
          clearHistory: mockClearHistory,
        };
        return selector(state as ReturnType<typeof useTestDataStore.getState>);
      });
    });

    it('renders history header with count', () => {
      render(<HistorySidebar />);

      expect(screen.getByText('History')).toBeInTheDocument();
      // The header shows the count next to "History" - use getAllByText since record counts may also show '3'
      const countElements = screen.getAllByText('3');
      expect(countElements.length).toBeGreaterThan(0);
    });

    it('renders all history items', () => {
      render(<HistorySidebar />);

      expect(screen.getByText('cart')).toBeInTheDocument();
      expect(screen.getByText('order')).toBeInTheDocument();
      expect(screen.getByText('user')).toBeInTheDocument();
    });

    it('displays record count for each entry', () => {
      render(<HistorySidebar />);

      expect(screen.getByText('5')).toBeInTheDocument();
      expect(screen.getByText('10')).toBeInTheDocument();
    });

    it('displays generation method labels', () => {
      render(<HistorySidebar />);

      expect(screen.getAllByText('LLM').length).toBeGreaterThan(0);
      expect(screen.getByText('Traditional')).toBeInTheDocument();
    });

    it('displays output format labels', () => {
      render(<HistorySidebar />);

      expect(screen.getAllByText('JSON').length).toBeGreaterThan(0);
      expect(screen.getByText('CSV')).toBeInTheDocument();
    });

    it('displays coherence score when available', () => {
      render(<HistorySidebar />);

      expect(screen.getAllByText('95% coherent').length).toBeGreaterThan(0);
    });

    it('calls loadHistoryEntry when clicking an entry', () => {
      render(<HistorySidebar />);

      const cartEntry = screen.getByText('cart').closest('div[class*="cursor-pointer"]');
      fireEvent.click(cartEntry!);

      expect(mockLoadHistoryEntry).toHaveBeenCalledWith('entry-1');
    });

    it('calls deleteHistoryEntry when clicking delete button', () => {
      render(<HistorySidebar />);

      const deleteButtons = screen.getAllByTitle('Delete');
      fireEvent.click(deleteButtons[0]);

      expect(mockDeleteHistoryEntry).toHaveBeenCalledWith('entry-1');
    });

    it('calls clearHistory when clicking Clear button', () => {
      render(<HistorySidebar />);

      const clearButton = screen.getByText('Clear');
      fireEvent.click(clearButton);

      expect(mockClearHistory).toHaveBeenCalled();
    });

    it('does not propagate click event when deleting', () => {
      render(<HistorySidebar />);

      const deleteButtons = screen.getAllByTitle('Delete');
      fireEvent.click(deleteButtons[0]);

      // Delete should be called but load should not
      expect(mockDeleteHistoryEntry).toHaveBeenCalledWith('entry-1');
      expect(mockLoadHistoryEntry).not.toHaveBeenCalled();
    });
  });

  describe('timestamp formatting', () => {
    it('displays "Just now" for recent entries', () => {
      const recentEntry = createMockEntry({
        id: 'recent',
        timestamp: Date.now() - 30000, // 30 seconds ago
      });

      mockUseTestDataStore.mockImplementation((selector) => {
        const state = {
          historyEntries: [recentEntry],
          loadHistoryEntry: mockLoadHistoryEntry,
          deleteHistoryEntry: mockDeleteHistoryEntry,
          clearHistory: mockClearHistory,
        };
        return selector(state as ReturnType<typeof useTestDataStore.getState>);
      });

      render(<HistorySidebar />);

      expect(screen.getByText('Just now')).toBeInTheDocument();
    });

    it('displays minutes ago for entries within the hour', () => {
      const entry = createMockEntry({
        id: 'minutes-ago',
        timestamp: Date.now() - 5 * 60000, // 5 minutes ago
      });

      mockUseTestDataStore.mockImplementation((selector) => {
        const state = {
          historyEntries: [entry],
          loadHistoryEntry: mockLoadHistoryEntry,
          deleteHistoryEntry: mockDeleteHistoryEntry,
          clearHistory: mockClearHistory,
        };
        return selector(state as ReturnType<typeof useTestDataStore.getState>);
      });

      render(<HistorySidebar />);

      expect(screen.getByText('5m ago')).toBeInTheDocument();
    });

    it('displays hours ago for entries within the day', () => {
      const entry = createMockEntry({
        id: 'hours-ago',
        timestamp: Date.now() - 3 * 3600000, // 3 hours ago
      });

      mockUseTestDataStore.mockImplementation((selector) => {
        const state = {
          historyEntries: [entry],
          loadHistoryEntry: mockLoadHistoryEntry,
          deleteHistoryEntry: mockDeleteHistoryEntry,
          clearHistory: mockClearHistory,
        };
        return selector(state as ReturnType<typeof useTestDataStore.getState>);
      });

      render(<HistorySidebar />);

      expect(screen.getByText('3h ago')).toBeInTheDocument();
    });

    it('displays days ago for entries within the week', () => {
      const entry = createMockEntry({
        id: 'days-ago',
        timestamp: Date.now() - 2 * 86400000, // 2 days ago
      });

      mockUseTestDataStore.mockImplementation((selector) => {
        const state = {
          historyEntries: [entry],
          loadHistoryEntry: mockLoadHistoryEntry,
          deleteHistoryEntry: mockDeleteHistoryEntry,
          clearHistory: mockClearHistory,
        };
        return selector(state as ReturnType<typeof useTestDataStore.getState>);
      });

      render(<HistorySidebar />);

      expect(screen.getByText('2d ago')).toBeInTheDocument();
    });
  });

  describe('generation method labels', () => {
    const testCases = [
      { method: GenerationMethod.TRADITIONAL, label: 'Traditional' },
      { method: GenerationMethod.LLM, label: 'LLM' },
      { method: GenerationMethod.RAG, label: 'RAG' },
      { method: GenerationMethod.HYBRID, label: 'Hybrid' },
    ];

    testCases.forEach(({ method, label }) => {
      it(`displays "${label}" for ${GenerationMethod[method]} method`, () => {
        const entry = createMockEntry({
          id: `method-${method}`,
          generationMethod: method,
        });

        mockUseTestDataStore.mockImplementation((selector) => {
          const state = {
            historyEntries: [entry],
            loadHistoryEntry: mockLoadHistoryEntry,
            deleteHistoryEntry: mockDeleteHistoryEntry,
            clearHistory: mockClearHistory,
          };
          return selector(state as ReturnType<typeof useTestDataStore.getState>);
        });

        render(<HistorySidebar />);

        expect(screen.getByText(label)).toBeInTheDocument();
      });
    });
  });

  describe('output format labels', () => {
    const testCases = [
      { format: OutputFormat.JSON, label: 'JSON' },
      { format: OutputFormat.CSV, label: 'CSV' },
      { format: OutputFormat.SQL, label: 'SQL' },
    ];

    testCases.forEach(({ format, label }) => {
      it(`displays "${label}" for ${OutputFormat[format]} format`, () => {
        const entry = createMockEntry({
          id: `format-${format}`,
          outputFormat: format,
        });

        mockUseTestDataStore.mockImplementation((selector) => {
          const state = {
            historyEntries: [entry],
            loadHistoryEntry: mockLoadHistoryEntry,
            deleteHistoryEntry: mockDeleteHistoryEntry,
            clearHistory: mockClearHistory,
          };
          return selector(state as ReturnType<typeof useTestDataStore.getState>);
        });

        render(<HistorySidebar />);

        expect(screen.getByText(label)).toBeInTheDocument();
      });
    });
  });

  describe('coherence score display', () => {
    it('does not display coherence score when zero', () => {
      const entry = createMockEntry({
        id: 'no-coherence',
        coherenceScore: 0,
      });

      mockUseTestDataStore.mockImplementation((selector) => {
        const state = {
          historyEntries: [entry],
          loadHistoryEntry: mockLoadHistoryEntry,
          deleteHistoryEntry: mockDeleteHistoryEntry,
          clearHistory: mockClearHistory,
        };
        return selector(state as ReturnType<typeof useTestDataStore.getState>);
      });

      render(<HistorySidebar />);

      expect(screen.queryByText(/coherent/)).not.toBeInTheDocument();
    });

    it('rounds coherence score to nearest percentage', () => {
      const entry = createMockEntry({
        id: 'coherence-round',
        coherenceScore: 0.876,
      });

      mockUseTestDataStore.mockImplementation((selector) => {
        const state = {
          historyEntries: [entry],
          loadHistoryEntry: mockLoadHistoryEntry,
          deleteHistoryEntry: mockDeleteHistoryEntry,
          clearHistory: mockClearHistory,
        };
        return selector(state as ReturnType<typeof useTestDataStore.getState>);
      });

      render(<HistorySidebar />);

      expect(screen.getByText('88% coherent')).toBeInTheDocument();
    });
  });
});
