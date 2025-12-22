export function Footer() {
  return (
    <footer className="border-t border-[var(--border-default)] bg-white mt-auto">
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <div className="text-sm text-[var(--text-muted)]">
            © {new Date().getFullYear()} QA Platform. AI-powered test generation.
          </div>

          <div className="flex items-center space-x-6">
            <a
              href="https://github.com/anthropics/claude-code"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-[var(--text-muted)] hover:text-[var(--accent-default)] transition-colors"
            >
              Documentation
            </a>
            <span className="text-xs text-[var(--text-muted)]">
              Powered by gRPC-Web
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}
