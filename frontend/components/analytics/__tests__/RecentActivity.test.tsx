/**
 * Unit tests for RecentActivity Component
 */

import { render, screen } from '@testing-library/react';
import { RecentActivity } from '../RecentActivity';
import { ActivityItem } from '@/lib/analytics/types';
import { DUMMY_ANALYTICS } from '@/lib/analytics/dummy-data';

describe('RecentActivity', () => {
  const sampleData: ActivityItem[] = DUMMY_ANALYTICS.recentActivity;

  describe('Rendering', () => {
    it('should render the activity list', () => {
      render(<RecentActivity data={sampleData} />);
      const list = screen.getByRole('list', { name: /recent activity/i });
      expect(list).toBeInTheDocument();
    });

    it('should render activity items', () => {
      render(<RecentActivity data={sampleData} />);
      expect(screen.getByText(/Guest Checkout Feature/)).toBeInTheDocument();
      expect(screen.getByText(/Product Reviews/)).toBeInTheDocument();
    });

    it('should display action and title', () => {
      render(<RecentActivity data={sampleData} />);
      expect(screen.getByText(/Analyzed Guest Checkout Feature/)).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      const { container } = render(
        <RecentActivity data={sampleData} className="custom-class" />
      );
      expect(container.firstChild).toHaveClass('custom-class');
    });
  });

  describe('Max Items', () => {
    it('should respect maxItems prop', () => {
      render(<RecentActivity data={sampleData} maxItems={3} />);
      const items = screen.getAllByText(/tokens$/);
      expect(items.length).toBeLessThanOrEqual(3);
    });

    it('should use default maxItems of 8', () => {
      render(<RecentActivity data={sampleData} />);
      // With 8 items in sample data, all should be shown
      const items = screen.getAllByText(/tokens$/);
      expect(items.length).toBe(8);
    });
  });

  describe('Activity Content', () => {
    it('should display agent name', () => {
      render(<RecentActivity data={sampleData} />);
      expect(screen.getAllByText('Requirement Analysis').length).toBeGreaterThan(0);
    });

    it('should display metrics when present', () => {
      render(<RecentActivity data={sampleData} />);
      expect(screen.getByText('72/100')).toBeInTheDocument();
      expect(screen.getByText('8 cases')).toBeInTheDocument();
    });

    it('should display token count', () => {
      render(<RecentActivity data={sampleData} />);
      // Multiple items may have similar token counts
      const tokenElements = screen.getAllByText(/tokens$/);
      expect(tokenElements.length).toBeGreaterThan(0);
    });
  });

  describe('Loading State', () => {
    it('should show loading skeleton when isLoading is true', () => {
      render(<RecentActivity data={sampleData} isLoading />);
      const skeleton = screen.getByLabelText(/loading activities/i);
      expect(skeleton).toBeInTheDocument();
    });

    it('should have aria-busy when loading', () => {
      render(<RecentActivity data={sampleData} isLoading />);
      const skeleton = screen.getByLabelText(/loading activities/i);
      expect(skeleton).toHaveAttribute('aria-busy', 'true');
    });

    it('should not render list content when loading', () => {
      render(<RecentActivity data={sampleData} isLoading />);
      expect(screen.queryByRole('list')).not.toBeInTheDocument();
    });

    it('should respect maxItems for skeleton count', () => {
      const { container } = render(
        <RecentActivity data={sampleData} isLoading maxItems={5} />
      );
      const skeletonItems = container.querySelectorAll('.bg-gray-50.rounded-lg');
      expect(skeletonItems.length).toBe(5);
    });
  });

  describe('Empty State', () => {
    it('should show empty state when data is empty', () => {
      render(<RecentActivity data={[]} />);
      const emptyState = screen.getByRole('status', { name: /no recent activity/i });
      expect(emptyState).toBeInTheDocument();
    });

    it('should show empty state message', () => {
      render(<RecentActivity data={[]} />);
      expect(screen.getByText(/no recent activity/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have role="list" with aria-label', () => {
      render(<RecentActivity data={sampleData} />);
      const list = screen.getByRole('list');
      expect(list).toHaveAttribute('aria-label', 'Recent activity');
    });
  });

  describe('Agent Icons', () => {
    it('should display agent icons', () => {
      render(<RecentActivity data={sampleData} />);
      // Icons should be rendered (they are emojis)
      expect(screen.getAllByText('🔍').length).toBeGreaterThan(0);
      expect(screen.getAllByText('🧪').length).toBeGreaterThan(0);
    });
  });
});
