import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, X, Send } from 'lucide-react';
import api from '../services/api';

export default function FeedbackModal({ messageId, rating, onClose, onSubmitted }) {
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.post('/chat/feedback', {
        message_id: messageId,
        rating: rating,
        comment: comment.trim() || null
      });
      onSubmitted();
      onClose();
    } catch (err) {
      console.error('Failed to submit feedback:', err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
      <div className="glass-card rounded-2xl p-6 w-full max-w-md relative shadow-2xl">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3 mb-4">
          <div className={`p-3 rounded-xl ${
            rating === 1 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
          }`}>
            {rating === 1 ? <ThumbsUp className="w-6 h-6" /> : <ThumbsDown className="w-6 h-6" />}
          </div>
          <div>
            <h3 className="font-bold text-slate-100 text-lg">
              {rating === 1 ? 'Helpful Response' : 'Improvement Feedback'}
            </h3>
            <p className="text-xs text-slate-400">
              {rating === 1 
                ? 'Glad this helped! Any additional notes?' 
                : 'Help us improve by providing details on what was missing.'}
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <textarea
              rows={3}
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Optional comment..."
              className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-sm text-slate-200 focus:outline-none focus:border-blue-500 resize-none"
            />
          </div>

          <div className="flex justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-400 hover:text-white"
            >
              Skip
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2 gradient-btn text-white font-medium text-sm rounded-xl flex items-center space-x-1.5 shadow-lg shadow-blue-500/20"
            >
              <Send className="w-4 h-4" />
              <span>{submitting ? 'Submitting...' : 'Submit Feedback'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
