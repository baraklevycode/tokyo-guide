"use client";

import { useEffect, useState } from "react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import SectionCard from "@/components/SectionCard";
import { getSections, type CategoryInfo } from "@/lib/api";

// Fallback categories for when the API is not available
const FALLBACK_CATEGORIES: CategoryInfo[] = [
  { category: "neighborhoods", label_hebrew: "שכונות ואזורים", count: 0, icon: "🏘️" },
  { category: "attractions", label_hebrew: "אטרקציות וציוני דרך", count: 0, icon: "⛩️" },
  { category: "restaurants", label_hebrew: "מסעדות ואוכל", count: 0, icon: "🍜" },
  { category: "hotels", label_hebrew: "מלונות ולינה", count: 0, icon: "🏨" },
  { category: "transportation", label_hebrew: "תחבורה", count: 0, icon: "🚃" },
  { category: "shopping", label_hebrew: "קניות", count: 0, icon: "🛍️" },
  { category: "cultural_experiences", label_hebrew: "חוויות תרבותיות", count: 0, icon: "🎎" },
  { category: "day_trips", label_hebrew: "טיולי יום", count: 0, icon: "🗻" },
  { category: "practical_tips", label_hebrew: "טיפים שימושיים", count: 0, icon: "💡" },
];

export default function SectionsPage() {
  const [categories, setCategories] = useState<CategoryInfo[]>(FALLBACK_CATEGORIES);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadSections() {
      try {
        const data = await getSections();
        if (data.categories.length > 0) {
          setCategories(data.categories);
        }
      } catch (error) {
        console.error("Failed to load sections:", error);
        // Keep fallback categories
      } finally {
        setLoading(false);
      }
    }
    loadSections();
  }, []);

  return (
    <>
      <Header />

      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center mb-10">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900">
              כל הקטגוריות
            </h1>
            <p className="text-gray-500 mt-3 text-lg">
              בחרו קטגוריה כדי לגלות את הטיפים וההמלצות
            </p>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {[...Array(9)].map((_, i) => (
                <div
                  key={i}
                  className="bg-gray-50 rounded-2xl h-24 animate-pulse"
                />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {categories.map((cat) => (
                <SectionCard key={cat.category} category={cat} />
              ))}
            </div>
          )}
        </div>
      </main>

      <Footer />
    </>
  );
}
