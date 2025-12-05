# AI Study Assistant

A lightweight study assistant that uses Retrieval-Augmented Generation (RAG) to answer questions using your own lecture notes and course materials.

---

## Why This Project?

Most chatbots answer using generic internet knowledge. This assistant answers using *your* materials by:

- Reading your notes
- Splitting them into chunks
- Embedding them using sentence-transformers
- Storing embeddings in a FAISS index
- Retrieving relevant chunks when you ask a question
- Using an LLM to answer based on retrieved context

Perfect for exam preparation and personalized studying.

---

## Features

- Load local notes (.pdf, .md, .txt)
- Extract and clean PDF text
- Chunk text with overlap
- Generate embeddings with all-MiniLM-L6-v2
- FAISS vector search for similarity lookup
- Full RAG pipeline
- FastAPI endpoint `/ask?q=...`

---

## Repository Layout

```
ai-study-assistant/
├─ app.py
├─ requirements.txt
├─ data/
│  └─ notes/COMP2123/
├─ rag/
│  ├─ loader.py
│  ├─ chunker.py
│  ├─ embedder.py
│  ├─ vectorstore.py
│  ├─ prompt.py
│  └─ qa.py
└─ api/
   └─ ask.py
```

---

## Quick Start

### 1. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

```powershell
python -m venv venv
venv\Scripts\Activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add notes

Place files under:

```
data/notes/COMP2123/
```

### 4. Build FAISS index (optional)

```bash
PYTHONPATH=/workspaces/ai-study-assistant python3 scripts/manage_index.py build
```

### 5. Run API

```bash
uvicorn app:app --reload
```

Query:

```
http://127.0.0.1:8000/ask?q=your+question
```

---

## Index Management CLI

### Build index

```bash
PYTHONPATH=/workspaces/ai-study-assistant python3 scripts/manage_index.py build
```

### Load index

```bash
PYTHONPATH=/workspaces/ai-study-assistant python3 scripts/manage_index.py load
```

### Status

```bash
PYTHONPATH=/workspaces/ai-study-assistant python3 scripts/manage_index.py status
```

---

## Security

Set API key:

```bash
export OPENAI_API_KEY="sk-..."
```

Do not commit keys or index files.

---

## License

MIT License
