"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import ContentCard from "@/components/ContentCard";
import { getSectionContent, type ContentItem } from "@/lib/api";

const CATEGORY_LABELS: Record<string, { label: string; icon: string }> = {
  neighborhoods: { label: "שכונות ואזורים", icon: "🏘️" },
  attractions: { label: "אטרקציות וציוני דרך", icon: "⛩️" },
  restaurants: { label: "מסעדות ואוכל", icon: "🍜" },
  hotels: { label: "מלונות ולינה", icon: "🏨" },
  transportation: { label: "תחבורה", icon: "🚃" },
  shopping: { label: "קניות", icon: "🛍️" },
  cultural_experiences: { label: "חוויות תרבותיות", icon: "🎎" },
  day_trips: { label: "טיולי יום", icon: "🗻" },
  practical_tips: { label: "טיפים שימושיים", icon: "💡" },
  itinerary: { label: "הצעות למסלולים", icon: "🗺️" },
};

export default function CategoryPage() {
  const params = useParams();
  const category = params.category as string;
  const [items, setItems] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const categoryInfo = CATEGORY_LABELS[category] || {
    label: category,
    icon: "📌",
  };

  useEffect(() => {
    async function loadContent() {
      try {
        const data = await getSectionContent(category);
        setItems(data);
      } catch (err) {
        console.error("Failed to load content:", err);
        setError("לא הצלחנו לטעון את התוכן. נסו שוב.");
      } finally {
        setLoading(false);
      }
    }
    if (category) {
      loadContent();
    }
  }, [category]);

  return (
    <>
      <Header />

      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Breadcrumb */}
          <nav className="flex items-center gap-2 text-sm text-gray-400 mb-6">
            <Link href="/" className="hover:text-gray-600 transition-colors">
              ראשי
            </Link>
            <span>/</span>
            <Link
              href="/sections"
              className="hover:text-gray-600 transition-colors"
            >
              קטגוריות
            </Link>
            <span>/</span>
            <span className="text-gray-700">{categoryInfo.label}</span>
          </nav>

          {/* Title */}
          <div className="flex items-center gap-3 mb-8">
            <span className="text-4xl">{categoryInfo.icon}</span>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {categoryInfo.label}
              </h1>
              {!loading && (
                <p className="text-gray-500 mt-1">{items.length} פריטים</p>
              )}
            </div>
          </div>

          {/* Content */}
          {loading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div
                  key={i}
                  className="bg-gray-50 rounded-xl h-32 animate-pulse"
                />
              ))}
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <p className="text-red-500 text-lg">{error}</p>
              <Link
                href="/sections"
                className="text-pink-600 hover:text-pink-700 mt-4 inline-block"
              >
                חזרה לקטגוריות
              </Link>
            </div>
          ) : items.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg">
                אין תוכן זמין בקטגוריה זו כרגע.
              </p>
              <Link
                href="/sections"
                className="text-pink-600 hover:text-pink-700 mt-4 inline-block"
              >
                חזרה לקטגוריות
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {items.map((item) => (
                <ContentCard key={item.id} item={item} />
              ))}
            </div>
          )}
        </div>
      </main>

      <Footer />
    </>
  );
}
