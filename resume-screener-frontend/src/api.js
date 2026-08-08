// Thin API client for the FastAPI backend you'll build next.
// All calls go through /api, which vite.config.js proxies to http://localhost:8000
// so you never have to deal with CORS in dev.
//
// Suggested FastAPI routes to implement (matches what this file calls):
//   GET    /api/chats                 -> { id, title, created_at }[]
//   POST   /api/chats                 -> { id, title, created_at }
//   DELETE /api/chats/{chat_id}       -> { ok: true }
//   GET    /api/chats/{chat_id}       -> { id, title, messages: [...] }
//   POST   /api/chats/{chat_id}/query -> streams plain text chunks (StreamingResponse)
//          body: multipart/form-data with fields: message, resumes (files, optional)
//   POST   /api/feedback              -> { ok: true }
//
//   Vector DB management (wraps vector_db_operations.py):
//   GET    /api/vector-db/docs             -> { id, source, chunks }[]  (from list_all_index_ids)
//   POST   /api/vector-db/docs             -> multipart/form-data, field "files" (PDFs) -> add_pdfs_to_db
//   DELETE /api/vector-db/docs/{doc_id}    -> delete_index_by_id(doc_id)
//   PUT    /api/vector-db/docs/{doc_id}    -> multipart/form-data, field "file" -> update_index(doc_id, path)

const BASE = import.meta.env.VITE_API_BASE_URL || "/api";

export async function listChats() {
  const res = await fetch(`${BASE}/chats`);
  if (!res.ok) throw new Error("Failed to load chats");
  return res.json();
}

export async function createChat() {
  const res = await fetch(`${BASE}/chats`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to create chat");
  return res.json();
}

export async function deleteChat(chatId) {
  const res = await fetch(`${BASE}/chats/${chatId}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete chat");
  return res.json();
}

export async function getChat(chatId) {
  const res = await fetch(`${BASE}/chats/${chatId}`);
  if (!res.ok) throw new Error("Failed to load chat");
  return res.json();
}

export async function submitFeedback({ sessionId, messageIndex, question, rating }) {
  const res = await fetch(`${BASE}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      message_index: messageIndex,
      question,
      rating,
    }),
  });
  if (!res.ok) throw new Error("Failed to submit feedback");
  return res.json();
}

// Streams the assistant's reply chunk by chunk, calling onChunk(text) as
// data arrives. Mirrors RAG_chatbot.answer_query's generator, just over HTTP.
export async function streamQuery({ chatId, message, resumeFiles = [], onChunk, signal }) {
  const formData = new FormData();
  formData.append("message", message);
  resumeFiles.forEach((file) => formData.append("resumes", file));

  let res;
  try {
    res = await fetch(`${BASE}/chats/${chatId}/query`, {
      method: "POST",
      body: formData,
      signal,
    });
  } catch (networkErr) {
    // fetch() only throws for things like the backend being down entirely,
    // DNS/connection failures, or a CORS rejection.
    throw new Error(
      `Can't reach the backend at all (is FastAPI running on :8000?): ${networkErr.message}`
    );
  }

  if (!res.ok) {
    // Surface *why* it failed instead of a generic message. FastAPI error
    // bodies are JSON ({"detail": "..."}); fall back to raw text otherwise.
    let detail = "";
    try {
      const text = await res.text();
      try {
        detail = JSON.parse(text).detail ?? text;
      } catch {
        detail = text;
      }
    } catch {
      // body unreadable, fall through with just the status
    }
    throw new Error(
      `Screening assistant returned ${res.status} ${res.statusText}${detail ? ` — ${detail}` : ""}`
    );
  }

  if (!res.body) {
    throw new Error("Screening assistant returned an empty response body");
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let full = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const text = decoder.decode(value, { stream: true });
    full += text;
    onChunk(text, full);
  }

  return full;
}

// ---- Vector DB management ----

export async function listVectorDocs() {
  const res = await fetch(`${BASE}/vector-db/docs`);
  if (!res.ok) throw new Error("Failed to load vector store index");
  return res.json();
}

export async function addVectorDocs(files) {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));
  const res = await fetch(`${BASE}/vector-db/docs`, { method: "POST", body: formData });
  if (!res.ok) throw new Error("Failed to add document(s)");
  return res.json();
}

export async function deleteVectorDoc(docId) {
  const res = await fetch(`${BASE}/vector-db/docs/${encodeURIComponent(docId)}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete document");
  return res.json();
}

// Optional fallback: bulk-index any PDFs already sitting in a pdfs/ folder
// in the backend directory. The normal drag-and-drop upload above never
// needed this folder — it's just an alternate way in.
export async function syncVectorDbFolder() {
  const res = await fetch(`${BASE}/vector-db/sync-folder`, { method: "POST" });
  if (!res.ok) {
    let detail = "";
    try {
      detail = (await res.json()).detail ?? "";
    } catch {
      // ignore, fall back to generic message below
    }
    throw new Error(detail || `Failed to sync pdfs/ folder (${res.status})`);
  }
  return res.json();
}

export async function updateVectorDoc(docId, file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${BASE}/vector-db/docs/${encodeURIComponent(docId)}`, {
    method: "PUT",
    body: formData,
  });
  if (!res.ok) throw new Error("Failed to update document");
  return res.json();
}
