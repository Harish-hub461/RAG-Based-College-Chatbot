import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { 
  FileText, Upload, RefreshCw, Trash2, CheckCircle2, 
  AlertTriangle, FilePlus, Layers, Tag 
} from 'lucide-react';

const CATEGORIES = ["Admissions", "Hostel", "Scholarships", "Examinations", "Placements", "General"];

export default function AdminDocuments() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  // Upload Form State
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('Admissions');
  const [version, setVersion] = useState('1.0');
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const res = await api.get('/documents');
      setDocuments(res.data);
    } catch (err) {
      console.error('Failed to load documents:', err);
    } fontFinally: {
      setLoading(false);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file || !title.trim()) return;

    setUploading(true);
    setMessage(null);

    const formData = new FormData();
    formData.append('title', title.trim());
    formData.append('category', category);
    formData.append('version', version);
    formData.append('file', file);

    try {
      const res = await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setMessage({ type: 'success', text: `Successfully uploaded and indexed '${res.data.title}'!` });
      setTitle('');
      setFile(null);
      fetchDocuments();
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Document upload failed.' });
    } finally {
      setUploading(false);
    }
  };

  const handleReprocess = async (id) => {
    try {
      await api.post(`/documents/${id}/reprocess`);
      fetchDocuments();
    } catch (err) {
      console.error('Reprocess failed:', err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this document and all its embedded vectors?')) return;
    try {
      await api.delete(`/documents/${id}`);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
    } catch (err) {
      console.error('Delete failed:', err);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Knowledge Base Management</h1>
        <p className="text-xs text-slate-400">Upload official college documents (PDF, DOCX, TXT) to automatically chunk, embed, and index in ChromaDB</p>
      </div>

      {message && (
        <div className={`p-4 rounded-xl text-xs font-semibold flex items-center justify-between ${
          message.type === 'success'
            ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-400'
            : 'bg-rose-500/10 border border-rose-500/30 text-rose-400'
        }`}>
          <span>{message.text}</span>
          <button onClick={() => setMessage(null)} className="text-slate-400 hover:text-white">✕</button>
        </div>
      )}

      {/* Upload Document Form */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800 shadow-xl">
        <h3 className="font-bold text-slate-100 text-lg mb-4 flex items-center">
          <FilePlus className="w-5 h-5 mr-2 text-blue-400" />
          Upload & Index New Document
        </h3>

        <form onSubmit={handleUpload} className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Document Title</label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. B.Tech Fee Structure 2026"
              className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-xs text-slate-100 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-xs text-slate-100 focus:outline-none focus:border-blue-500"
            >
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Document File (PDF/DOCX/TXT)</label>
            <input
              type="file"
              required
              accept=".pdf,.docx,.txt"
              onChange={(e) => setFile(e.target.files[0])}
              className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2 text-xs text-slate-300 file:mr-3 file:py-1 file:px-2.5 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-blue-600/20 file:text-blue-400"
            />
          </div>

          <div className="md:col-span-3 flex justify-end">
            <button
              type="submit"
              disabled={uploading || !file || !title.trim()}
              className="py-2.5 px-6 gradient-btn text-white font-semibold text-xs rounded-xl flex items-center space-x-2 shadow-lg shadow-blue-500/25 disabled:opacity-50"
            >
              <Upload className="w-4 h-4" />
              <span>{uploading ? 'Processing & Embedding Vectors...' : 'Upload Document'}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Uploaded Documents List */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800">
        <h3 className="font-bold text-slate-100 text-lg mb-4 flex items-center justify-between">
          <span className="flex items-center">
            <FileText className="w-5 h-5 mr-2 text-cyan-400" />
            Indexed Knowledge Base Documents
          </span>
          <span className="text-xs font-semibold text-slate-400">Total: {documents.length}</span>
        </h3>

        {loading ? (
          <div className="text-center py-12 text-slate-400 text-sm">Loading document inventory...</div>
        ) : documents.length === 0 ? (
          <div className="text-center py-12 text-slate-500 text-xs">
            No documents uploaded yet.<br />Use the upload form above to add college documents.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                <tr>
                  <th className="p-3">Title & File</th>
                  <th className="p-3">Category</th>
                  <th className="p-3">Type</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Pages / Chunks</th>
                  <th className="p-3">Uploaded At</th>
                  <th className="p-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-800/40">
                    <td className="p-3">
                      <div className="font-semibold text-slate-100">{doc.title}</div>
                      <div className="text-[10px] text-slate-400">{doc.file_name}</div>
                    </td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                        {doc.category}
                      </span>
                    </td>
                    <td className="p-3 uppercase font-mono font-bold text-slate-400">{doc.file_type}</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                        doc.processing_status === 'completed'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : doc.processing_status === 'processing'
                            ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                            : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      }`}>
                        {doc.processing_status}
                      </span>
                    </td>
                    <td className="p-3 font-mono">
                      {doc.page_count} pages / {doc.chunk_count} chunks
                    </td>
                    <td className="p-3">{new Date(doc.created_at).toLocaleDateString()}</td>
                    <td className="p-3 text-right space-x-2">
                      <button
                        onClick={() => handleReprocess(doc.id)}
                        className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-blue-400 transition"
                        title="Re-process & Re-embed Document"
                      >
                        <RefreshCw className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleDelete(doc.id)}
                        className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-rose-400 transition"
                        title="Delete Document"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
}
