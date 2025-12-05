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

3️⃣ Add your notes

Place .txt or .md files inside:

data/notes/

4️⃣ Run the API
uvicorn app:app --reload


Then open:

http://127.0.0.1:8000/ask?q=what+is+polymorphism

## 🧠 Example Use Cases

Generate explanations for complex concepts

Review course material

Prepare exam summaries

Create personalized practice questions

Build your own AI tutor

## 🛣️ Roadmap (Planned Features)
🔹 Phase 1 — MVP (current)

Basic RAG pipeline

Simple web API

🔹 Phase 2 — Advanced RAG

PDF → text support

Better chunking strategies

Multiple course indexing

🔹 Phase 3 — Frontend UI

Web dashboard

Chat-like interface

🔹 Phase 4 — Smart Extensions

Auto-generate quizzes

Auto-summarize notes

Study schedule suggestions

Memory-based personalized learning

## 🤝 Contributing

Currently a personal learning project, but PRs and suggestions are welcome.

## 📄 License

MIT License
