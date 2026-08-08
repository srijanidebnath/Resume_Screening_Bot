import { useRef } from "react";

export default function FileUploader({ files, onAdd, onRemove }) {
  const inputRef = useRef(null);

  return (
    <div className="upload-row">
      <button className="pill-btn" onClick={() => inputRef.current?.click()}>
        📎 Upload resumes
      </button>
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        multiple
        hidden
        onChange={(e) => {
          onAdd(Array.from(e.target.files || []));
          e.target.value = "";
        }}
      />
      {files.map((file, i) => (
        <span className="resume-chip" key={`${file.name}-${i}`}>
          <span className="dot" />
          {file.name}
          <button onClick={() => onRemove(i)}>✕</button>
        </span>
      ))}
    </div>
  );
}
