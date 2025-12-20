"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Dashboard", href: "/" },
  { name: "Architecture", href: "/architecture" },
  { name: "Entities", href: "/entities" },
  { name: "Workflows", href: "/workflows" },
  { name: "Orchestration", href: "/generate" },
  { name: "Knowledge", href: "/knowledge" },
];

export default function Header() {
  const pathname = usePathname();

  return (
    <header className="macys-header">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between py-4">
          {/* Macy's Logo */}
          <Link href="/" className="flex items-center">
            <Image
              src="https://assets.macysassets.com/app/navigation-wgl/static/images/logo.svg"
              alt="Macy's"
              width={120}
              height={40}
              priority
            />
            <span className="ml-4 text-lg font-semibold text-gray-800">
              eCommerce Domain Agent
            </span>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center space-x-6">
            {navigation.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "text-sm font-medium transition-colors hover:text-macys-red",
                    isActive
                      ? "text-macys-red border-b-2 border-macys-red pb-1"
                      : "text-gray-700"
                  )}
                >
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>
    </header>
  );
}