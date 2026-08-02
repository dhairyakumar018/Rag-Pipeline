# backend/ingest.py
import os
import glob
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

import chromadb
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="documents")


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return [c.strip() for c in chunks if c.strip()]


def embed_text(text: str) -> list[float]:
    result = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text,
    )
    return result.embeddings[0].values


def ingest_file(filepath: str):
    """Read one file, chunk it, embed each chunk, store in ChromaDB."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text)
    filename = os.path.basename(filepath)

    for i, chunk in enumerate(chunks):
        embedding = embed_text(chunk)
        chunk_id = f"{filename}-{i}"
        collection.add(
            ids=[chunk_id],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[{"source": filename, "chunk_index": i}],
        )
    print(f"Ingested {len(chunks)} chunks from {filename}")


def ingest_directory(data_dir: str = "./data"):
    """Ingest every .txt and .md file in the data directory."""
    files = glob.glob(f"{data_dir}/**/*.txt", recursive=True) + \
            glob.glob(f"{data_dir}/**/*.md", recursive=True)

    if not files:
        print(f"No .txt or .md files found in {data_dir}. Add some and rerun.")
        return

    for filepath in files:
        ingest_file(filepath)

    print(f"\nDone. Total chunks in collection: {collection.count()}")


if __name__ == "__main__":
    ingest_directory()
