import React, { useState, useEffect, useRef } from 'react';
import Sidebar from '../components/Sidebar';
import SourceCard from '../components/SourceCard';
import FeedbackModal from '../components/FeedbackModal';
import api from '../services/api';
import { 
  Send, Bot, User, Sparkles, Filter, AlertTriangle, 
  ThumbsUp, ThumbsDown, HelpCircle, RefreshCw 
} from 'lucide-react';

const SUGGESTED_QUESTIONS = [
  "What is the fee for CSE?",
  "What are the hostel fees?",
  "What scholarships are available?",
  "When do semester exams begin?",
  "Tell me about placement eligibility.",
  "What are the library working hours?"
];

const CATEGORIES = ["All", "Admissions", "Hostel", "Scholarships", "Examinations", "General"];

export default function ChatPage() {
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputQuestion, setInputQuestion] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [loading, setLoading] = useState(false);
  const [feedbackMessageId, setFeedbackMessageId] = useState(null);
  const [feedbackRating, setFeedbackRating] = useState(1);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (activeConversationId) {
      fetchConversation(activeConversationId);
    } else {
      setMessages([]);
    }
  }, [activeConversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchConversations = async () => {
    try {
      const res = await api.get('/chat/history');
      setConversations(res.data);
    } catch (err) {
      console.error('Failed to load chat history:', err);
    }
  };

  const fetchConversation = async (id) => {
    try {
      const res = await api.get(`/chat/conversation/${id}`);
      setMessages(res.data.messages || []);
    } catch (err) {
      console.error('Failed to load conversation details:', err);
    }
  };

  const handleNewChat = () => {
    setActiveConversationId(null);
    setMessages([]);
    setInputQuestion('');
  };

  const handleDeleteConversation = async (id) => {
    try {
      await api.delete(`/chat/conversation/${id}`);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeConversationId === id) {
        handleNewChat();
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  };

  const handleSendQuestion = async (qText = null) => {
    const query = qText || inputQuestion.trim();
    if (!query || loading) return;

    setInputQuestion('');
    setLoading(true);

    // Optimistically insert user message
    const tempUserMsg = {
      id: Date.now(),
      sender: 'user',
      message_text: query,
      created_at: new Date().toISOString()
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const res = await api.post('/chat/ask', {
        conversation_id: activeConversationId,
        question: query,
        category_filter: categoryFilter === 'All' ? null : categoryFilter
      });

      const aiMsg = res.data;

      if (!activeConversationId) {
        setActiveConversationId(aiMsg.conversation_id);
        fetchConversations();
      }

      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      console.error('Error querying RAG assistant:', err);
      const errorMsg = {
        id: Date.now() + 1,
        sender: 'ai',
        message_text: 'Sorry, an error occurred while searching the knowledge base. Please check backend connection and try again.',
        sources: [],
        is_unanswered: true,
        created_at: new Date().toISOString()
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col md:flex-row gap-4 h-[calc(100vh-5rem)]">
      
      {/* Sidebar Navigation */}
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={setActiveConversationId}
        onNewChat={handleNewChat}
        onDeleteConversation={handleDeleteConversation}
      />

      {/* Main Chat Workspace */}
      <main className="flex-1 glass-card rounded-2xl p-4 flex flex-col justify-between h-[calc(100vh-6rem)] overflow-hidden">
        
        {/* Workspace Top Toolbar */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800 shrink-0">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <h2 className="font-bold text-slate-100 text-sm">College RAG Assistant</h2>
              <p className="text-[10px] text-emerald-400 flex items-center">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1 animate-pulse" />
                Live Document Knowledge Base Connected
              </p>
            </div>
          </div>

          {/* Category Filter Selector */}
          <div className="flex items-center space-x-2">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="bg-slate-900 border border-slate-700/80 rounded-lg px-2.5 py-1 text-xs text-slate-300 focus:outline-none focus:border-blue-500"
            >
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>Filter: {cat}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Message Stream Area */}
        <div className="flex-1 overflow-y-auto py-4 space-y-6 px-1">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-6 max-w-lg mx-auto">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-600/20 to-cyan-500/20 border border-blue-500/30 flex items-center justify-center text-blue-400 mb-4 shadow-xl">
                <Sparkles className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold text-slate-100 mb-2">How can I help you today?</h3>
              <p className="text-xs text-slate-400 mb-6 leading-relaxed">
                Ask questions regarding admissions, CSE fees, hostel policies, library timings, scholarships, and placement rules.
              </p>

              {/* Suggested Questions Grid */}
              <div className="w-full text-left">
                <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center">
                  <HelpCircle className="w-3.5 h-3.5 mr-1 text-blue-400" />
                  Suggested Questions
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {SUGGESTED_QUESTIONS.map((sq, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSendQuestion(sq)}
                      className="p-2.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-left text-xs text-slate-300 transition"
                    >
                      {sq}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.sender === 'ai' && (
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shrink-0 mt-1 shadow-md">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div className={`max-w-2xl rounded-2xl p-4 space-y-3 ${
                  msg.sender === 'user'
                    ? 'bg-blue-600 text-white rounded-tr-none shadow-lg shadow-blue-600/10'
                    : msg.is_unanswered
                      ? 'bg-slate-900/90 border border-amber-500/40 text-amber-200 rounded-tl-none'
                      : 'bg-slate-900/90 border border-slate-800 text-slate-100 rounded-tl-none'
                }`}>
                  
                  {/* Message Content */}
                  <div className="text-sm whitespace-pre-wrap leading-relaxed">
                    {msg.message_text}
                  </div>

                  {/* Warning banner for unanswered questions */}
                  {msg.is_unanswered && msg.sender === 'ai' && (
                    <div className="flex items-center space-x-2 text-xs text-amber-400 bg-amber-500/10 p-2.5 rounded-xl border border-amber-500/20">
                      <AlertTriangle className="w-4 h-4 shrink-0" />
                      <span>Information unavailable in indexed college documents.</span>
                    </div>
                  )}

                  {/* Sources Cards Display */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="pt-2 border-t border-slate-800/80 space-y-2">
                      <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider flex items-center">
                        <Sparkles className="w-3 h-3 mr-1 text-cyan-400" />
                        Verified Source References ({msg.sources.length})
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {msg.sources.map((src, idx) => (
                          <SourceCard key={idx} source={src} index={idx} />
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Message Actions (Feedback buttons for AI) */}
                  {msg.sender === 'ai' && (
                    <div className="pt-1 flex items-center justify-between text-[11px] text-slate-500">
                      <span>{new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => {
                            setFeedbackMessageId(msg.id);
                            setFeedbackRating(1);
                          }}
                          className="hover:text-emerald-400 transition"
                          title="Helpful"
                        >
                          <ThumbsUp className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => {
                            setFeedbackMessageId(msg.id);
                            setFeedbackRating(-1);
                          }}
                          className="hover:text-rose-400 transition"
                          title="Needs Improvement"
                        >
                          <ThumbsDown className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>

                {msg.sender === 'user' && (
                  <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0 mt-1">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            ))
          )}

          {/* Typing Loading Indicator */}
          {loading && (
            <div className="flex items-center space-x-3 text-slate-400 text-xs py-2">
              <div className="w-8 h-8 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
                <RefreshCw className="w-4 h-4 animate-spin" />
              </div>
              <div className="bg-slate-900 border border-slate-800 px-4 py-2.5 rounded-2xl text-slate-300 animate-pulse">
                Searching vector database & generating grounded answer...
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Message Input Box */}
        <div className="pt-3 border-t border-slate-800 shrink-0">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendQuestion();
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              value={inputQuestion}
              onChange={(e) => setInputQuestion(e.target.value)}
              placeholder="Ask a question (e.g. What is the fee for CSE?)..."
              disabled={loading}
              className="flex-1 bg-slate-900 border border-slate-700/80 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!inputQuestion.trim() || loading}
              className="py-3 px-5 gradient-btn rounded-xl text-white font-semibold text-sm flex items-center justify-center shadow-lg shadow-blue-500/25 disabled:opacity-50 cursor-pointer"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>

      </main>

      {/* Feedback Modal Popup */}
      {feedbackMessageId && (
        <FeedbackModal
          messageId={feedbackMessageId}
          rating={feedbackRating}
          onClose={() => setFeedbackMessageId(null)}
          onSubmitted={() => alert('Thank you for your feedback!')}
        />
      )}
    </div>
  );
}
