import os
import tempfile
from typing import List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from langchain_community.document_loaders import PyPDFLoader

from .. import chat_store
from ..rag_chatbot import answer_query, load_chat_to_memory

router = APIRouter(prefix="/api/chats", tags=["chats"])

SCREEN_KEYWORDS = ["screen", "evaluate", "assess", "review", "match"]


def _to_api_role(role: str) -> str:
    return "assistant" if role == chat_store.ASSISTANT_ROLE else role


@router.get("")
def list_chats():
    chat_data = chat_store.load_chat_history()
    chats = [
        {"id": int(cid), "title": info["title"], "created_at": info["created_at"]}
        for cid, info in chat_data.items()
    ]
    chats.sort(key=lambda c: c["id"], reverse=True)
    return chats


@router.post("")
def new_chat():
    return chat_store.create_chat()


@router.delete("/{chat_id}")
def remove_chat(chat_id: int):
    if not chat_store.delete_chat(chat_id):
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"ok": True}


@router.get("/{chat_id}")
def get_chat(chat_id: int):
    chat = chat_store.get_chat(chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {
        "id": chat_id,
        "title": chat["title"],
        "messages": [
            {"role": _to_api_role(m["role"]), "content": m["content"], "timestamp": m["timestamp"]}
            for m in chat["messages"]
        ],
    }


@router.post("/{chat_id}/query")
async def query_chat(
    chat_id: int,
    message: str = Form(...),
    resumes: List[UploadFile] = File(default=[]),
):
    chat = chat_store.get_chat(chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Prime the shared conversation memory with this chat's prior turns,
    # exactly like Resume_Screener.py did when switching sessions.
    load_chat_to_memory(chat["messages"])

    backend_query = message
    temp_paths: List[str] = []
    lowered = message.lower()

    if resumes and any(k in lowered for k in SCREEN_KEYWORDS):
        resume_blocks = []
        for i, resume in enumerate(resumes):
            try:
                content = await resume.read()
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(content)
                    temp_paths.append(tmp.name)
                docs = PyPDFLoader(temp_paths[-1]).load()
                text = "\n\n".join(d.page_content for d in docs)
            except Exception as e:
                # A bad/corrupt/scanned-image PDF here used to crash the whole
                # endpoint with a raw 500, which is what "Failed to reach the
                # screening assistant" was actually masking. Fail loudly with
                # a message the frontend can show instead.
                for path in temp_paths:
                    if os.path.exists(path):
                        os.remove(path)
                raise HTTPException(
                    status_code=422,
                    detail=f"Couldn't read resume '{resume.filename}': {e}",
                )
            resume_blocks.append(f"Resume {i + 1}: {resume.filename}\n{text}")
        backend_query += "\n\nScreen the following resumes:\n" + "\n\n".join(resume_blocks)

    is_first_message = len(chat["messages"]) == 0
    chat_store.save_message(chat_id, "user", message)
    if is_first_message:
        chat_store.update_chat_title(chat_id, message)

    def generate():
        full_response = ""
        try:
            for chunk in answer_query(backend_query):
                full_response += chunk
                yield chunk
        finally:
            chat_store.save_message(chat_id, chat_store.ASSISTANT_ROLE, full_response)
            for path in temp_paths:
                if os.path.exists(path):
                    os.remove(path)

    return StreamingResponse(generate(), media_type="text/plain")
