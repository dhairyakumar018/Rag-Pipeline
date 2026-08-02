# backend/generate.py
import os
from google import genai
from dotenv import load_dotenv
from retrieve import retrieve_chunks

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def build_prompt(question: str, chunks: list[dict]) -> str:
    """
    Stuff the retrieved chunks into a prompt template. This is the
    'augmented' part of Retrieval-Augmented Generation.
    """
    context = "\n\n".join(
        f"[Source: {c['source']}]\n{c['text']}" for c in chunks
    )

    return f"""You are a helpful assistant answering questions using ONLY the
context provided below. If the answer isn't in the context, say you don't
have that information — do not make things up.

Context:
{context}

Question: {question}

Answer (cite which source(s) you used):"""


def answer_question(question: str) -> dict:
    chunks = retrieve_chunks(question, top_k=4)

    if not chunks:
        return {"answer": "I don't have any relevant information for that.", "sources": []}

    prompt = build_prompt(question, chunks)
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    return {
        "answer": response.text,
        "sources": list({c["source"] for c in chunks}),
    }
