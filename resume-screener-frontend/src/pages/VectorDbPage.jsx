import { useEffect, useRef, useState } from "react";
import {
  listVectorDocs,
  addVectorDocs,
  deleteVectorDoc,
  updateVectorDoc,
  syncVectorDbFolder,
} from "../api.js";

export default function VectorDbPage() {
  const [backendOnline, setBackendOnline] = useState(true);
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState(null);
  const addInputRef = useRef(null);
  const updateInputRef = useRef(null);
  const [updateTargetId, setUpdateTargetId] = useState(null);
  const [syncMessage, setSyncMessage] = useState(null);
  const [syncing, setSyncing] = useState(false);

  async function refresh() {
    setLoading(true);
    try {
      const remote = await listVectorDocs();
      setBackendOnline(true);
      setDocs(remote);
    } catch {
      setBackendOnline(false);
      setDocs([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleAdd(files) {
    if (!files.length) return;
    if (!backendOnline) {
      setDocs((prev) => [
        ...prev,
        ...files.map((f) => ({ id: f.name, source: f.name, chunks: 1 })),
      ]);
      return;
    }
    setLoading(true);
    try {
      await addVectorDocs(files);
      await refresh();
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id) {
    setBusyId(id);
    try {
      if (backendOnline) await deleteVectorDoc(id);
      setDocs((prev) => prev.filter((d) => d.id !== id));
    } finally {
      setBusyId(null);
    }
  }

  async function handleUpdateFile(id, file) {
    if (!file) return;
    setBusyId(id);
    try {
      if (backendOnline) await updateVectorDoc(id, file);
      await refresh();
    } finally {
      setBusyId(null);
      setUpdateTargetId(null);
    }
  }

  async function handleSyncFolder() {
    setSyncing(true);
    setSyncMessage(null);
    try {
      const result = await syncVectorDbFolder();
      const parts = [];
      if (result.added?.length) parts.push(`indexed ${result.added.length} new PDF(s)`);
      if (result.skipped?.length) parts.push(`${result.skipped.length} already indexed`);
      setSyncMessage(parts.length ? parts.join(", ") : result.note || "No PDFs found in pdfs/ folder");
      await refresh();
    } catch (err) {
      setSyncMessage(err.message);
    } finally {
      setSyncing(false);
    }
  }

  return (
    <div className="vdb-page">
      <div className="vdb-header">
        <div>
          <h2 className="vdb-title">Job Description Index</h2>
          <p className="vdb-subtitle">
            Job description PDFs powering the RAG retriever. Add, replace, or
            remove entries — changes apply to the Chroma vector store.
          </p>
        </div>
        <div className="topbar-meta">
          {backendOnline ? "● connected" : "○ local preview — backend offline"}
        </div>
      </div>

      <div className="vdb-upload">
        <button className="pill-btn" onClick={() => addInputRef.current?.click()}>
          📥 Add job description PDFs
        </button>
        <button className="pill-btn" onClick={handleSyncFolder} disabled={syncing || !backendOnline}>
          {syncing ? "Syncing…" : "🔄 Sync pdfs/ folder"}
        </button>
        {syncMessage && <span className="vdb-sync-message">{syncMessage}</span>}
        <input
          ref={addInputRef}
          type="file"
          accept="application/pdf"
          multiple
          hidden
          onChange={(e) => {
            handleAdd(Array.from(e.target.files || []));
            e.target.value = "";
          }}
        />
        <input
          ref={updateInputRef}
          type="file"
          accept="application/pdf"
          hidden
          onChange={(e) => {
            const file = e.target.files?.[0];
            handleUpdateFile(updateTargetId, file);
            e.target.value = "";
          }}
        />
      </div>

      <div className="vdb-table">
        <div className="vdb-row vdb-row-head">
          <span>Document ID</span>
          <span>Source</span>
          <span></span>
        </div>

        {loading && <div className="vdb-empty">Loading index…</div>}

        {!loading && docs.length === 0 && (
          <div className="vdb-empty">
            No documents indexed yet. Add a job description PDF to get started.
          </div>
        )}

        {!loading &&
          docs.map((doc) => (
            <div className="vdb-row" key={doc.id}>
              <span className="vdb-id">{doc.id}</span>
              <span>{doc.source || doc.id}</span>
              <span className="vdb-actions">
                <button
                  className="pill-btn"
                  disabled={busyId === doc.id}
                  onClick={() => {
                    setUpdateTargetId(doc.id);
                    updateInputRef.current?.click();
                  }}
                >
                  ↻ Replace
                </button>
                <button
                  className="pill-btn danger"
                  disabled={busyId === doc.id}
                  onClick={() => handleDelete(doc.id)}
                >
                  🗑 Delete
                </button>
              </span>
            </div>
          ))}
      </div>
    </div>
  );
}
