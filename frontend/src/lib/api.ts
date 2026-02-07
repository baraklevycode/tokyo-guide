/**
 * API client for the Tokyo Guide backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ── Types ────────────────────────────────────────────────────────────────────

export interface SourceReference {
  id: string;
  title: string;
  title_hebrew: string;
  category: string;
  similarity: number;
}

export interface ChatResponse {
  answer: string;
  sources: SourceReference[];
  session_id: string;
  suggested_questions: string[];
}

export interface CategoryInfo {
  category: string;
  label_hebrew: string;
  count: number;
  icon: string;
}

export interface SectionsResponse {
  categories: CategoryInfo[];
}

export interface ContentItem {
  id: string;
  title: string;
  title_hebrew: string;
  content_hebrew: string;
  category: string;
  subcategory?: string;
  tags: string[];
  location_name?: string;
  latitude?: number;
  longitude?: number;
  price_range?: string;
  recommended_duration?: string;
  best_time_to_visit?: string;
}

export interface SearchResponse {
  results: ContentItem[];
  total: number;
}

export interface SuggestionsResponse {
  suggestions: string[];
}

// ── API Functions ────────────────────────────────────────────────────────────

export async function sendChatMessage(
  question: string,
  sessionId?: string | null
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      session_id: sessionId || null,
    }),
  });

  if (!response.ok) {
    throw new Error(`Chat API error: ${response.status}`);
  }

  return response.json();
}

export async function getSections(): Promise<SectionsResponse> {
  const response = await fetch(`${API_BASE}/api/sections`);
  if (!response.ok) {
    throw new Error(`Sections API error: ${response.status}`);
  }
  return response.json();
}

export async function getSectionContent(
  category: string
): Promise<ContentItem[]> {
  const response = await fetch(`${API_BASE}/api/section/${category}`);
  if (!response.ok) {
    throw new Error(`Section content API error: ${response.status}`);
  }
  return response.json();
}

export async function searchContent(
  query: string,
  category?: string
): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE}/api/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, category: category || null }),
  });

  if (!response.ok) {
    throw new Error(`Search API error: ${response.status}`);
  }

  return response.json();
}

export async function getSuggestions(): Promise<SuggestionsResponse> {
  const response = await fetch(`${API_BASE}/api/suggestions`);
  if (!response.ok) {
    throw new Error(`Suggestions API error: ${response.status}`);
  }
  return response.json();
}
