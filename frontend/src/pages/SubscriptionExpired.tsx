import React from 'react';
import { CreditCard, LogOut, ExternalLink } from 'lucide-react';
import { useAuthStore } from '../store/authStore';

export default function SubscriptionExpired() {
  const { logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <div className="max-w-md w-full text-center space-y-6 bg-white p-10 rounded-3xl shadow-xl border border-slate-100">
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-amber-50 text-amber-600 mb-2">
          <CreditCard size={40} strokeWidth={2} />
        </div>

        <div className="space-y-2">
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Subscription Expired</h1>
          <p className="text-slate-500 font-medium">
            Your university's subscription has expired. Please contact your administrator to renew.
          </p>
        </div>

        <div className="flex flex-col gap-3">
          <a
            href="mailto:admin@university.edu"
            className="flex items-center justify-center gap-2 w-full py-3.5 px-4 bg-primary-600 text-white font-bold rounded-xl hover:bg-primary-700 transition-all shadow-lg shadow-primary-200"
          >
            <ExternalLink size={18} />
            Contact Administrator
          </a>

          <button
            onClick={handleLogout}
            className="flex items-center justify-center gap-2 w-full py-3.5 px-4 bg-white text-slate-600 font-bold rounded-xl border border-slate-200 hover:bg-slate-50 transition-all"
          >
            <LogOut size={18} />
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
}
