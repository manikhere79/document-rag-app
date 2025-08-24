# Simple Local Knowledgebase (RAG) Project

This project is a beginner-friendly, fully local knowledgebase application that demonstrates Retrieval-Augmented Generation (RAG) using only open-source tools and Docker Desktop on Windows. No external APIs (like ChatGPT or Google) are used—everything runs on your machine!

## What is RAG?
Retrieval-Augmented Generation (RAG) is a technique where an AI model answers questions by first retrieving relevant information from a database (vector database) and then generating a response using a language model. This is the foundation for many modern AI-powered search and Q&A systems.

---

## Project Structure

- **docker-compose.yml**: Orchestrates all services (LLM, vector DB, backend, frontend) with one command.
- **backend/**: Python FastAPI app that handles document upload, embedding, storage, and answering questions using RAG.
- **frontend/**: Simple React app for uploading documents and asking questions.

---

## Step-by-Step: How It Works

1. **Start All Services**
   - Docker Compose launches:
     - Ollama (local LLM)
     - Qdrant (vector database)
     - Backend (FastAPI)
     - Frontend (React)

2. **Upload a Document**
   - Use the web UI to upload a `.txt` file.
   - The backend splits the text into chunks, generates embeddings, and stores them in Qdrant.

3. **Ask a Question**
   - Enter a question in the web UI.
   - The backend embeds your question, searches Qdrant for relevant chunks, and sends the context + question to the LLM.
   - The LLM generates an answer using only your local data.

---

## How to Run (Step-by-Step)

1. **Install Prerequisites**
   - [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
   - [Git for Windows](https://git-scm.com/)
   - (Optional) [VS Code](https://code.visualstudio.com/)

2. **Clone This Repository**
   ```sh
   git clone <your-repo-url>
   cd document-rag
   ```

3. **Start All Services**
   ```sh
   docker compose up --build
   ```
   This will download images and start all containers. The first run may take several minutes.

4. **Access the App**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:8001](http://localhost:8001)

5. **Upload a Text File**
   - Use the web UI to upload a `.txt` file (e.g., notes, articles, etc.).

6. **Ask Questions**
   - Type your question in the input box and get answers based on your uploaded documents!

---

## Service Details

### 1. Ollama (LLM)
- Runs a local large language model (e.g., Llama2) for generating answers.
- No internet or external API required.

### 2. Qdrant (Vector Database)
- Stores document chunks as vectors for fast similarity search.
- Used to retrieve relevant context for each question.

### 3. Backend (FastAPI)
- Handles document upload, chunking, embedding, storage, and answering questions.
- Implements the RAG pattern.

### 4. Frontend (React)
- Simple web interface for uploading files and asking questions.
- Communicates with the backend API.

---

## For Beginners: What You Learn
- How to run a local LLM and vector DB with Docker
- How RAG works in practice
- How to build a simple AI-powered app end-to-end

---

## Troubleshooting
- If you see errors, make sure Docker Desktop is running and you have enough RAM (8GB+ recommended).
- The first run may be slow as models and dependencies are downloaded.

---

## Next Steps
- Try uploading your own notes or articles.
- Explore the backend code to see how RAG is implemented.
- Experiment with different LLMs or vector DBs.

---

Happy learning!
