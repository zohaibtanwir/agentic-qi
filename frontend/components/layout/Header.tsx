'use client';

import Link from 'next/link';

export function Header() {
  return (
    <header className="fixed top-0 w-full h-16 bg-white border-b border-[var(--border-default)] shadow-sm z-50">
      <div className="flex items-center justify-between h-full px-6 max-w-7xl mx-auto">
        {/* Logo and title */}
        <Link href="/" className="flex items-center space-x-3 hover:opacity-80 transition-opacity">
          <div className="w-10 h-10 bg-[var(--accent-default)] rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-xl">QA</span>
          </div>
          <span className="text-lg font-semibold text-[var(--text-secondary)]">
            QA Platform
          </span>
        </Link>

        {/* Navigation */}
        <nav className="flex items-center space-x-6">
          <Link
            href="/"
            className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--accent-default)] transition-colors"
          >
            Home
          </Link>
          <Link
            href="/test-cases"
            className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--accent-default)] transition-colors"
          >
            Test Cases
          </Link>
          <a
            href={process.env.NEXT_PUBLIC_TEST_DATA_AGENT_URL || 'http://localhost:3001'}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--accent-default)] transition-colors"
          >
            Test Data
          </a>
        </nav>
      </div>
    </header>
  );
}
