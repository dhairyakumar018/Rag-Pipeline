# RAG System with Gemini

A Retrieval-Augmented Generation (RAG) application that allows you to chat with your documents. The system uses a FastAPI backend with ChromaDB for vector storage, Google's Generative AI (Gemini) for embeddings and text generation, and a modern React frontend powered by Vite.

## 🚀 Features

- **Document Ingestion:** Automatically reads and chunks `.txt` and `.md` files from a data directory.
- **Vector Search:** Embeds documents using Gemini (`gemini-embedding-2`) and stores them in a local ChromaDB instance for fast semantic retrieval.
- **Context-Aware Chat:** Retrieves the most relevant document chunks based on user queries and generates accurate answers using `gemini-3.5-flash`.
- **Modern Stack:** Fast backend with FastAPI and a responsive frontend built with React + Vite.

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI, Uvicorn
- **Vector Database:** ChromaDB
- **AI / LLM:** Google GenAI SDK (Gemini)
- **Frontend:** React, Vite

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- A Google Gemini API Key

## 🏗️ Getting Started

### 1. Backend Setup

Navigate to the backend directory and set up your Python environment:

```bash
cd backend
python -m venv venv
```

Activate the virtual environment:
- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

Install dependencies:
```bash
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory and add your Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Ingesting Data

Before starting the server, you need to populate the database. Place your `.txt` or `.md` files in the `backend/data` directory, then run the ingestion script:

```bash
python ingest.py
```
This will chunk your documents, generate embeddings, and save them to the local `chroma_db` folder.

### 3. Running the Application

**Start the Backend Server:**
Ensure your virtual environment is active, then run:
```bash
uvicorn main:app --reload --port 8000
```
The API will be available at `http://localhost:8000`.

**Start the Frontend Server:**
Open a new terminal, navigate to the frontend directory, and start the Vite development server:
```bash
cd frontend
npm install
npm run dev
```
The frontend will be available at `http://localhost:5173`.

## 📂 Project Structure

```
rag-system/
├── backend/
│   ├── data/               # Place your documents here
│   ├── chroma_db/          # Local vector database storage
│   ├── .env                # Environment variables (API Key)
│   ├── main.py             # FastAPI application entry point
│   ├── ingest.py           # Document chunking and embedding logic
│   ├── retrieve.py         # Vector search functionality
│   ├── generate.py         # LLM prompt generation and querying
│   └── requirements.txt    # Python dependencies
└── frontend/
    ├── src/                # React components and source code
    ├── package.json        # Node.js dependencies
    └── vite.config.js      # Vite configuration
```

## 📝 Notes

- Make sure your Python IDE interpreter is set to use the virtual environment (`backend/venv`) so that imports (like `google.genai`) resolve correctly.
- The ChromaDB database is stored locally. If you wish to reset your database, simply delete the `backend/chroma_db` folder and re-run `ingest.py`.
