# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from generate import answer_question
from db import init_db, save_message, get_history

app = FastAPI(title="RAG System API")

# Allow React frontend (running on port 5173) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
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
