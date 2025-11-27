# Real Estate RAG Tool

A Retrieval-Augmented Generation (RAG) application for intelligent property search in Pune. This tool uses semantic search and AI to answer queries about real estate properties including new launches and resale properties.

## Overview

This application combines document embeddings, vector search, and OpenAI's language models to provide intelligent answers to property-related questions. It processes property data from text documents, creates semantic embeddings, and retrieves relevant information based on user queries.

## Architecture

The application consists of:

- **Frontend**: Simple HTML/CSS/JavaScript interface
- **Backend**: Node.js Express server handling AI operations
- **RAG Pipeline**: Document processing, embedding generation, and semantic search
- **Data Ingestion**: Document splitting and preprocessing pipeline

## File Structure and Purpose

### Core Files

#### `server.js`

Express.js server that acts as the backend API. It:

- Serves the static frontend files (HTML, CSS, JS)
- Exposes `/api/search` endpoint for processing user queries
- Handles communication with the RAG pipeline
- Manages error handling and responses

#### `index.html`

The main user interface featuring:

- Clean, modern design with Google Fonts
- Input form for property queries
- Display area for AI responses
- Material Symbols icons for visual elements

#### `index.css`

Stylesheet providing:

- Responsive layout and design
- Custom styling for form elements
- Typography and color scheme
- Visual feedback for user interactions

#### `index.js`

Frontend JavaScript that:

- Handles form submissions
- Sends queries to the backend API
- Displays loading states ("Thinking...")
- Shows AI responses to the user
- Manages error states

### RAG Pipeline Files

#### `splitDocument.js`

**Document ingestion and preprocessing module** - This is the first step in the RAG pipeline that:

- **Reads property data**: Fetches content from text files in the `documents/` folder
- **File path resolution**: Uses Node.js path utilities to locate files relative to the project structure
- **Document splitting**: Implements RecursiveCharacterTextSplitter from LangChain to break large documents into manageable chunks
- **Chunk configuration**:
  - `chunkSize: 300` - Each chunk contains approximately 300 characters
  - `chunkOverlap: 30` - 30 characters overlap between chunks to maintain context
- **Exports two main functions**:
  - `fetchContentFromFile(fileName)`: Reads and returns file content as a string
  - `splitContent(text)`: Splits text into Document objects ready for embedding
- **Default file**: Currently configured to process `ResaleProperty_MockData (1).txt`
- **Error handling**: Includes file existence checks and detailed error messages

**How it works in the pipeline**:

1. Called by `storeEmbeddings.js` to ingest property data
2. Reads raw text from property listing files
3. Splits text into semantic chunks preserving context
4. Returns Document objects with page content and metadata
5. These chunks are then converted to embeddings for vector search

#### `storeEmbeddings.js`

Embedding generation and storage module that:

- Imports split documents from `splitDocument.js`
- Creates vector embeddings using OpenAI's text-embedding model
- Stores embeddings in a vector database (MemoryVectorStore)
- Manages the vector store for semantic search
- Combines document splitting and embedding creation

#### `documentSemanticSearch.js`

The main RAG orchestrator that:

- Performs semantic similarity search on stored embeddings
- Retrieves top relevant document chunks for a query
- Constructs prompts with context from retrieved documents
- Calls OpenAI's chat model to generate natural language responses
- Returns formatted answers based on property data

### Configuration Files

#### `.env`

Environment variables file containing:

- `OPENAI_API_KEY`: Your OpenAI API key for embeddings and completions
- `SUPABASE_API_KEY`: Your Supabase API key
- `SUPABASE_URL`: Your Supabase project URL

#### `package.json`

Project dependencies and scripts including:

- Express for server
- OpenAI SDK for AI operations
- LangChain for RAG utilities
- Other Node.js dependencies

### Data Files

#### `documents/`

Folder containing property data files:

- `NewLaunches_MockData (1).txt`: New property launch information
- `ResaleProperty_MockData (1).txt`: Resale property listings
- Additional property data as needed

## Setup and Installation

### Prerequisites

- Node.js (v18 or higher)
- npm (comes with Node.js)
- OpenAI API key

### Installation Steps

