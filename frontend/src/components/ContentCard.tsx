"use client";

import { useState } from "react";
import type { ContentItem } from "@/lib/api";

interface ContentCardProps {
  item: ContentItem;
}

export default function ContentCard({ item }: ContentCardProps) {
  const [expanded, setExpanded] = useState(false);

  const previewText = item.content_hebrew.slice(0, 200);
  const hasMore = item.content_hebrew.length > 200;

  return (
    <div className="bg-white rounded-xl border border-gray-100 p-6 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <h3 className="text-lg font-bold text-gray-900">
            {item.title_hebrew}
          </h3>
          {item.location_name && (
            <p className="text-sm text-pink-600 mt-0.5">{item.location_name}</p>
          )}
        </div>
        {item.price_range && (
          <span className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded-full whitespace-nowrap">
            {item.price_range}
          </span>
        )}
      </div>

      {/* Tags */}
      {item.tags && item.tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-3">
          {item.tags.map((tag) => (
            <span
              key={tag}
              className="text-xs bg-gray-100 text-gray-600 px-2.5 py-1 rounded-full"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Content */}
      <p className="text-gray-700 text-sm leading-relaxed mt-4">
        {expanded ? item.content_hebrew : previewText}
        {hasMore && !expanded && "..."}
      </p>

      {hasMore && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-sm text-pink-600 hover:text-pink-700 font-medium mt-3 transition-colors"
        >
          {expanded ? "הצג פחות" : "קרא עוד"}
        </button>
      )}

      {/* Meta info */}
      <div className="flex flex-wrap items-center gap-4 mt-4 text-xs text-gray-400">
        {item.recommended_duration && (
          <span>⏱ {item.recommended_duration}</span>
        )}
        {item.best_time_to_visit && (
          <span>📅 {item.best_time_to_visit}</span>
        )}
        {item.subcategory && <span>📂 {item.subcategory}</span>}
      </div>
    </div>
  );
}
