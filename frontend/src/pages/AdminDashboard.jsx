import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { 
  FileText, Layers, MessageSquare, HelpCircle, AlertCircle, 
  TrendingUp, BarChart2, CheckCircle2, Clock 
} from 'lucide-react';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await api.get('/admin/dashboard');
      setStats(res.data);
    } catch (err) {
      console.error('Failed to load admin stats:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-16 text-slate-400 text-sm">Loading admin dashboard metrics...</div>;
  }

  if (!stats) return null;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Admin Title */}
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Administrator Control Center</h1>
        <p className="text-xs text-slate-400">Knowledge base analytics, document processing health, and query usage</p>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        
        <div className="glass-card p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400 font-semibold">Total Documents</span>
            <FileText className="w-5 h-5 text-blue-400" />
          </div>
          <div className="text-3xl font-extrabold text-slate-100">{stats.total_documents}</div>
          <p className="text-[10px] text-slate-500 mt-1">Uploaded & Indexed</p>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400 font-semibold">Vector Chunks</span>
            <Layers className="w-5 h-5 text-indigo-400" />
          </div>
          <div className="text-3xl font-extrabold text-slate-100">{stats.total_chunks}</div>
          <p className="text-[10px] text-slate-500 mt-1">Embedded Vectors</p>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400 font-semibold">Conversations</span>
            <MessageSquare className="w-5 h-5 text-cyan-400" />
          </div>
          <div className="text-3xl font-extrabold text-slate-100">{stats.total_conversations}</div>
          <p className="text-[10px] text-slate-500 mt-1">Student Chat Sessions</p>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400 font-semibold">Total Questions</span>
            <HelpCircle className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="text-3xl font-extrabold text-slate-100">{stats.total_questions}</div>
          <p className="text-[10px] text-slate-500 mt-1">RAG Queries Processed</p>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400 font-semibold">Unanswered</span>
            <AlertCircle className="w-5 h-5 text-amber-400" />
          </div>
          <div className="text-3xl font-extrabold text-amber-400">{stats.unanswered_questions_count}</div>
          <p className="text-[10px] text-slate-500 mt-1">Gaps in Knowledge Base</p>
        </div>

      </div>

      {/* Two-Column Analytics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Categories Breakdown */}
        <div className="glass-card p-6 rounded-2xl border border-slate-800">
          <h3 className="font-bold text-slate-100 text-lg mb-4 flex items-center">
            <BarChart2 className="w-5 h-5 mr-2 text-indigo-400" />
            Knowledge Base Categories
          </h3>
          {Object.keys(stats.categories_breakdown).length === 0 ? (
            <div className="text-xs text-slate-500 py-6 text-center">No categorized documents uploaded yet.</div>
          ) : (
            <div className="space-y-3">
              {Object.entries(stats.categories_breakdown).map(([cat, count]) => (
                <div key={cat} className="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span className="text-sm font-semibold text-slate-200">{cat}</span>
                  <span className="px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 text-xs font-bold">
                    {count} Document{count > 1 ? 's' : ''}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Frequently Asked Topics */}
        <div className="glass-card p-6 rounded-2xl border border-slate-800">
          <h3 className="font-bold text-slate-100 text-lg mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-cyan-400" />
            Top Student Queries
          </h3>
          {stats.frequently_asked_topics.length === 0 ? (
            <div className="text-xs text-slate-500 py-6 text-center">No queries logged yet.</div>
          ) : (
            <div className="space-y-3">
              {stats.frequently_asked_topics.map((t, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span className="text-xs font-medium text-slate-300 truncate max-w-xs">{t.question}</span>
                  <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 text-xs font-bold">
                    {t.count}x
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>

      {/* Recent Document Indexing Table */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800">
        <h3 className="font-bold text-slate-100 text-lg mb-4 flex items-center">
          <Clock className="w-5 h-5 mr-2 text-blue-400" />
          Recent Document Processing Logs
        </h3>

        {stats.recent_documents.length === 0 ? (
          <div className="text-xs text-slate-500 py-6 text-center">No recent uploads found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                <tr>
                  <th className="p-3">Document Title</th>
                  <th className="p-3">Category</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Chunks</th>
                  <th className="p-3">Uploaded Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {stats.recent_documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-800/40">
                    <td className="p-3 font-semibold text-slate-100">{doc.title}</td>
                    <td className="p-3">{doc.category}</td>
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
                    <td className="p-3 font-mono">{doc.chunk_count}</td>
                    <td className="p-3">{new Date(doc.created_at).toLocaleDateString()}</td>
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
