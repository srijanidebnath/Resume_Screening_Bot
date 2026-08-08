"""
Wraps the same Chroma logic as your original vector_db_operations.py, but as
plain functions with no import-time side effects — the original ran
add_pdfs_to_db("pdfs") automatically on import, which isn't safe once this
gets imported every time the FastAPI server (re)starts.
"""
import os
from langchain_chroma import Chroma
from langchain.docstore.document import Document
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_community.embeddings import HuggingFaceEmbeddings

PERSIST_DIRECTORY = "chroma_db"

_embedding_function = None
_vectorstore = None


def get_embedding_function():
    global _embedding_function
    if _embedding_function is None:
        _embedding_function = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    return _embedding_function


def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        os.makedirs(PERSIST_DIRECTORY, exist_ok=True)
        _vectorstore = Chroma(
            persist_directory=PERSIST_DIRECTORY,
            embedding_function=get_embedding_function(),
        )
    return _vectorstore


def list_all_index_ids():
    collection = get_vectorstore()._collection
    results = collection.get()
    return results["ids"]


def add_pdf_to_db(file_path: str, doc_id: str):
    """Loads one PDF, merges all pages into a single document, and indexes it
    under doc_id (matches the original add_pdfs_to_db behaviour, one file at a time)."""
    vectorstore = get_vectorstore()
    loader = PDFPlumberLoader(file_path)
    docs = loader.load()
    full_text = "\n".join(doc.page_content for doc in docs)
    merged_doc = Document(page_content=full_text, metadata={"source": doc_id})
    vectorstore.add_documents([merged_doc], ids=[doc_id])


def delete_index_by_id(doc_id: str):
    get_vectorstore().delete(ids=[doc_id])


def update_index(doc_id: str, new_pdf_path: str):
    vectorstore = get_vectorstore()
    vectorstore.delete(ids=[doc_id])
    loader = PDFPlumberLoader(new_pdf_path)
    docs = loader.load()
    full_text = "\n".join(doc.page_content for doc in docs)
    merged_doc = Document(page_content=full_text, metadata={"source": doc_id})
    vectorstore.add_documents([merged_doc], ids=[doc_id])


def sync_pdfs_folder(folder: str = "pdfs"):
    """Optional bulk-import: index every .pdf sitting in `folder` (relative to
    wherever the server process runs, i.e. the backend directory) that isn't
    already indexed, using the filename as the doc id — same convention as
    the API upload path. Skips ids already in the store rather than
    re-indexing them, so it's safe to call repeatedly (e.g. on startup, or
    from a manual "sync" button) without duplicating documents.

    This is a fallback alongside the upload API, not a replacement for it —
    add_pdf_to_db() below (used by the /vector-db/docs upload endpoint)
    works with no folder involved at all.
    """
    if not os.path.isdir(folder):
        # Nothing has ever created this folder for you (deliberately — we
        # don't want a "pdfs" directory magically appearing in random
        # working directories). Create it now so the sync becomes a normal
        # "found nothing yet" result instead of a 404 error.
        os.makedirs(folder, exist_ok=True)
        return {"added": [], "skipped": [], "note": f"Created '{folder}/' — drop PDFs in there and sync again"}

    existing_ids = set(list_all_index_ids())
    added, skipped = [], []
    for filename in sorted(os.listdir(folder)):
        if not filename.lower().endswith(".pdf"):
            continue
        if filename in existing_ids:
            skipped.append(filename)
            continue
        add_pdf_to_db(os.path.join(folder, filename), doc_id=filename)
        added.append(filename)

    return {"added": added, "skipped": skipped}
