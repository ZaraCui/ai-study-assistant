from fastapi import APIRouter
from rag.qa import answer_question

router = APIRouter()

@router.get("/ask")
def ask(q: str):
    return {"answer": answer_question(q)}
