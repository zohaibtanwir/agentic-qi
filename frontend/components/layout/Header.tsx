'use client';

import Image from 'next/image';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export function Header() {
  const pathname = usePathname();

  const navLinks = [
    { href: '/', label: 'Home' },
    { href: '/test-cases', label: 'Test Cases' },
    { href: '/test-data', label: 'Test Data' },
    { href: '/ecommerce', label: 'eCommerce' },
  ];

  return (
    <header className="fixed top-0 w-full h-16 bg-white border-b border-[var(--border-default)] shadow-sm z-50">
      <div className="flex items-center justify-between h-full px-6 max-w-7xl mx-auto">
        {/* Logo and title */}
        <Link href="/" className="flex items-center space-x-3 hover:opacity-80 transition-opacity">
          <Image
            src="https://assets.macysassets.com/app/navigation-wgl/static/images/logo.svg"
            alt="Macy's Logo"
            width={96}
            height={32}
            className="h-8 w-auto"
            unoptimized
          />
          <span className="text-lg font-semibold text-[var(--text-secondary)]">
            QA Platform
          </span>
        </Link>

        {/* Navigation */}
        <nav className="flex items-center space-x-6">
          {navLinks.map((link) => {
            const isActive = link.href === '/'
              ? pathname === '/'
              : pathname.startsWith(link.href);

            return (
              <Link
                key={link.href}
                href={link.href}
                className={`text-sm font-medium transition-colors ${
                  isActive
                    ? 'text-[var(--accent-default)]'
                    : 'text-[var(--text-secondary)] hover:text-[var(--accent-default)]'
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
