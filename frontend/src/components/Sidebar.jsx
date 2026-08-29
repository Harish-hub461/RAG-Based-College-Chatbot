import React from 'react';
import { Plus, MessageSquare, Trash2, ChevronRight, Clock } from 'lucide-react';

export default function Sidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewChat,
  onDeleteConversation
}) {
  return (
    <aside className="w-full md:w-64 glass-card rounded-2xl p-4 flex flex-col h-[calc(100vh-6rem)]">
      
      {/* New Chat Button */}
      <button
        onClick={onNewChat}
        className="w-full py-3 px-4 rounded-xl gradient-btn text-white font-medium flex items-center justify-center space-x-2 shadow-lg shadow-blue-500/20 mb-4 cursor-pointer"
      >
        <Plus className="w-5 h-5" />
        <span>New Conversation</span>
      </button>

      {/* History Header */}
      <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider px-2 mb-2">
        <span className="flex items-center space-x-1.5">
          <Clock className="w-3.5 h-3.5 text-blue-400" />
          <span>Past Chats</span>
        </span>
        <span className="bg-slate-800 px-2 py-0.5 rounded-full text-slate-300">
          {conversations.length}
        </span>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto space-y-1.5 pr-1">
        {conversations.length === 0 ? (
          <div className="text-center py-8 text-slate-500 text-xs">
            No previous conversations found.<br />Start a new chat!
          </div>
        ) : (
          conversations.map((conv) => {
            const isActive = conv.id === activeConversationId;
            return (
              <div
                key={conv.id}
                onClick={() => onSelectConversation(conv.id)}
                className={`group relative flex items-center justify-between p-3 rounded-xl cursor-pointer text-sm transition-all ${
                  isActive
                    ? 'bg-blue-600/25 border border-blue-500/40 text-blue-300 font-medium'
                    : 'text-slate-300 hover:bg-slate-800/60 hover:text-white border border-transparent'
                }`}
              >
                <div className="flex items-center space-x-2.5 min-w-0 pr-6">
                  <MessageSquare className={`w-4 h-4 shrink-0 ${isActive ? 'text-blue-400' : 'text-slate-400'}`} />
                  <span className="truncate">{conv.title || 'Untitled Chat'}</span>
                </div>

                {/* Delete Conversation Button */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteConversation(conv.id);
                  }}
                  title="Delete Chat"
                  className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-rose-400 transition"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            );
          })
        )}
      </div>
    </aside>
  );
}
