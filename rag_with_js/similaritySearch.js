import { supabase } from "./config.js";

// rpc - remote procedure call
/**
 * Matches the given embedding against stored document embeddings using Supabase RPC.
 * @async
 * @param {number[]} embedding - The embedding vector to match.
 * @param {number} [threshold=0.75] - The similarity threshold for matching.
 * @param {number} [matchCount=2] - The maximum number of matches to return.
 * @returns {Promise<Object[]>} An array of matched documents.
 */
export async function matchEmbedding(
  embedding,
  threshold = 0.75,
  matchCount = 2,
) {
  const { data, error } = await supabase.rpc("match_real_estate", {
    query_embedding: embedding,
    match_threshold: threshold,
    match_count: matchCount,
  });

  if (error) {
    console.error("Error matching embedding:", error);
    return [];
  }

  return data;
}
