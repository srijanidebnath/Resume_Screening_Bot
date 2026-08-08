import os
import tempfile
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile

from .. import vector_store

router = APIRouter(prefix="/api/vector-db", tags=["vector-db"])


@router.get("/docs")
def list_docs():
    ids = vector_store.list_all_index_ids()
    return [{"id": doc_id, "source": doc_id} for doc_id in ids]


@router.post("/docs")
async def add_docs(files: List[UploadFile] = File(...)):
    added = []
    for file in files:
        content = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            vector_store.add_pdf_to_db(tmp_path, doc_id=file.filename)
            added.append(file.filename)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    return {"added": added}


@router.post("/sync-folder")
def sync_folder():
    """Optional bulk-import fallback: index any PDFs sitting in a `pdfs/`
    folder in the backend directory that aren't indexed yet. The normal
    upload flow (POST /docs) never required this folder — this just exists
    for the "drop files in a folder" workflow alongside it."""
    return vector_store.sync_pdfs_folder("pdfs")


@router.delete("/docs/{doc_id}")
def delete_doc(doc_id: str):
    vector_store.delete_index_by_id(doc_id)
    return {"ok": True}


@router.put("/docs/{doc_id}")
async def replace_doc(doc_id: str, file: UploadFile = File(...)):
    content = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        vector_store.update_index(doc_id, tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    return {"ok": True}
