import { splitContent, fetchContentFromFile } from "./splitDocument.js";
import { generateEmbedding, storeEmbeddingToSupabase } from "./embedding.js";

const content = await fetchContentFromFile();
const chunks = await splitContent(content);

const data = await Promise.all(
  chunks.map(async (chunk) => {
    const embedding = await generateEmbedding(chunk.pageContent);
    return {
      content: chunk.pageContent,
      embedding: embedding.data[0].embedding,
    };
  }),
);

console.log(
  `Generated embeddings for ${data.length} chunks.`,
  Array.isArray(data),
);

await storeEmbeddingToSupabase(data);
console.log("All embeddings stored in Supabase");
