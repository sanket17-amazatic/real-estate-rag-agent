import express from "express";
import cors from "cors";
import { documentSemanticSearch } from "./documentSemanticSearch.js";

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());
app.use(express.static("."));

app.post("/api/search", async (req, res) => {
  try {
    const { question } = req.body;
    const response = await documentSemanticSearch(question);
    res.json({ content: response.content });
  } catch (error) {
    console.error("Error:", error.message);
    res.status(500).json({ error: "Something went wrong" });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
