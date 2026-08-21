import { useState, useEffect, useRef } from "react";
import { getDocuments, uploadDocument, deleteDocument } from "../services/api";
import type { DocumentInfo } from "../types";

export default function Documents() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadDocuments = () => {
    setLoading(true);
    getDocuments()
      .then((res) => setDocuments(res.documents))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const handleUpload = async (file: File) => {
    setUploading(true);
    try {
      await uploadDocument(file);
      loadDocuments();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Upload failed";
      alert(message);
    } finally {
      setUploading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleUpload(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this document and all its chunks?")) return;
    try {
      await deleteDocument(id);
      loadDocuments();
    } catch {
      alert("Failed to delete document");
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h2>Documents</h2>
        <button
          className="btn btn-primary"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
        >
          {uploading ? "Uploading..." : "Upload Document"}
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,.md"
          onChange={handleFileChange}
          style={{ display: "none" }}
        />
      </div>

      <div
        className={`drop-zone ${dragActive ? "active" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
      >
        Drag and drop PDF, TXT, or Markdown files here
      </div>

      {loading ? (
        <div className="loading">Loading...</div>
      ) : documents.length === 0 ? (
        <div className="empty-state">No documents uploaded yet</div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Filename</th>
                <th>Chunks</th>
                <th>Uploaded</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((d) => (
                <tr key={d.id}>
                  <td>#{d.id}</td>
                  <td>{d.filename}</td>
                  <td>{d.chunk_count}</td>
                  <td>{new Date(d.created_at).toLocaleDateString()}</td>
                  <td>
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={() => handleDelete(d.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
