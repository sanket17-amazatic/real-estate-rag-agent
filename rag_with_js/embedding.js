import { openai, supabase } from "./config.js";

export async function generateEmbedding(text) {
  const embedding = await openai.embeddings.create({
    model: "text-embedding-ada-002",
    input: text,
  });
  return embedding;
}

export async function storeEmbeddingToSupabase(data) {
  // const resp = await supabase.from("real_estate").select("*");
  const { data: insertedData, error } = await supabase
    .from("real_estate")
    .insert(data)
    .select();
  if (error) {
    console.error("Error inserting data:", error);
  } else {
    console.log("All embedding saved successfully", insertedData);
  }
}
