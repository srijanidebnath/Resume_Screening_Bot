import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()  # reads .env before anything (rag_chatbot, vector_store) needs the keys

from .routers import chats, vector_db, feedback  # noqa: E402  (import after load_dotenv on purpose)

app = FastAPI(title="Resume Screener API")
frontend_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chats.router)
app.include_router(vector_db.router)
app.include_router(feedback.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
