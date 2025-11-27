create table real_estate (
  id bigserial primary key,
  content text, -- corresponds to the "text chunk"
  embedding vector(1536) -- 1536 works for OpenAI embeddings
);

-- Create a function to search for documents
create or replace function match_real_estate (
  query_embedding vector(1536),
  match_threshold float,
  match_count int
)
returns table (
  id bigint,
  content text,
  similarity float
)
language sql stable
as $$
  select
    real_estate.id,
    real_estate.content,
    1 - (real_estate.embedding <=> query_embedding) as similarity
  from real_estate
  where 1 - (real_estate.embedding <=> query_embedding) > match_threshold
  order by similarity desc
  limit match_count;
$$;