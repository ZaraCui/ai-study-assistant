import os
import logging
from functools import lru_cache
import fitz  # PyMuPDF

from .vectorstore import VectorStore
from .loader import load_texts

logger = logging.getLogger(__name__)

# -------------------------------------------------------
# Load persisted FAISS + text chunks
# -------------------------------------------------------
def load_persisted_vectorstore(index_dir: str) -> VectorStore:
    vs = VectorStore(index_dir)
    vs.load()  # load FAISS + pkl
    logger.info(f"[VectorStore] Loaded {len(vs.text_chunks)} text chunks.")
    return vs


# -------------------------------------------------------
# Cached global accessor
# -------------------------------------------------------
@lru_cache(maxsize=1)
def get_vectorstore(notes_path: str, index_path: str) -> VectorStore:

    logger.info("Initializing knowledge base for COMP2123")
    logger.info(f"Notes dir: {notes_path}")
    logger.info(f"Index path: {index_path}")

    index_file = index_path + ".index"
    text_file = index_path + "_texts.pkl"

    if not (os.path.exists(index_file) and os.path.exists(text_file)):
        raise RuntimeError(
            f"❌ Precomputed index missing at {index_path}. "
            f"Run scripts/build_index.py locally and commit the files."
        )

    return load_persisted_vectorstore(index_path)


# -------------------------------------------------------
# ONLY search, NO embedding, NO LLM
# -------------------------------------------------------
def answer_question(question: str, course: str = None):
    notes_dir = os.getenv("NOTES_DIR", "backend/data/notes/COMP2123")
    index_dir = os.getenv("INDEX_PATH", "backend/data/index/comp2123")

    vs = get_vectorstore(notes_dir, index_dir)

    results = vs.search(question, top_k=5)

    response_text = "\n\n".join([r["text"] for r in results])
    return response_text


# -------------------------------------------------------
# On startup, only load index and process PDF files if needed
# -------------------------------------------------------
def build_knowledge_base_from_dir(notes_path: str, index_path: str):
    logger.info("Attempting to load persisted index...")

    try:
        _ = load_persisted_vectorstore(index_path)
        logger.info("Successfully loaded precomputed index.")
    except Exception as e:
        logger.error(f"Failed loading persisted index: {e}")
        raise

    # 如果没有找到已存在的索引，尝试加载 PDF 文件并创建新的索引
    try:
        # 遍历目录，加载所有 PDF 文件
        pdf_files = [f for f in os.listdir(notes_path) if f.endswith(".pdf")]
        for pdf_file in pdf_files:
            pdf_path = os.path.join(notes_path, pdf_file)
            logger.info(f"Processing PDF file: {pdf_path}")

            # 读取 PDF 内容
            doc = fitz.open(pdf_path)
            full_text = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                full_text += page.get_text("text")  # 获取页面的文本内容

            # 将读取的 PDF 文本添加到索引中（假设有 add_to_index 方法）
            logger.info(f"Extracted text from {pdf_file}")
            # 您可以将文本添加到现有的索引或数据库中，按需修改
            # add_to_index(full_text)

    except Exception as e:
        logger.error(f"Failed processing PDF files: {e}")
        raise

    return True
