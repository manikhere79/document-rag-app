import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from sentence_transformers import SentenceTransformer
import httpx

app = FastAPI()

# Allow frontend CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
COLLECTION_NAME = "docs"

qdrant = QdrantClient(QDRANT_URL)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Ensure collection exists
try:
    qdrant.get_collection(COLLECTION_NAME)
except Exception:
    qdrant.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    text = (await file.read()).decode("utf-8")
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    vectors = model.encode(chunks).tolist()
    points = [PointStruct(id=i, vector=v, payload={"text": c}) for i, (v, c) in enumerate(zip(vectors, chunks))]
    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    return {"status": "uploaded", "chunks": len(chunks)}

@app.post("/query")
async def query(question: str = Form(...)):
    q_vec = model.encode([question])[0].tolist()
    hits = qdrant.search(collection_name=COLLECTION_NAME, query_vector=q_vec, limit=3)
    context = "\n".join([hit.payload["text"] for hit in hits])
    prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{OLLAMA_URL}/api/generate", json={"model": "llama2", "prompt": prompt})
        answer = resp.json().get("response", "No answer.")
    return {"answer": answer, "context": context}

@app.get("/")
def root():
    return {"message": "Knowledgebase backend running."}
