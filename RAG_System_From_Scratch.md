# Build a RAG System From Scratch — Full Guide

A complete Retrieval-Augmented Generation system: ingest documents → embed →
store in a vector DB → retrieve → generate answers with an LLM → chat UI.

**Stack:** FastAPI (backend) · ChromaDB (vector store, free & local) ·
Gemini API (embeddings + generation — you already use this in LexiFlux) ·
React (frontend) · SQLite (chat history)

**What you'll have at the end:** a working chatbot that answers questions
using YOUR documents (your projects, notes, resume, a codebase — whatever
you point it at), running locally, deployable for free.

---

## 0. How RAG Actually Works (read this before coding)

```
Your docs → [CHUNK] → [EMBED] → [STORE in vector DB]
                                         ↑
User question → [EMBED question] → [SEARCH vector DB] → top-K similar chunks
                                         ↓
              [PROMPT: question + retrieved chunks] → LLM → Answer
```

Five moving parts, in order:
1. **Chunking** — split documents into small pieces (LLMs and embeddings work
   better on focused chunks, not whole documents).
2. **Embedding** — turn each chunk into a vector (a list of numbers
   representing its *meaning*). Similar meaning = similar vector.
3. **Vector store** — a database optimized for "find the vectors closest to
   this one" (semantic search, not keyword search).
4. **Retrieval** — embed the user's question, search the vector store for
   the most similar chunks.
5. **Generation** — hand the LLM the question + retrieved chunks, ask it to
   answer using only that context.

---

## 1. Project Structure

```
rag-system/
├── backend/
│   ├── main.py              # FastAPI app + routes
│   ├── ingest.py            # chunking + embedding + storing docs
│   ├── retrieve.py          # search logic
│   ├── generate.py          # LLM call with retrieved context
│   ├── db.py                # SQLite for chat history
│   ├── requirements.txt
│   └── data/                # put your source documents here (.txt, .md)
│       └── (your files)
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── Chat.jsx
│   │   └── main.jsx
│   ├── index.html
│   └── package.json
└── README.md
```

---

## 2. Backend Setup

### 2.1 Install dependencies

```bash
mkdir rag-system && cd rag-system
mkdir backend frontend
cd backend
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
```

`backend/requirements.txt`:
```txt
fastapi==0.115.0
uvicorn[standard]==0.30.6
chromadb==0.5.5
google-generativeai==0.8.3
python-dotenv==1.0.1
pydantic==2.9.2
```

```bash
pip install -r requirements.txt
```

### 2.2 Environment variables

`backend/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Get a free Gemini API key at https://aistudio.google.com/apikey — you've
already used the Gemini API in LexiFlux, so this should feel familiar.

---

## 3. Chunking + Embedding + Storing (`ingest.py`)

This is the pipeline that turns your raw documents into searchable vectors.

```python
# backend/ingest.py
import os
import glob
from dotenv import load_dotenv
import google.generativeai as genai
import chromadb

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ChromaDB: a free, local vector database. It persists to disk in ./chroma_db
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="documents")


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks.
    - chunk_size: max characters per chunk
    - overlap: characters shared between consecutive chunks, so an idea
      that spans a chunk boundary isn't lost entirely in either chunk.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return [c.strip() for c in chunks if c.strip()]


def embed_text(text: str) -> list[float]:
    """
    Turn a piece of text into a vector using Gemini's embedding model.
    This is what lets us do semantic (meaning-based) search later.
    """
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_document",  # optimized for documents being stored
    )
    return result["embedding"]


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
    # Drop your own docs into backend/data/ first — e.g. project READMEs,
    # your goals/experience .md files, notes, anything text-based.
    ingest_directory()
```

**Run it once to build your knowledge base:**
```bash
python ingest.py
```

---

## 4. Retrieval (`retrieve.py`)

```python
# backend/retrieve.py
from ingest import collection, embed_text
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def embed_query(question: str) -> list[float]:
    """
    Same embedding model as documents, but task_type differs slightly —
    this tells the model "this is a search query" vs "this is a document",
    which improves retrieval quality.
    """
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=question,
        task_type="retrieval_query",
    )
    return result["embedding"]


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
    for doc, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "text": doc,
            "source": meta["source"],
            "relevance": 1 - distance,  # convert distance to a similarity score
        })
    return chunks
```

**Why `top_k=4`?** Retrieve too few chunks and you miss context; too many and
you drown the LLM in irrelevant text (and waste tokens). 3-6 is a reasonable
starting range — tune based on your chunk size and how spread out relevant
info tends to be in your docs.

---

## 5. Generation (`generate.py`)

```python
# backend/generate.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
from retrieve import retrieve_chunks

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")  # fast + free-tier friendly


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
    response = model.generate_content(prompt)

    return {
        "answer": response.text,
        "sources": list({c["source"] for c in chunks}),  # unique source files used
    }
```

**The one line that matters most:** *"If the answer isn't in the context,
say you don't have that information — do not make things up."* Without this
instruction, LLMs will confidently answer from their general training
knowledge instead of your documents, which defeats the purpose of RAG.

---

## 6. Chat History Database (`db.py`)

```python
# backend/db.py
import sqlite3
from datetime import datetime

