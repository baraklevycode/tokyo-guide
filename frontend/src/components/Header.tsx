"use client";

import Link from "next/link";
import { useState } from "react";

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="bg-white/90 backdrop-blur-sm border-b border-gray-100 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">⛩️</span>
            <span className="text-xl font-bold text-gray-900">
              מדריך טוקיו
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-8">
            <Link
              href="/sections"
              className="text-gray-600 hover:text-gray-900 transition-colors font-medium"
            >
              קטגוריות
            </Link>
            <Link
              href="/sections/neighborhoods"
              className="text-gray-600 hover:text-gray-900 transition-colors font-medium"
            >
              שכונות
            </Link>
            <Link
              href="/sections/restaurants"
              className="text-gray-600 hover:text-gray-900 transition-colors font-medium"
            >
              מסעדות
            </Link>
            <Link
              href="/sections/practical_tips"
              className="text-gray-600 hover:text-gray-900 transition-colors font-medium"
            >
              טיפים
            </Link>
          </nav>

          {/* Mobile menu button */}
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
            aria-label="תפריט"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {menuOpen ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Navigation */}
        {menuOpen && (
          <nav className="md:hidden py-4 border-t border-gray-100 animate-fade-in">
            <div className="flex flex-col gap-4">
              <Link
                href="/sections"
                onClick={() => setMenuOpen(false)}
                className="text-gray-600 hover:text-gray-900 font-medium py-1"
              >
                כל הקטגוריות
              </Link>
              <Link
                href="/sections/neighborhoods"
                onClick={() => setMenuOpen(false)}
                className="text-gray-600 hover:text-gray-900 font-medium py-1"
              >
                שכונות ואזורים
              </Link>
              <Link
                href="/sections/restaurants"
                onClick={() => setMenuOpen(false)}
                className="text-gray-600 hover:text-gray-900 font-medium py-1"
              >
                מסעדות ואוכל
              </Link>
              <Link
                href="/sections/practical_tips"
                onClick={() => setMenuOpen(false)}
                className="text-gray-600 hover:text-gray-900 font-medium py-1"
              >
                טיפים שימושיים
              </Link>
            </div>
          </nav>
        )}
      </div>
    </header>
  );
}
