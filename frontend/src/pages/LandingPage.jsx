import React from 'react';
import { Link } from 'react-router-dom';
import { Bot, ShieldCheck, FileSearch, Sparkles, BookOpen, Layers, ArrowRight, CheckCircle2 } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between">
      
      {/* Hero Section */}
      <section className="relative pt-20 pb-16 px-4 overflow-hidden">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute top-1/3 right-1/4 w-80 h-80 bg-cyan-600/15 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-5xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-6">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Next-Gen RAG Architecture</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-tight mb-6">
            Instant, Verified Answers from <br />
            <span className="gradient-text">Official College Documents</span>
          </h1>

          <p className="text-lg sm:text-xl text-slate-400 max-w-3xl mx-auto mb-10 leading-relaxed">
            Powered by Retrieval-Augmented Generation (RAG). Ask anything about admissions, courses, fees, exams, hostel rules, and scholarships with 100% grounded accuracy and instant source citations.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/chat"
              className="w-full sm:w-auto px-8 py-4 rounded-xl text-base font-semibold gradient-btn text-white shadow-xl shadow-blue-500/25 flex items-center justify-center space-x-2 group"
            >
              <span>Ask Chatbot Now</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>

            <Link
              to="/login"
              className="w-full sm:w-auto px-8 py-4 rounded-xl text-base font-semibold glass-card text-slate-200 hover:text-white border border-slate-700/60 hover:border-slate-600 flex items-center justify-center space-x-2"
            >
              <span>Admin Portal Login</span>
            </Link>
          </div>
        </div>
      </section>

      {/* Feature Highlights Grid */}
      <section className="py-16 px-4 max-w-7xl mx-auto w-full">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          <div className="glass-card p-8 rounded-2xl border border-slate-800 hover:border-blue-500/30 transition">
            <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 mb-6">
              <FileSearch className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold mb-3 text-slate-100">Document Grounded RAG</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Every query triggers semantic vector retrieval across official college circulars, notices, and handbooks before generating answers.
            </p>
          </div>

          <div className="glass-card p-8 rounded-2xl border border-slate-800 hover:border-indigo-500/30 transition">
            <div className="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-6">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold mb-3 text-slate-100">Zero Hallucination Guarantee</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              If an answer is not found in official documents, the AI clearly informs you rather than guessing or fabricating responses.
            </p>
          </div>

          <div className="glass-card p-8 rounded-2xl border border-slate-800 hover:border-cyan-500/30 transition">
            <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 mb-6">
              <Layers className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold mb-3 text-slate-100">Source References & Page #</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Transparent source citation cards display the document name, page number, and confidence score for complete verifiability.
            </p>
          </div>

        </div>
      </section>

      {/* RAG Workflow Diagram Visual */}
      <section className="py-12 px-4 max-w-5xl mx-auto w-full">
        <div className="glass-card rounded-2xl p-8 border border-slate-800">
          <h2 className="text-2xl font-bold text-center mb-8 gradient-text">Real-Time RAG Execution Pipeline</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center text-xs font-semibold text-slate-300">
            <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
              <div className="text-blue-400 font-bold mb-1">1. Query Vectorization</div>
              <p className="text-[11px] text-slate-400 font-normal">Converts student question into dense numerical embeddings.</p>
            </div>
            <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
              <div className="text-cyan-400 font-bold mb-1">2. Semantic Vector Search</div>
              <p className="text-[11px] text-slate-400 font-normal">Searches ChromaDB vector database for top matching document chunks.</p>
            </div>
            <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
              <div className="text-indigo-400 font-bold mb-1">3. Context Injection</div>
              <p className="text-[11px] text-slate-400 font-normal">Passes retrieved document context to LLM with strict grounding prompt.</p>
            </div>
            <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
              <div className="text-emerald-400 font-bold mb-1">4. Grounded Output & Source</div>
              <p className="text-[11px] text-slate-400 font-normal">Generates factual answer with clickable source citation cards.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 text-center text-xs text-slate-500 border-t border-slate-800/60">
        © 2026 Excellence Institute of Technology — RAG College Information Assistant System.
      </footer>
    </div>
  );
}
