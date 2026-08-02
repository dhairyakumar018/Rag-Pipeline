# backend/retrieve.py
from ingest import collection
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def embed_query(question: str) -> list[float]:
    """
    Same embedding model as documents, but task_type differs slightly —
    this tells the model "this is a search query" vs "this is a document",
    which improves retrieval quality.
    """
    result = client.models.embed_content(
        model="gemini-embedding-2",
        contents=question,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    return result.embeddings[0].values


def retrieve_chunks(question: str, top_k: int = 4) -> list[dict]:
    """
    Embed the question, search ChromaDB for the top_k most similar chunks.
    Returns the chunks plus their source metadata.
    """
    query_embedding = embed_query(question)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    chunks = []
    if results and results.get("documents") and len(results["documents"]) > 0 and len(results["documents"][0]) > 0:
        for doc, meta, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            chunks.append({
                "text": doc,
                "source": meta["source"],
                "relevance": 1 - distance,
            })
    return chunks
