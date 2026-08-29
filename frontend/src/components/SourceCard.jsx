import React, { useState } from 'react';
import { FileText, ChevronDown, ChevronUp, Tag, ExternalLink } from 'lucide-react';

export default function SourceCard({ source, index }) {
  const [expanded, setExpanded] = useState(false);

  const confidencePercent = Math.round((source.similarity_score || 0.8) * 100);

  return (
    <div className="bg-slate-900/80 border border-slate-700/60 rounded-xl p-3 text-xs transition hover:border-slate-600">
      <div 
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center space-x-2 min-w-0">
          <div className="w-6 h-6 rounded-md bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold text-[10px]">
            #{index + 1}
          </div>
          <div className="truncate">
            <h4 className="font-semibold text-slate-200 truncate">{source.document_title}</h4>
            <div className="flex items-center space-x-2 text-[10px] text-slate-400 mt-0.5">
              <span className="flex items-center">
                <Tag className="w-3 h-3 mr-0.5 text-cyan-400" />
                {source.category}
              </span>
              <span>•</span>
              <span>Page {source.page_number}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2 shrink-0">
          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            {confidencePercent}% Match
          </span>
          {expanded ? (
            <ChevronUp className="w-4 h-4 text-slate-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-slate-400" />
          )}
        </div>
      </div>

      {expanded && (
        <div className="mt-2.5 pt-2.5 border-t border-slate-800 text-slate-300 font-mono text-[11px] leading-relaxed bg-slate-950/60 p-2.5 rounded-lg">
          <div className="text-[10px] font-sans text-slate-400 mb-1 font-semibold uppercase tracking-wider">Retrieved Document Snippet:</div>
          "{source.snippet}"
        </div>
      )}
    </div>
  );
}
