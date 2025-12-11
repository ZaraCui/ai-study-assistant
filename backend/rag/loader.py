import os
import re
import fitz  # PyMuPDF


def _clean_pdf_text(text: str) -> str:
    """
    Clean raw PDF text:
    - remove common headers/footers from USYD slides
    - collapse excessive newlines
    """
    # Remove "The University of Sydney Page X"
    text = re.sub(r"The University of Sydney Page \d+", "", text)
    # Remove big copyright warning blocks (very rough but ok)
    text = re.sub(r"Copyright Regulations 1969.*?notice\.", "", text, flags=re.DOTALL)
    # Collapse 3+ newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def pdf_to_text(path: str) -> str:
    """
    Extract text from a PDF using PyMuPDF.
    """
    doc = fitz.open(path)
    pages = []
    for page in doc:
        pages.append(page.get_text("text"))
    raw = "\n\n".join(pages)
    return _clean_pdf_text(raw)


def load_texts(folder_path: str):
    """
    Load all .txt, .md, and .pdf files under the given folder.
    Return a list of raw text strings.
    """
    texts = []
    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)
        if not os.path.isfile(full_path):
            continue
        print(f"Processing file: {filename}")  # Debug log
        if filename.lower().endswith(".pdf"):
            text = pdf_to_text(full_path)
            texts.append(text)
        elif filename.endswith(".txt") or filename.endswith(".md"):
            with open(full_path, "r", encoding="utf-8") as f:
                texts.append(f.read())
    print(f"Loaded {len(texts)} files.")  # Debug log
    return texts
