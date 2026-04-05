import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import { useAuthStore } from '../store/authStore';
import { LogOut, User as UserIcon } from 'lucide-react';

export default function AppLayout() {
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  const rightContent = (
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-50 border border-slate-200">
        <UserIcon size={14} className="text-slate-500" />
        <div className="flex flex-col items-start leading-tight">
          <span className="text-xs font-semibold text-slate-700">{user?.full_name}</span>
          <span className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">{user?.role}</span>
        </div>
      </div>
      <button
        onClick={handleLogout}
        className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        title="Sign Out"
      >
        <LogOut size={18} />
      </button>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-50/50">
      <Navbar rightContent={rightContent} />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 max-w-screen-2xl mx-auto p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
