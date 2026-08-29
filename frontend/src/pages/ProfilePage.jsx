import React from 'react';
import { useAuth } from '../context/AuthContext';
import { User, Shield, Mail, Calendar, Key, CheckCircle2 } from 'lucide-react';

export default function ProfilePage() {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="glass-card rounded-2xl p-8 border border-slate-800 shadow-xl">
        
        {/* User Card Header */}
        <div className="flex items-center space-x-4 pb-6 border-b border-slate-800">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-white text-2xl font-bold uppercase shadow-lg shadow-cyan-500/20">
            {user.name ? user.name[0] : 'U'}
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-100">{user.name}</h1>
            <div className="flex items-center space-x-2 mt-1">
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider ${
                user.role === 'admin'
                  ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                  : 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
              }`}>
                {user.role} Role
              </span>
              <span className="text-xs text-slate-400">• Active User Account</span>
            </div>
          </div>
        </div>

        {/* Profile Attributes */}
        <div className="py-6 space-y-4">
          <div className="flex items-center justify-between p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="flex items-center space-x-3">
              <Mail className="w-5 h-5 text-blue-400" />
              <div>
                <div className="text-xs text-slate-400 font-medium">Email Address</div>
                <div className="text-sm font-semibold text-slate-200">{user.email}</div>
              </div>
            </div>
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          </div>

          <div className="flex items-center justify-between p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="flex items-center space-x-3">
              <Shield className="w-5 h-5 text-indigo-400" />
              <div>
                <div className="text-xs text-slate-400 font-medium">Access Control Role</div>
                <div className="text-sm font-semibold text-slate-200 capitalize">{user.role} Authorization</div>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="flex items-center space-x-3">
              <Calendar className="w-5 h-5 text-cyan-400" />
              <div>
                <div className="text-xs text-slate-400 font-medium">Member Since</div>
                <div className="text-sm font-semibold text-slate-200">
                  {new Date(user.created_at).toLocaleDateString()}
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
