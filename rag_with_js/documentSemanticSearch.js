import { generateEmbedding } from "./embedding.js";
import { matchEmbedding } from "./similaritySearch.js";
import { openai } from "./config.js";

const systemPrompt = {
  role: "system",
  content:
    "You are a helpful Real Estate Assistant mostly looking for properties in Pune City. It is a company invloved in Real Estate industry. If any one ask you any question other than Real Estate, you will reply with 'Let's stay on track'. When providing information, ensure it is accurate and relevant to real estate. Also make sure to add appropriate links to their products for more information. If you are unsure about an answer, it's better to admit it than to provide incorrect information. Also, keep your answers concise and to the point. Currently you only have information about properties in Pune city.",
};

const chatMessages = [systemPrompt];

async function getChatCompletions(text, query) {
  chatMessages.push({
    role: "user",
    content: `Content: ${text}. Question: ${query}`,
  });
  try {
    const response = await openai.chat.completions.create({
      model: "gpt-5-nano",
      messages: chatMessages,
    });

    console.log(response.choices[0].message);
    chatMessages.push(response.choices[0].message);
    return response.choices[0].message;
  } catch (error) {
    console.error("Error during chat completions:", error);
  }
}

export const documentSemanticSearch = async (query) => {
  try {
    const queryEmbedding = await generateEmbedding(query);
    const queryVector = queryEmbedding.data[0].embedding;

    const matches = await matchEmbedding(queryVector, 0.75, 5);
    const contents = matches.map((match) => match.content).join("\n---\n");
    // console.log("Matches found:", matches);
    const reply = await getChatCompletions(contents, query);
    return reply;
  } catch (error) {
    console.error("Error during semantic search:", error);
  }
};

// await documentSemanticSearch(queryText);
