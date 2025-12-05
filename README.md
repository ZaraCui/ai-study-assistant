## 🧠 AI Study Assistant

A personalized AI-powered study assistant that learns from your course notes and answers your questions using Retrieval-Augmented Generation (RAG).

## 🚀 Why This Project?

Unlike general chatbots, this tool answers specifically based on your own lecture notes, tutorials, and study materials.
Perfect for consolidating knowledge, preparing for exams, and generating personalized explanations.

## ✨ Features

📘 Load your own course notes (TXT/MD)
```markdown
# AI Study Assistant

A lightweight, personal study assistant that uses Retrieval-Augmented Generation (RAG) to answer questions using your own lecture notes and course materials.

## Overview

This project extracts text from `.pdf`, `.md`, and `.txt` notes, splits content into chunks, converts chunks to embeddings with `sentence-transformers`, stores embeddings in a FAISS index, and answers user questions by combining retrieved passages with an LLM.

Key goals:
- Provide answers grounded in your own materials (no hallucination from unrelated data)
- Make it easy to index course notes and query them via a simple HTTP API

## Features

- Load notes from local files (`.pdf`, `.md`, `.txt`)
- Text extraction and basic cleaning for PDFs
- Chunking with overlap to preserve context
- Embedding via `sentence-transformers` (`all-MiniLM-L6-v2`)
- Similarity search using FAISS
- Simple RAG pipeline that builds prompts from retrieved passages and queries an LLM
- FastAPI endpoint at `/ask?q=...` for querying

## Repository Layout

```
ai-study-assistant/
├─ app.py                 # FastAPI app and startup logic
├─ requirements.txt       # Python dependencies
├─ data/                  # Place your notes here
│  └─ notes/COMP2123/
├─ rag/                   # RAG pipeline modules
│  ├─ loader.py           # Load & clean files (pdf/text)
│  ├─ chunker.py          # Split text into chunks
│  ├─ embedder.py         # sentence-transformers wrapper
│  ├─ vectorstore.py      # FAISS wrapper with persistence
│  ├─ prompt.py           # Prompt template builder
│  └─ qa.py               # Build/load index and answer questions
└─ api/
   └─ ask.py              # /ask endpoint
```

## Quick Start

1. Create a virtual environment and activate it:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add notes:

Place `.pdf`, `.md`, or `.txt` files under `data/notes/COMP2123/` (or adjust paths accordingly).

4. (Optional) Build the FAISS index manually:

```bash
PYTHONPATH=/workspaces/ai-study-assistant python3 scripts/manage_index.py build
```

5. Run the API:

```bash
uvicorn app:app --reload
```

Then query:

```
http://127.0.0.1:8000/ask?q=your+question
```

## Index Management CLI

`scripts/manage_index.py` supports:

- `build` — build (or rebuild) the index from a notes folder
- `load` — load an existing index and print basic stats
- `status` — check if index files exist

Examples:

```bash
# Build index (default notes path: data/notes/COMP2123)
PYTHONPATH=/workspaces/ai-study-assistant python3 scripts/manage_index.py build

# Force-rebuild (delete existing files first)
PYTHONPATH=/workspaces/ai-study-assistant python3 scripts/manage_index.py build --force

# Load and inspect
PYTHONPATH=/workspaces/ai-study-assistant python3 scripts/manage_index.py load

# Check index file existence
PYTHONPATH=/workspaces/ai-study-assistant python3 scripts/manage_index.py status
```

Note: The first build downloads the `all-MiniLM-L6-v2` model and may take time.

## Security & Notes

- Set your OpenAI API key via environment variable: `export OPENAI_API_KEY="sk-..."`.
- Do not commit secrets into the repository.
- The FAISS index is persisted to `data/index/` by default; large files (e.g. `venv/`) are excluded via `.gitignore`.

## Contributing

Contributions are welcome — open an issue or PR for improvements.

## License

MIT License

```

## 🧰 Index Management CLI

The repository includes a small CLI to manage the FAISS index: `scripts/manage_index.py`.

- Build an index from your notes (default path: `data/notes/COMP2123`):

```bash
PYTHONPATH=/workspaces/ai-study-assistant python3 scripts/manage_index.py build
```

Optional flags:
- `--index-path` — path prefix for saved index files (default `data/index/comp2123`)
- `--force` — remove existing index files before building

- Load an existing index and print basic stats:

```bash
PYTHONPATH=/workspaces/ai-study-assistant python3 scripts/manage_index.py load
```

- Check whether index files exist:

```bash
PYTHONPATH=/workspaces/ai-study-assistant python3 scripts/manage_index.py status
```

Note: Building the index downloads the `all-MiniLM-L6-v2` sentence-transformers model the first time and may take a few minutes.

## 🤝 Contributing

This is a personal project but contributions and suggestions are welcome.

## 📄 License

MIT License
