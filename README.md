## 🧠 AI Study Assistant

A personalized AI-powered study assistant that learns from your course notes and answers your questions using Retrieval-Augmented Generation (RAG).

## 🚀 Why This Project?

Unlike general chatbots, this tool answers specifically based on your own lecture notes, tutorials, and study materials.
Perfect for consolidating knowledge, preparing for exams, and generating personalized explanations.

## ✨ Features

📘 Load your own course notes (TXT/MD)

✂️ Automatically chunk text into semantic units

🧩 Generate embeddings using sentence-transformers

🔎 Search relevant chunks via FAISS similarity search

💬 Ask any question and get an answer grounded in your notes

🌐 FastAPI backend with a simple /ask?q=... endpoint

## 📁 Project Structure
ai-study-assistant/<br>
│ app.py<br>
│ config.py<br>
│ requirements.txt<br>
│<br>
├── data/<br>
│   └── notes/                 # Place your course notes here<br>
│<br>
├── rag/<br>
│   ├── loader.py              # Load and clean text files<br>
│   ├── chunker.py             # Split text into chunks<br>
│   ├── embedder.py            # Embedding model wrapper<br>
│   ├── vectorstore.py         # FAISS index + search<br>
│   ├── prompt.py              # Prompt template for LLM<br>
│   └── qa.py                  # Full RAG pipeline<br>
│<br>
└── api/<br>
    └── ask.py                 # /ask endpoint using FastAPI<br>

## 🧪 Quick Start
1️⃣ Create virtual environment
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

2️⃣ Install dependencies
pip install -r requirements.txt

```markdown
## 🧠 AI Study Assistant

A lightweight, personalized AI study assistant that uses your own course materials to answer questions via Retrieval-Augmented Generation (RAG).

## 🚀 Project Goal

This project is designed to provide precise answers grounded in your lecture notes, slides, and other study documents. It helps consolidate knowledge, prepare for exams, and create personalized explanations.

## ✨ Key Features

- Load notes from local files (`.txt`, `.md`, and `.pdf`)
- Chunk documents into semantic passages
- Generate sentence embeddings using `sentence-transformers`
- Perform similarity search with FAISS
- Build prompts from retrieved passages and query an LLM for grounded answers
- Expose a simple FastAPI endpoint `/ask?q=...` for querying

## 📁 Project Structure

ai-study-assistant/
│ app.py
│ config.py
│ requirements.txt
│
├── data/
│   └── notes/            # Put your course notes here
│
├── rag/
│   ├── loader.py         # Load and clean text/pdf files
│   ├── chunker.py        # Split text into chunks
│   ├── embedder.py       # Embedding model wrapper
│   ├── vectorstore.py    # FAISS index and search wrapper
│   ├── prompt.py         # Prompt template builder
│   └── qa.py             # RAG pipeline: build index and answer questions
│
└── api/
    └── ask.py            # FastAPI route for `/ask`

## 🧪 Quick Start

1) Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

2) Install dependencies

```bash
pip install -r requirements.txt
```

3) Add your notes

Place `.txt`, `.md`, or `.pdf` files under:

```
data/notes/
```

4) (Optional) Build the index manually

```bash
PYTHONPATH=/workspaces/ai-study-assistant python3 scripts/manage_index.py build
```

5) Run the API

```bash
uvicorn app:app --reload
```

Open the ask endpoint in your browser or via curl:

```
http://127.0.0.1:8000/ask?q=what+is+polymorphism
```

## 🧠 Example Use Cases

- Generate clear explanations for complex topics
- Review course materials
- Create exam summaries and practice questions
- Build a personal study tutor

## 🛣️ Roadmap

**Phase 1 — MVP (current)**

- Basic RAG pipeline
- Simple web API

**Phase 2 — Advanced RAG**

- Better PDF handling and text extraction
- Smarter chunking strategies
- Multi-course indexing and metadata support

**Phase 3 — Frontend UI**

- Web dashboard and chat-like interface

**Phase 4 — Smart Extensions**

- Auto-generate quizzes and summaries
- Learning schedule suggestions and memory-based personalization

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

``` 
