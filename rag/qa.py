from rag.embedder import model, embed_texts
from rag.vectorstore import VectorStore
from rag.prompt import build_prompt
import openai

openai.api_key = "YOUR_API_KEY_HERE"

# 初始化向量库
store = VectorStore(dim=384)

def build_knowledge_base(texts):
    chunks = []
    for t in texts:
        chunks.extend(t)

    vectors = embed_texts(chunks)
    store.add(vectors, chunks)

def answer_question(question):
    q_vec = model.encode([question])[0]
    context = store.search(q_vec, top_k=3)
    prompt = build_prompt(question, context)

    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content