DB_PATH = "chat_history.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            sources TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_message(question: str, answer: str, sources: list[str]):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO messages (question, answer, sources, created_at) VALUES (?, ?, ?, ?)",
        (question, answer, ",".join(sources), datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def get_history(limit: int = 50) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM messages ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
```

---

## 7. FastAPI App (`main.py`)

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from generate import answer_question
from db import init_db, save_message, get_history

app = FastAPI(title="RAG System API")

# Allow your React frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default dev port
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


class Question(BaseModel):
    question: str


@app.post("/ask")
def ask(payload: Question):
    result = answer_question(payload.question)
    save_message(payload.question, result["answer"], result["sources"])
    return result


@app.get("/history")
def history():
    return get_history()


@app.get("/health")
def health():
    return {"status": "ok"}
```

**Run the backend:**
```bash
uvicorn main:app --reload --port 8000
```

Test it directly before building the frontend:
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What projects have I built?"}'
```

---

## 8. Frontend — React Chat UI

### 8.1 Setup

```bash
cd ../frontend
npm create vite@latest . -- --template react
npm install
```

### 8.2 `src/Chat.jsx`

```jsx
import { useState, useRef, useEffect } from "react";

const API_URL = "http://localhost:8000";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendQuestion() {
    if (!input.trim() || loading) return;

    const question = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data.answer, sources: data.sources },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Error reaching the server.", sources: [] },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendQuestion();
    }
  }

  return (
    <div style={styles.container}>
      <h2 style={styles.header}>RAG Chat</h2>

      <div style={styles.messages}>
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              ...styles.bubble,
              alignSelf: m.role === "user" ? "flex-end" : "flex-start",
              background: m.role === "user" ? "#5B5BFF" : "#f0f0f0",
              color: m.role === "user" ? "white" : "black",
            }}
          >
            <div>{m.text}</div>
            {m.sources && m.sources.length > 0 && (
              <div style={styles.sources}>
                Sources: {m.sources.join(", ")}
              </div>
            )}
          </div>
        ))}
        {loading && <div style={styles.loading}>Thinking...</div>}
        <div ref={bottomRef} />
      </div>

      <div style={styles.inputRow}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask something about your documents..."
          style={styles.textarea}
          rows={2}
        />
        <button onClick={sendQuestion} disabled={loading} style={styles.button}>
          Send
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: 700,
    margin: "0 auto",
    height: "100vh",
    display: "flex",
    flexDirection: "column",
    fontFamily: "system-ui, sans-serif",
    padding: 16,
  },
  header: { marginBottom: 8 },
  messages: {
    flex: 1,
    overflowY: "auto",
    display: "flex",
    flexDirection: "column",
    gap: 10,
    padding: 8,
  },
  bubble: {
    maxWidth: "75%",
    padding: "10px 14px",
    borderRadius: 12,
  },
  sources: { fontSize: 11, opacity: 0.6, marginTop: 6 },
  loading: { fontSize: 13, opacity: 0.6, fontStyle: "italic" },
  inputRow: { display: "flex", gap: 8, marginTop: 8 },
  textarea: {
    flex: 1,
    padding: 10,
    borderRadius: 8,
    border: "1px solid #ccc",
    resize: "none",
    fontFamily: "inherit",
  },
  button: {
    padding: "0 20px",
    borderRadius: 8,
    border: "none",
    background: "#5B5BFF",
    color: "white",
    fontWeight: 600,
    cursor: "pointer",
  },
};
```

### 8.3 `src/App.jsx`

```jsx
import Chat from "./Chat";

function App() {
  return <Chat />;
}

export default App;
```

**Run the frontend:**
```bash
npm run dev
```

Open `http://localhost:5173` — you now have a working chat UI talking to
your RAG backend.

---

## 9. End-to-End Test

1. Put a few `.md`/`.txt` files in `backend/data/` — start with the
   `Dhairya_Kumar_Experience.md` and `Dhairya_Goals_and_Work_Preferences.md`
   files from earlier. Real, meaningful test data.
2. `python ingest.py` — builds your vector database.
3. `uvicorn main:app --reload` — starts the backend.
4. `npm run dev` (in `frontend/`) — starts the chat UI.
5. Ask it: *"What has Dhairya built?"* or *"What internships is he looking
   for?"* — it should answer using your actual files, with sources cited.

---

## 10. How to Extend This (once the basics work)

Roughly in order of value:

1. **Better chunking** — split on paragraphs/headings instead of raw
   character counts, so chunks don't cut sentences in half.
2. **Streaming responses** — stream the LLM's answer token-by-token to the
   frontend instead of waiting for the full response (better UX).
3. **PDF/DOCX support** — add `pypdf` or `python-docx` to `ingest.py` so you
   can ingest more than just `.txt`/`.md`.
4. **Re-ranking** — after retrieving top_k chunks, use a second, more
   precise model to re-score and re-order them before generation.
5. **Conversation memory** — pass recent chat history into the prompt so
   follow-up questions ("what about the second one?") work.
6. **Deploy it** — backend on Render/Railway free tier, frontend on
   Cloudflare Pages (you already know this stack from LaunchFolio).

---

## 11. What This Teaches You (for interviews)

Be able to explain, in your own words, without notes:
- Why RAG beats just stuffing everything into one giant prompt (cost, token
  limits, and retrieval focuses the LLM on what's actually relevant)
- Why embeddings enable *semantic* search vs. keyword search (they capture
  meaning, so "car" and "automobile" land near each other in vector space)
- Why the "don't make things up" instruction in the prompt matters
- The tradeoff in `chunk_size` and `top_k` (too small/few = missing
  context; too large/many = noise and wasted tokens)

This is exactly the kind of system design conversation that comes up in the
AI-focused internship interviews you've been applying to (Dobbe AI,
Chopsticks AI, Shoppeal) — build it, then be ready to explain every piece.
