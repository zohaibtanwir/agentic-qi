/**
 * Unit tests for QualityScoreChart Component
 */

import { render, screen } from '@testing-library/react';
import { QualityScoreChart } from '../QualityScoreChart';
import { QualityDistribution } from '@/lib/analytics/types';
import { DUMMY_ANALYTICS } from '@/lib/analytics/dummy-data';

// Mock ResizeObserver
const mockResizeObserver = jest.fn(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));
global.ResizeObserver = mockResizeObserver;

describe('QualityScoreChart', () => {
  const sampleData: QualityDistribution[] = DUMMY_ANALYTICS.qualityDistribution;

  describe('Rendering', () => {
    it('should render the chart container', () => {
      render(<QualityScoreChart data={sampleData} />);
      const chart = screen.getByRole('img', { name: /bar chart showing quality/i });
      expect(chart).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      const { container } = render(
        <QualityScoreChart data={sampleData} className="custom-class" />
      );
      expect(container.firstChild).toHaveClass('custom-class');
    });

    it('should include total count in aria-label', () => {
      render(<QualityScoreChart data={sampleData} />);
      const chart = screen.getByRole('img');
      expect(chart.getAttribute('aria-label')).toContain('Total:');
    });
  });

  describe('Loading State', () => {
    it('should show loading skeleton when isLoading is true', () => {
      render(<QualityScoreChart data={sampleData} isLoading />);
      const skeleton = screen.getByLabelText(/loading chart/i);
      expect(skeleton).toBeInTheDocument();
    });

    it('should have aria-busy when loading', () => {
      render(<QualityScoreChart data={sampleData} isLoading />);
      const skeleton = screen.getByLabelText(/loading chart/i);
      expect(skeleton).toHaveAttribute('aria-busy', 'true');
    });
  });

  describe('Empty State', () => {
    it('should show empty state when data is empty', () => {
      render(<QualityScoreChart data={[]} />);
      const emptyState = screen.getByRole('img', { name: /no data available/i });
      expect(emptyState).toBeInTheDocument();
    });

    it('should show empty state message', () => {
      render(<QualityScoreChart data={[]} />);
      expect(screen.getByText(/no data available/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have role="img"', () => {
      render(<QualityScoreChart data={sampleData} />);
      expect(screen.getByRole('img')).toBeInTheDocument();
    });

    it('should have descriptive aria-label', () => {
      render(<QualityScoreChart data={sampleData} />);
      const chart = screen.getByRole('img');
      expect(chart).toHaveAttribute('aria-label', expect.stringContaining('quality distribution'));
    });
  });

  describe('Data Handling', () => {
    it('should handle 5 grades', () => {
      render(<QualityScoreChart data={sampleData} />);
      const chart = screen.getByRole('img', { name: /bar chart/i });
      expect(chart).toBeInTheDocument();
    });

    it('should handle single grade', () => {
      const singleGrade: QualityDistribution[] = [
        { grade: 'A', count: 10, percentage: 100 },
      ];
      render(<QualityScoreChart data={singleGrade} />);
      expect(screen.getByRole('img', { name: /bar chart/i })).toBeInTheDocument();
    });
  });
});
