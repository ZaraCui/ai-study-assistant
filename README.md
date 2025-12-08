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
- **Safe token handling** to prevent API overflow errors

Perfect for exam preparation and personalized studying.

---


## Features

- Load local notes (.pdf, .md, .txt)
- Extract and clean PDF text
- Chunk text with overlap
- Generate embeddings with all-MiniLM-L6-v2
- FAISS vector search for similarity lookup
- Full RAG pipeline with **token safety checks**
- **Comprehensive logging** for debugging
- **Configurable via environment variables** (NOTES_DIR, INDEX_PATH, DEFAULT_COURSE)
- **Multi-course support** — manage and query multiple courses independently
- FastAPI endpoints: `/ask?q=...&course=COURSE_CODE`, `/courses`, `/courses/{course_code}`
- Persistent index storage (auto-load on startup)
---

## Repository Layout

```
ai-study-assistant/
├─ app.py                    # FastAPI app with env var config
├─ requirements.txt
├─ data/
│  ├─ notes/COMP2123/       # Your notes go here
│  └─ index/                # Persisted FAISS indices
├─ rag/
│  ├─ loader.py             # Load & clean files
│  ├─ chunker.py            # Split text into chunks
│  ├─ embedder.py           # Embedding model wrapper
│  ├─ vectorstore.py        # FAISS with save/load
│  ├─ prompt.py             # Prompt builder
│  ├─ qa.py                 # RAG pipeline & QA
│  └─ token_manager.py      # Token counting & truncation
├─ api/
│  └─ ask.py                # /ask endpoint
└─ scripts/
   └─ manage_index.py       # CLI for index management
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

(Or change `NOTES_DIR` environment variable to use a different folder)

### 4. Build FAISS index (optional)

```bash
PYTHONPATH=/workspaces/ai-study-assistant python3 scripts/manage_index.py build
```

### 5. Run API

```bash
# Default configuration
uvicorn app:app --reload

# Or with custom paths:
NOTES_DIR=data/notes/YOUR_COURSE INDEX_PATH=data/index/your_course uvicorn app:app --reload
```

Query:

```
http://127.0.0.1:8000/ask?q=your+question
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NOTES_DIR` | `data/notes/COMP2123` | Path to folder containing your notes |
| `INDEX_PATH` | `data/index/comp2123` | Path prefix for persisted FAISS index |
| `OPENAI_API_KEY` | (required) | Your OpenAI API key |
| `DEFAULT_COURSE` | `COMP2123` | Default course to use when not specified |
| `NOTES_BASE_DIR` | `data/notes` | Base folder for all course notes |
| `INDEX_BASE_DIR` | `data/index` | Base folder for all course indexes |

---

## Testing

Recommended (CI-friendly): install the package into the environment so tests import the package naturally:

```bash
python -m pip install -e .
pytest -q
```

Alternatively, to run tests without installing, you can set `PYTHONPATH` (less preferred):

```bash
export PYTHONPATH=.
pytest -q
```

Install development tools:

```bash
pip install -r requirements-dev.txt
```

CI: Ensure your workflow runs `python -m pip install -e .` (or `pip install -e .`) before running `pytest`.


## Index Management CLI

### Build index

```bash
PYTHONPATH=/workspaces/ai-study-assistant python3 scripts/manage_index.py build
```

Options:
`--course <code>` — course code like 'COMP2123' (default: value of DEFAULT_COURSE env var)
`--notes <path>` — notes folder (default: data/notes/<course>)
`--index-path <path>` — index path prefix (default: data/index/<course>)
`--force` — delete existing files before rebuilding
- `--notes <path>` — notes folder (default: data/notes/COMP2123)
- `--index-path <path>` — index path prefix (default: data/index/comp2123)
- `--force` — delete existing files before rebuilding

### Load index

```bash
PYTHONPATH=/workspaces/ai-study-assistant python3 scripts/manage_index.py load
```

### Status

```bash
PYTHONPATH=/workspaces/ai-study-assistant python3 scripts/manage_index.py status
```

---

## Recent Improvements (v0.2)

✨ **Environment Variable Configuration**: Set `NOTES_DIR` and `INDEX_PATH` without editing code.

📊 **Comprehensive Logging**: Detailed INFO/DEBUG/ERROR logs at every step for troubleshooting.

🛡️ **Token Safety**: Automatic detection and truncation of large prompts to prevent API errors.

## Recent Improvements (v0.3)

✨ **Multi-Course Support**: Manage and query multiple courses independently with separate indexes.

📚 **Course Management**: New `/courses` API endpoints to list and inspect available courses.

🛠️ **Enhanced CLI**: Improved `manage_index.py` with course-aware commands and better status reporting.

💾 **Smart Caching**: Lazy-load course indexes on first query, automatic in-memory caching.

## Previous Improvements (v0.2)

✨ **Environment Variable Configuration**: Set `NOTES_DIR` and `INDEX_PATH` without editing code.

📊 **Comprehensive Logging**: Detailed INFO/DEBUG/ERROR logs at every step for troubleshooting.

🛡️ **Token Safety**: Automatic detection and truncation of large prompts to prevent API errors.
---

## Architecture

### RAG Pipeline

1. **Loader** (`rag/loader.py`)
   - Reads .pdf, .md, .txt files
   - Cleans and normalizes text

2. **Chunker** (`rag/chunker.py`)
   - Splits text into 500-word chunks with 50-word overlap

3. **Embedder** (`rag/embedder.py`)
   - Uses sentence-transformers to generate embeddings

4. **VectorStore** (`rag/vectorstore.py`)
   - Stores vectors in FAISS IndexFlatL2
   - Persists to disk via faiss.write_index + pickle

5. **QA** (`rag/qa.py`)
   - Encodes user question
   - Retrieves top-3 similar chunks
   - **Checks token safety** before sending to LLM
   - Builds prompt from chunks + question
   - Calls OpenAI Chat Completions

6. **Token Manager** (`rag/token_manager.py`)
   - Estimates token count (1 token ≈ 4 characters)
   - Truncates chunks to fit API limits
   - Prevents token overflow errors

---

## Configuration

### Logging Levels

Default is `INFO`. To see more details, set:

```bash
export PYTHONPATH=/workspaces/ai-study-assistant
python3 app.py  # Will show INFO logs
```

Or modify `rag/qa.py` and `app.py` to change `level=logging.INFO` to `level=logging.DEBUG`.

### Token Limits

Current settings in `rag/token_manager.py`:
- Model: `gpt-4o-mini` (128K context window)
- Context limit: 120K tokens (reserved 8K for response)
- Safe chunk truncation: 15K tokens if prompt exceeds limit

---

## Security & Notes

- **Never commit your API keys.** Use environment variables only.
- Large files (venv/, .pkl, .index) are in `.gitignore`.
- Index files are persisted but not tracked in git.

---

## Contributing

Contributions welcome! Please:

1. Test locally before opening a PR
2. Update README for new features
3. Follow existing code style (logging, error handling)

---

## License

MIT License

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Knowledge base is not initialized" | Run `scripts/manage_index.py build` first |
| "OpenAI auth failed" | Check `OPENAI_API_KEY` environment variable |
| "No chunks found" | Ensure `.pdf`, `.md`, `.txt` files are in `NOTES_DIR` |
| Token overflow | Automatic truncation is enabled; check logs for warnings |
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
