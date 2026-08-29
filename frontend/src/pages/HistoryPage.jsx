import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { History, MessageSquare, Calendar, Trash2, ArrowRight } from 'lucide-react';

export default function HistoryPage() {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await api.get('/chat/history');
      setConversations(res.data);
    } catch (err) {
      console.error('Failed to load chat history:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/chat/conversation/${id}`);
      setConversations((prev) => prev.filter((c) => c.id !== id));
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="flex items-center space-x-3 mb-8">
        <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
          <History className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Conversation History</h1>
          <p className="text-xs text-slate-400">View and resume your past college assistant conversations</p>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-16 text-slate-400 text-sm">Loading history...</div>
      ) : conversations.length === 0 ? (
        <div className="glass-card rounded-2xl p-12 text-center border border-slate-800">
          <MessageSquare className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-slate-200 mb-1">No Chat History Yet</h3>
          <p className="text-xs text-slate-400 mb-6">Start a conversation with the RAG assistant to see history here.</p>
          <button
            onClick={() => navigate('/chat')}
            className="px-6 py-2.5 rounded-xl gradient-btn text-white text-sm font-semibold shadow-lg shadow-blue-500/25"
          >
            Start New Chat
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {conversations.map((conv) => (
            <div
              key={conv.id}
              className="glass-card rounded-2xl p-5 border border-slate-800 hover:border-slate-700 transition flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs text-slate-400 flex items-center">
                    <Calendar className="w-3.5 h-3.5 mr-1 text-cyan-400" />
                    {new Date(conv.updated_at).toLocaleDateString()}
                  </span>
                  <button
                    onClick={() => handleDelete(conv.id)}
                    className="p-1 text-slate-500 hover:text-rose-400 transition"
                    title="Delete Conversation"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                <h3 className="font-semibold text-slate-100 text-base mb-2 line-clamp-2">
                  {conv.title}
                </h3>
              </div>

              <div className="pt-4 border-t border-slate-800/80 flex justify-end">
                <button
                  onClick={() => navigate('/chat')}
                  className="text-xs font-semibold text-blue-400 hover:text-blue-300 flex items-center space-x-1"
                >
                  <span>Resume Chat</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
