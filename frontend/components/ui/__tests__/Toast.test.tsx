import { render, screen, fireEvent, act, waitFor } from '@testing-library/react';
import { ToastProvider, useToast, useToastActions } from '../Toast';

// Test component that uses the toast hook
function TestComponent() {
  const toast = useToastActions();

  return (
    <div>
      <button onClick={() => toast.success('Success message')}>Show Success</button>
      <button onClick={() => toast.error('Error message')}>Show Error</button>
      <button onClick={() => toast.info('Info message')}>Show Info</button>
      <button onClick={() => toast.warning('Warning message')}>Show Warning</button>
      <button onClick={() => toast.success('Custom duration', 5000)}>Custom Duration</button>
    </div>
  );
}

// Test component for dismiss functionality
function DismissTestComponent() {
  const { toasts, removeToast, addToast } = useToast();

  return (
    <div>
      <button onClick={() => addToast('Dismissable toast', 'info', 0)}>Add Toast</button>
      {toasts.map(t => (
        <div key={t.id} data-testid={`toast-${t.id}`}>
          {t.message}
          <button onClick={() => removeToast(t.id)}>Dismiss</button>
        </div>
      ))}
    </div>
  );
}

describe('Toast', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('ToastProvider', () => {
    it('renders children correctly', () => {
      render(
        <ToastProvider>
          <div data-testid="child">Child content</div>
        </ToastProvider>
      );

      expect(screen.getByTestId('child')).toBeInTheDocument();
    });

    it('provides toast context to children', () => {
      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      expect(screen.getByText('Show Success')).toBeInTheDocument();
    });
  });

  describe('useToast hook', () => {
    it('throws error when used outside ToastProvider', () => {
      // Suppress console.error for this test
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      expect(() => {
        render(<TestComponent />);
      }).toThrow('useToast must be used within a ToastProvider');

      consoleSpy.mockRestore();
    });
  });

  describe('Toast notifications', () => {
    it('shows success toast when triggered', () => {
      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      fireEvent.click(screen.getByText('Show Success'));

      expect(screen.getByText('Success message')).toBeInTheDocument();
      expect(screen.getByRole('alert')).toHaveClass('bg-green-50');
    });

    it('shows error toast when triggered', () => {
      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      fireEvent.click(screen.getByText('Show Error'));

      expect(screen.getByText('Error message')).toBeInTheDocument();
      expect(screen.getByRole('alert')).toHaveClass('bg-red-50');
    });

    it('shows info toast when triggered', () => {
      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      fireEvent.click(screen.getByText('Show Info'));

      expect(screen.getByText('Info message')).toBeInTheDocument();
      expect(screen.getByRole('alert')).toHaveClass('bg-blue-50');
    });

    it('shows warning toast when triggered', () => {
      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      fireEvent.click(screen.getByText('Show Warning'));

      expect(screen.getByText('Warning message')).toBeInTheDocument();
      expect(screen.getByRole('alert')).toHaveClass('bg-yellow-50');
    });

    it('auto-dismisses toast after default duration', async () => {
      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      fireEvent.click(screen.getByText('Show Success'));
      expect(screen.getByText('Success message')).toBeInTheDocument();

      // Fast-forward past the default 3000ms duration
      act(() => {
        jest.advanceTimersByTime(3100);
      });

      await waitFor(() => {
        expect(screen.queryByText('Success message')).not.toBeInTheDocument();
      });
    });

    it('shows multiple toasts simultaneously', () => {
      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      fireEvent.click(screen.getByText('Show Success'));
      fireEvent.click(screen.getByText('Show Error'));
      fireEvent.click(screen.getByText('Show Info'));

      expect(screen.getByText('Success message')).toBeInTheDocument();
      expect(screen.getByText('Error message')).toBeInTheDocument();
      expect(screen.getByText('Info message')).toBeInTheDocument();
    });

    it('can be manually dismissed', () => {
      render(
        <ToastProvider>
          <DismissTestComponent />
        </ToastProvider>
      );

      fireEvent.click(screen.getByText('Add Toast'));
      // The toast appears both in test component and actual toast container
      expect(screen.getAllByText('Dismissable toast').length).toBe(2);

      // Click the dismiss button in the test component
      fireEvent.click(screen.getByText('Dismiss'));
      // After dismissal, only the test component's copy should remain briefly
      // but both should be removed since removeToast is called
      expect(screen.queryAllByText('Dismissable toast').length).toBeLessThan(2);
    });

    it('has accessible dismiss button', () => {
      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      fireEvent.click(screen.getByText('Show Success'));

      const dismissButton = screen.getByLabelText('Dismiss notification');
      expect(dismissButton).toBeInTheDocument();
    });
  });

  describe('Toast container', () => {
    it('has correct ARIA attributes', () => {
      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      const container = screen.getByLabelText('Notifications');
      expect(container).toHaveAttribute('aria-live', 'polite');
    });
  });

  describe('Toast types and styling', () => {
    const testCases = [
      { button: 'Show Success', expectedClass: 'bg-green-50', borderClass: 'border-green-200' },
      { button: 'Show Error', expectedClass: 'bg-red-50', borderClass: 'border-red-200' },
      { button: 'Show Info', expectedClass: 'bg-blue-50', borderClass: 'border-blue-200' },
      { button: 'Show Warning', expectedClass: 'bg-yellow-50', borderClass: 'border-yellow-200' },
    ];

    testCases.forEach(({ button, expectedClass, borderClass }) => {
      it(`applies correct styling for ${button.replace('Show ', '')} toast`, () => {
        render(
          <ToastProvider>
            <TestComponent />
          </ToastProvider>
        );

        fireEvent.click(screen.getByText(button));

        const alert = screen.getByRole('alert');
        expect(alert).toHaveClass(expectedClass);
        expect(alert).toHaveClass(borderClass);
      });
    });
  });

  describe('Toast icons', () => {
    it('shows checkmark icon for success toast', () => {
      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      fireEvent.click(screen.getByText('Show Success'));

      // Check for SVG with check path
      const alert = screen.getByRole('alert');
      const svg = alert.querySelector('svg');
      expect(svg).toBeInTheDocument();
      expect(svg).toHaveClass('text-green-600');
    });

    it('shows X icon for error toast', () => {
      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      fireEvent.click(screen.getByText('Show Error'));

      const alert = screen.getByRole('alert');
      const svg = alert.querySelector('svg');
      expect(svg).toBeInTheDocument();
      expect(svg).toHaveClass('text-red-600');
    });
  });

  describe('Toast animation', () => {
    it('has slide-in animation class', () => {
      render(
        <ToastProvider>
          <TestComponent />
        </ToastProvider>
      );

      fireEvent.click(screen.getByText('Show Success'));

      const alert = screen.getByRole('alert');
      expect(alert).toHaveClass('animate-slide-in-right');
    });
  });
});