1. **Clone or navigate to the project directory**

   ```bash
   cd <path to your folder>/real-estate-rag-agent/rag_with_js
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Set up environment variables**

   Create a `.env` file in the `rag_with_js` folder:

   ```bash
   touch .env
   ```

   Add your OpenAI and SUPABASE API key:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   SUPABASE_API_KEY=your_supabase_api_key_here
   SUPABASE_URL=https://rqqnngupcyarscsyfnpa.supabase.co
   ```

4. **Prepare your documents**

   Ensure your property data files are in the `documents/` folder:

   ```
   documents/
   ├── NewLaunches_MockData (1).txt
   └── ResaleProperty_MockData (1).txt
   ```

## Running the Application

### Step 1: Ingest and Process Documents (One-time setup)

Before starting the server, you need to process your property documents and create embeddings:

```bash
node storeEmbeddings.js
```

This script will:

1. Read property data from `documents/ResaleProperty_MockData (1).txt` (or configured file)
2. Split the document into chunks using `splitDocument.js`
3. Generate embeddings for each chunk using OpenAI
4. Store embeddings in memory for semantic search

**Note**: This step needs to be run whenever:

- You add new property documents
- You update existing property data
- You change chunk size/overlap settings

### Step 2: Start the Server

```bash
node server.js
```

You should see:

```
Server running on http://localhost:3000
```

### Step 3: Open the Application

Open your web browser and navigate to:

```
http://localhost:3000
```

Or directly open the `index.html` file in your browser (if the server is running).

### Step 4: Use the Application

1. Type your property-related question in the input field

   - Example: "What new launches are available in Pune?"
   - Example: "Show me 2BHK apartments under 80 lakhs"
   - Example: "What are the best areas for resale properties?"

2. Click the send button or press Enter

3. Wait for the AI response to appear

## Example Queries

- "What new property launches are available?"
- "Tell me about resale properties in Pune"
- "What is the price range for 2BHK apartments?"
- "Which areas have the best connectivity?"
- "What amenities are available in new launches?"

## Troubleshooting

### Port Already in Use

If port 3000 is busy, modify `server.js`:

```javascript
const PORT = 3001; // or any available port
```

### API Key Issues

Ensure your `.env` file is in the correct location and properly formatted.

### Module Not Found

Run `npm install` again to ensure all dependencies are installed.

### CORS Errors

The server includes CORS middleware. If issues persist, check browser console for specific errors.

## Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Node.js, Express.js
- **AI/ML**: OpenAI API (GPT models, Embeddings)
- **RAG Framework**: LangChain
- **Vector Store**: In-memory vector database

## Future Enhancements

- Add support for multiple document types (PDF, DOCX)
- Implement persistent vector storage
- Add conversation history
- Include property images
- Add filtering and sorting options
- Implement authentication
- Deploy to cloud platform

## Data Ingestion Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Property Data Files (documents/*.txt)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. splitDocument.js                                         │
│    - fetchContentFromFile() reads raw text                  │
│    - splitContent() chunks text (300 chars, 30 overlap)     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. storeEmbeddings.js                                       │
│    - Generates embeddings for each chunk                    │
│    - Stores in MemoryVectorStore                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. documentSemanticSearch.js                                │
│    - Performs similarity search on user queries             │
│    - Retrieves relevant chunks                              │
│    - Generates AI responses with context                    │
└─────────────────────────────────────────────────────────────┘
```

## Customizing Document Ingestion

To process different files or multiple files, modify `splitDocument.js`:

```javascript
// For a different file:
export async function fetchContentFromFile(
  fileName = "documents/NewLaunches_MockData (1).txt",
) {
  // ...existing code...
}

// For multiple files:
export async function fetchContentFromFile(
  fileNames = [
    "documents/ResaleProperty_MockData (1).txt",
    "documents/NewLaunches_MockData (1).txt",
  ],
) {
  let allContent = "";
  for (const fileName of fileNames) {
    const filePath = path.join(__dirname, "..", fileName);
    allContent += fs.readFileSync(filePath, "utf8") + "\n\n";
  }
  return allContent;
}
```

To adjust chunk sizes for better or worse granularity:

```javascript
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 500, // Larger chunks = more context, fewer chunks
  chunkOverlap: 50, // More overlap = better context preservation
});
```

## Contact

For questions or issues, please contact the development team.
