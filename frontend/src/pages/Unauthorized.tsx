import React from 'react';
import { ShieldAlert, LogIn, Home } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Unauthorized() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <div className="max-w-md w-full text-center space-y-6 bg-white p-10 rounded-3xl shadow-xl border border-slate-100">
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-red-50 text-red-600 mb-2">
          <ShieldAlert size={40} strokeWidth={2} />
        </div>

        <div className="space-y-2">
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Access Denied</h1>
          <p className="text-slate-500 font-medium">
            You don't have the required permissions to view this page.
          </p>
        </div>

        <div className="flex flex-col gap-3">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center justify-center gap-2 w-full py-3.5 px-4 bg-slate-900 text-white font-bold rounded-xl hover:bg-slate-800 transition-all shadow-lg shadow-slate-200"
          >
            <Home size={18} />
            Back to Dashboard
          </button>

          <button
            onClick={() => navigate('/login')}
            className="flex items-center justify-center gap-2 w-full py-3.5 px-4 bg-white text-slate-600 font-bold rounded-xl border border-slate-200 hover:bg-slate-50 transition-all"
          >
            <LogIn size={18} />
            Sign in as different user
          </button>
        </div>
      </div>
    </div>
  );
}
