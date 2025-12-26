/**
 * Unit tests for ExportButton Component
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ExportButton } from '../ExportButton';
import { exportToCSV } from '@/lib/analytics/utils';

// Mock the utils module
jest.mock('@/lib/analytics/utils', () => ({
  exportToCSV: jest.fn(),
}));
const mockExportToCSV = jest.mocked(exportToCSV);

describe('ExportButton', () => {
  const sampleData = [
    { id: 1, name: 'Test 1', value: 100 },
    { id: 2, name: 'Test 2', value: 200 },
  ];

  const defaultProps = {
    data: sampleData,
    filename: 'test-export',
  };

  beforeEach(() => {
    jest.clearAllMocks();
    // Mock window.alert
    jest.spyOn(window, 'alert').mockImplementation(() => {});
    // Mock URL methods
    global.URL.createObjectURL = jest.fn(() => 'blob:test-url');
    global.URL.revokeObjectURL = jest.fn();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Rendering', () => {
    it('should render the export button', () => {
      render(<ExportButton {...defaultProps} />);

      expect(
        screen.getByRole('button', { name: /export/i })
      ).toBeInTheDocument();
    });

    it('should display Export text', () => {
      render(<ExportButton {...defaultProps} />);

      expect(screen.getByText('Export')).toBeInTheDocument();
    });

    it('should render download icon', () => {
      render(<ExportButton {...defaultProps} />);

      const button = screen.getByRole('button');
      expect(button.querySelector('svg')).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      const { container } = render(
        <ExportButton {...defaultProps} className="custom-class" />
      );

      expect(container.firstChild).toHaveClass('custom-class');
    });

    it('should not show dropdown initially', () => {
      render(<ExportButton {...defaultProps} />);

      expect(screen.queryByRole('menu')).not.toBeInTheDocument();
    });
  });

  describe('Single Format Mode', () => {
    it('should render simple button when only one format', () => {
      render(<ExportButton {...defaultProps} formats={['csv']} />);

      const button = screen.getByRole('button', { name: /export as csv/i });
      expect(button).toBeInTheDocument();
    });

    it('should export directly when only one format', async () => {
      const user = userEvent.setup();
      const onExport = jest.fn();

      render(
        <ExportButton
          {...defaultProps}
          formats={['csv']}
          onExport={onExport}
        />
      );

      await user.click(screen.getByRole('button', { name: /export as csv/i }));

      expect(mockExportToCSV).toHaveBeenCalled();
      expect(onExport).toHaveBeenCalledWith('csv');
    });
  });

  describe('Dropdown Behavior', () => {
    it('should open dropdown when clicked with multiple formats', async () => {
      const user = userEvent.setup();
      render(<ExportButton {...defaultProps} formats={['csv', 'json']} />);

      const button = screen.getByRole('button', { name: /export options/i });
      await user.click(button);

      expect(screen.getByRole('menu')).toBeInTheDocument();
    });

    it('should close dropdown when clicking outside', async () => {
      const user = userEvent.setup();
      render(
        <div>
          <ExportButton {...defaultProps} formats={['csv', 'json']} />
          <div data-testid="outside">Outside</div>
        </div>
      );

      // Open dropdown
      const button = screen.getByRole('button', { name: /export options/i });
      await user.click(button);
      expect(screen.getByRole('menu')).toBeInTheDocument();

      // Click outside
      await user.click(screen.getByTestId('outside'));
      expect(screen.queryByRole('menu')).not.toBeInTheDocument();
    });

    it('should close dropdown when Escape is pressed', async () => {
      const user = userEvent.setup();
      render(<ExportButton {...defaultProps} formats={['csv', 'json']} />);

      // Open dropdown
      const button = screen.getByRole('button', { name: /export options/i });
      await user.click(button);
      expect(screen.getByRole('menu')).toBeInTheDocument();

      // Press Escape
      await user.keyboard('{Escape}');
      expect(screen.queryByRole('menu')).not.toBeInTheDocument();
    });

    it('should display only requested formats', async () => {
      const user = userEvent.setup();
      render(<ExportButton {...defaultProps} formats={['csv', 'json']} />);

      const button = screen.getByRole('button', { name: /export options/i });
      await user.click(button);

      expect(screen.getByText('Export as CSV')).toBeInTheDocument();
      expect(screen.getByText('Export as JSON')).toBeInTheDocument();
      expect(screen.queryByText('Export as PDF')).not.toBeInTheDocument();
    });
  });

  describe('Export Actions', () => {
    it('should call exportToCSV for CSV format', async () => {
      const user = userEvent.setup();
      const onExport = jest.fn();

      render(
        <ExportButton
          {...defaultProps}
          formats={['csv', 'json']}
          onExport={onExport}
        />
      );

      const button = screen.getByRole('button', { name: /export options/i });
      await user.click(button);
      await user.click(screen.getByText('Export as CSV'));

      expect(mockExportToCSV).toHaveBeenCalled();
      expect(onExport).toHaveBeenCalledWith('csv');
    });

    it('should call onExport for JSON format', async () => {
      const user = userEvent.setup();
      const onExport = jest.fn();

      render(
        <ExportButton
          {...defaultProps}
          formats={['csv', 'json']}
          onExport={onExport}
        />
      );

      const button = screen.getByRole('button', { name: /export options/i });
      await user.click(button);
      await user.click(screen.getByText('Export as JSON'));

      expect(onExport).toHaveBeenCalledWith('json');
    });

    it('should show alert for PDF format (placeholder)', async () => {
      const user = userEvent.setup();
      const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});

      render(<ExportButton {...defaultProps} formats={['csv', 'pdf']} />);

      const button = screen.getByRole('button', { name: /export options/i });
      await user.click(button);
      await user.click(screen.getByText('Export as PDF'));

      expect(alertSpy).toHaveBeenCalledWith(
        'PDF export will be available in a future update.'
      );
    });

    it('should close dropdown after export', async () => {
      const user = userEvent.setup();

      render(<ExportButton {...defaultProps} formats={['csv', 'json']} />);

      const button = screen.getByRole('button', { name: /export options/i });
      await user.click(button);
      await user.click(screen.getByText('Export as CSV'));

      expect(screen.queryByRole('menu')).not.toBeInTheDocument();
    });
  });

  describe('Disabled State', () => {
    it('should not open when disabled', async () => {
      const user = userEvent.setup();
      render(
        <ExportButton {...defaultProps} formats={['csv', 'json']} disabled />
      );

      const button = screen.getByRole('button', { name: /export options/i });
      await user.click(button);

      expect(screen.queryByRole('menu')).not.toBeInTheDocument();
    });

    it('should have disabled attribute when disabled', () => {
      render(
        <ExportButton {...defaultProps} formats={['csv', 'json']} disabled />
      );

      const button = screen.getByRole('button', { name: /export options/i });
      expect(button).toBeDisabled();
    });

    it('should be disabled when data is empty', () => {
      render(
        <ExportButton {...defaultProps} data={[]} formats={['csv', 'json']} />
      );

      const button = screen.getByRole('button', { name: /export options/i });
      expect(button).toBeDisabled();
    });

    it('should not export when data is empty', async () => {
      const user = userEvent.setup();
      const onExport = jest.fn();

      render(
        <ExportButton
          data={[]}
          formats={['csv']}
          onExport={onExport}
        />
      );

      const button = screen.getByRole('button');
      await user.click(button);

      expect(mockExportToCSV).not.toHaveBeenCalled();
      expect(onExport).not.toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('should have aria-haspopup attribute when multiple formats', () => {
      render(<ExportButton {...defaultProps} formats={['csv', 'json']} />);

      const button = screen.getByRole('button', { name: /export options/i });
      expect(button).toHaveAttribute('aria-haspopup', 'menu');
    });

    it('should have aria-expanded attribute when multiple formats', async () => {
      const user = userEvent.setup();
      render(<ExportButton {...defaultProps} formats={['csv', 'json']} />);

      const button = screen.getByRole('button', { name: /export options/i });
      expect(button).toHaveAttribute('aria-expanded', 'false');

      await user.click(button);
      expect(button).toHaveAttribute('aria-expanded', 'true');
    });

    it('should have aria-label on the button', () => {
      render(<ExportButton {...defaultProps} formats={['csv', 'json']} />);

      const button = screen.getByRole('button', { name: /export options/i });
      expect(button).toHaveAttribute('aria-label', 'Export options');
    });

    it('should have aria-label on the menu', async () => {
      const user = userEvent.setup();
      render(<ExportButton {...defaultProps} formats={['csv', 'json']} />);

      const button = screen.getByRole('button', { name: /export options/i });
      await user.click(button);

      const menu = screen.getByRole('menu');
      expect(menu).toHaveAttribute('aria-label', 'Export format options');
    });

    it('should have menuitem role for options', async () => {
      const user = userEvent.setup();
      render(<ExportButton {...defaultProps} formats={['csv', 'json']} />);

      const button = screen.getByRole('button', { name: /export options/i });
      await user.click(button);

      const menuItems = screen.getAllByRole('menuitem');
      expect(menuItems).toHaveLength(2);
    });
  });

  describe('Default Props', () => {
    it('should use default filename when not provided', async () => {
      const user = userEvent.setup();

      render(<ExportButton data={sampleData} formats={['csv']} />);

      await user.click(screen.getByRole('button', { name: /export as csv/i }));

      expect(mockExportToCSV).toHaveBeenCalledWith(
        sampleData,
        expect.stringContaining('analytics-export')
      );
    });

    it('should default to csv and json formats', async () => {
      const user = userEvent.setup();
      render(<ExportButton data={sampleData} />);

      const button = screen.getByRole('button', { name: /export options/i });
      await user.click(button);

      expect(screen.getByText('Export as CSV')).toBeInTheDocument();
      expect(screen.getByText('Export as JSON')).toBeInTheDocument();
      expect(screen.queryByText('Export as PDF')).not.toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should toggle dropdown on repeated clicks', async () => {
      const user = userEvent.setup();
      render(<ExportButton {...defaultProps} formats={['csv', 'json']} />);

      const button = screen.getByRole('button', { name: /export options/i });

      // First click - open
      await user.click(button);
      expect(screen.getByRole('menu')).toBeInTheDocument();

      // Second click - close
      await user.click(button);
      expect(screen.queryByRole('menu')).not.toBeInTheDocument();

      // Third click - open again
      await user.click(button);
      expect(screen.getByRole('menu')).toBeInTheDocument();
    });

    it('should handle all three formats', async () => {
      const user = userEvent.setup();
      render(
        <ExportButton {...defaultProps} formats={['csv', 'json', 'pdf']} />
      );

      const button = screen.getByRole('button', { name: /export options/i });
      await user.click(button);

      expect(screen.getByText('Export as CSV')).toBeInTheDocument();
      expect(screen.getByText('Export as JSON')).toBeInTheDocument();
      expect(screen.getByText('Export as PDF')).toBeInTheDocument();
    });
  });
});
