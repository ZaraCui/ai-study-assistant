from fastapi import FastAPI
from api.ask import router as ask_router

app = FastAPI()
app.include_router(ask_router)

@app.get("/health")
def health():
    return {"status": "ok"}
