import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";
import fs from "fs";
// Remove mammoth import as it's not needed for text files
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function fetchContentFromFile(
  fileName = "documents/ResaleProperty_MockData (1).txt",
) {
  try {
    const filePath = path.join(__dirname, "..", fileName);

    // Check if file exists
    if (!fs.existsSync(filePath)) {
      throw new Error(`File not found: ${filePath}`);
    }

    // Read the text file
    const content = fs.readFileSync(filePath, "utf8");

    return content;
  } catch (error) {
    console.error("Error reading text file:", error.message);
    throw error;
  }
}

export async function splitContent(text) {
  const splitter = new RecursiveCharacterTextSplitter({
    chunkSize: 300,
    chunkOverlap: 30,
  });

  const output = await splitter.createDocuments([text]);

  return output;
}
