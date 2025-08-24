
# Standard library imports
import os
# FastAPI imports for API creation and file handling
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
# Qdrant client for vector database operations
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
# SentenceTransformer for text embedding
from sentence_transformers import SentenceTransformer
# HTTP libraries for making requests to Ollama
import httpx
import requests


# Initialize FastAPI app
app = FastAPI()

# Allow frontend CORS (so frontend can call backend from another port)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Configuration: URLs for Qdrant and Ollama, and collection name
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
COLLECTION_NAME = "docs"


# Initialize Qdrant client and embedding model
qdrant = QdrantClient(QDRANT_URL)
model = SentenceTransformer("all-MiniLM-L6-v2")


# Ensure the Qdrant collection exists (create if not)
try:
    qdrant.get_collection(COLLECTION_NAME)
except Exception:
    qdrant.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )


# Endpoint: Upload a text file, split into chunks, embed, and store in Qdrant
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    # Read and decode file
    text = (await file.read()).decode("utf-8")
    # Split text into 500-character chunks
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    # Generate embeddings for each chunk
    vectors = model.encode(chunks).tolist()
    # Prepare points for Qdrant
    points = [PointStruct(id=i, vector=v, payload={"text": c}) for i, (v, c) in enumerate(zip(vectors, chunks))]
    # Upsert points into Qdrant collection
    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    return {"status": "uploaded", "chunks": len(chunks)}


# Endpoint: Ask a question, retrieve relevant context, and generate answer using LLM
@app.post("/query")
async def query(question: str = Form(...)):
    try:
        import json
        # Embed the question
        q_vec = model.encode([question])[0].tolist()
        # Search Qdrant for top-3 relevant chunks
        hits = qdrant.search(collection_name=COLLECTION_NAME, query_vector=q_vec, limit=3)
        # Combine retrieved chunks as context
        context = "\n".join([hit.payload["text"] for hit in hits])
        # Build prompt for LLM
        prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"

        # Call Ollama LLM API (streaming NDJSON)
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": "llama3", "prompt": prompt},
            stream=True
        )
        response.raise_for_status()
        answer = ""
        # Parse each line of NDJSON and concatenate 'response' fields
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "response" in data:
                    answer += data["response"]

        return {"answer": answer, "context": context}
    except Exception as e:
        # Return error message if anything fails
        return {"error": str(e)}


# Health check endpoint
@app.get("/")
def root():
    return {"message": "Knowledgebase backend running."}
