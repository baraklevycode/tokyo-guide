-- Enable pgvector extension
create extension if not exists vector;

-- Main content table
create table if not exists tokyo_content (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  title_hebrew text not null,
  content text not null,
  content_hebrew text not null,
  category text not null,
  subcategory text,
  tags text[],
  location_name text,
  latitude float,
  longitude float,
  price_range text,
  recommended_duration text,
  best_time_to_visit text,
  embedding vector(384),
  created_at timestamp default now()
);

-- Index on category for fast filtering
create index if not exists idx_tokyo_content_category on tokyo_content(category);

-- Index on embedding for vector similarity search (ivfflat)
-- Note: run this AFTER inserting data (ivfflat needs data to build lists)
-- create index if not exists idx_tokyo_content_embedding on tokyo_content
--   using ivfflat (embedding vector_cosine_ops) with (lists = 10);

-- User sessions table for chat history
create table if not exists chat_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id text,
  platform text check (platform in ('web', 'telegram')),
  messages jsonb default '[]'::jsonb,
  created_at timestamp default now(),
  updated_at timestamp default now()
);

-- Index on user_id + platform for quick session lookup
create index if not exists idx_chat_sessions_user on chat_sessions(user_id, platform);

-- Vector similarity search function
create or replace function match_documents (
  query_embedding vector(384),
  match_threshold float,
  match_count int
)
returns table (
  id uuid,
  title text,
  title_hebrew text,
  content_hebrew text,
  category text,
  subcategory text,
  location_name text,
  similarity float
)
language sql stable
as $$
  select
    tokyo_content.id,
    tokyo_content.title,
    tokyo_content.title_hebrew,
    tokyo_content.content_hebrew,
    tokyo_content.category,
    tokyo_content.subcategory,
    tokyo_content.location_name,
    1 - (tokyo_content.embedding <=> query_embedding) as similarity
  from tokyo_content
  where 1 - (tokyo_content.embedding <=> query_embedding) > match_threshold
  order by tokyo_content.embedding <=> query_embedding
  limit match_count;
$$;
