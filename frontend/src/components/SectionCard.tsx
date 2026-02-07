import Link from "next/link";
import type { CategoryInfo } from "@/lib/api";

interface SectionCardProps {
  category: CategoryInfo;
}

export default function SectionCard({ category }: SectionCardProps) {
  return (
    <Link
      href={`/sections/${category.category}`}
      className="group block bg-white rounded-2xl border border-gray-100 p-6 hover:shadow-lg hover:border-pink-200 transition-all duration-300"
    >
      <div className="flex items-start gap-4">
        <span className="text-3xl group-hover:scale-110 transition-transform duration-300">
          {category.icon}
        </span>
        <div className="flex-1">
          <h3 className="text-lg font-bold text-gray-900 group-hover:text-pink-700 transition-colors">
            {category.label_hebrew}
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            {category.count} פריטים
          </p>
        </div>
        <svg
          className="w-5 h-5 text-gray-300 group-hover:text-pink-500 transition-colors rotate-180"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5l7 7-7 7"
          />
        </svg>
      </div>
    </Link>
  );
}
