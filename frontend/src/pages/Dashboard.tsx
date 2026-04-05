import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import StatCard from '../components/StatCard';
import { useDashboard } from '../hooks/useDashboard';
import { useSessionStore } from '../store/sessionStore';
import {
  Activity,
  CheckCircle,
  Target,
  Award,
  Play,
  ChevronRight,
  Clock,
  User,
  ShieldCheck,
  ArrowRight,
  School,
  Users,
  CreditCard
} from 'lucide-react';
import clsx from 'clsx';

import { useAuthStore } from '../store/authStore';

export default function Dashboard() {
  const { user } = useAuthStore();
  const { stats, recentSessions, loading } = useDashboard();

  if (loading || !stats) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse flex flex-col items-center">
          <Activity size={40} className="text-primary-500 mb-4" />
          <p className="text-slate-500 font-bold tracking-wider uppercase text-sm">Loading Workspace...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-12 selection:bg-primary-100">
      <main className="max-w-screen-xl mx-auto px-4 sm:px-6 pt-10 space-y-10 animate-fade-in relative z-10">
        
        {/* decorative glow */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-primary-200/20 rounded-full blur-[100px] pointer-events-none -z-10" />

        {/* ── Header & CTA ── */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 card p-8 border-t-4 border-t-primary-500">
          <div>
            <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-slate-900 to-slate-600 tracking-tight mb-2">
              Welcome back, {user?.full_name.split(' ')[0]}
            </h1>
            <p className="text-slate-500 font-medium text-lg">
              {user?.role === 'student'
                ? 'Ready for your next clinical simulation protocol?'
                : `Managing the platform as ${user?.role.replace('_', ' ')}.`}
            </p>
          </div>
          {user?.role === 'student' && (
            <Link to="/session" className="btn-primary py-4 px-8 text-lg group">
              <Play size={20} className="fill-white group-hover:scale-110 transition-transform" />
              Launch Simulator
            </Link>
          )}
        </div>

        {/* ── Stats Grid (Role-Aware) ── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {user?.role === 'super_admin' && (
            <>
              <StatCard label="Total Universities" value={stats.total_universities} icon={<School size={24} />} color="indigo" />
              <StatCard label="Total Users" value={stats.total_users} icon={<User size={24} />} color="emerald" />
              <StatCard label="Total Students" value={stats.total_students} icon={<Users size={24} />} color="amber" />
              <StatCard label="Active Subscriptions" value={stats.active_subscriptions} icon={<CreditCard size={24} />} color="cyan" />
            </>
          )}

          {user?.role === 'university_admin' && (
            <>
              <StatCard label="Total Students" value={stats.total_students} icon={<Users size={24} />} color="indigo" />
              <StatCard label="Lab Admins" value={stats.total_lab_admins} icon={<ShieldCheck size={24} />} color="emerald" />
              <StatCard label="Total Sessions" value={stats.total_sessions} icon={<Activity size={24} />} color="amber" />
              <StatCard label="Avg Performance" value={`${stats.avg_performance}%`} icon={<Target size={24} />} color="cyan" />
            </>
          )}

          {user?.role === 'student' && (
            <>
              <StatCard label="Total Sessions" value={stats.total_sessions} icon={<Activity size={24} />} color="indigo" />
              <StatCard label="Completed" value={stats.completed} icon={<CheckCircle size={24} />} color="emerald" />
              <StatCard label="Avg Performance" value={`${stats.avg_performance}%`} icon={<Target size={24} />} color="amber" />
              <StatCard label="Last Score" value={`${stats.last_performance}%`} icon={<Award size={24} />} color="cyan" />
            </>
          )}
        </div>

        <div className="grid lg:grid-cols-3 gap-10">
          
          {/* Main Column: Recents */}
          <div className="lg:col-span-2 space-y-6">
            <div className="flex items-center justify-between px-2">
              <h2 className="section-title text-2xl">Recent Sessions</h2>
              <button className="text-sm font-bold text-primary-600 hover:text-primary-700 flex items-center gap-1 group">
                View All <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
              </button>
            </div>
            
            <div className="card divide-y divide-slate-100/50">
              {recentSessions.map((Session) => (
                <div key={Session.id} className="p-5 hover:bg-slate-50/50 transition-all duration-300 flex items-center justify-between group cursor-pointer">
                  <div className="flex items-center gap-5">
                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-slate-100 to-slate-200 flex items-center justify-center text-slate-500 shadow-inner group-hover:from-primary-50 group-hover:to-primary-100 group-hover:text-primary-600 transition-colors">
                      <User size={20} />
                    </div>
                    <div>
                      <p className="font-extrabold text-slate-800 text-lg">Patient #{Session.patientId}</p>
                      <div className="flex items-center gap-2 mt-1 text-sm text-slate-500 font-medium">
                        <span className="flex items-center gap-1.5"><Clock size={14} className="text-slate-400" /> {Session.duration}</span>
                        <span className="text-slate-300">&bull;</span>
                        <span>{Session.date}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <p className="text-xs uppercase tracking-widest font-bold text-slate-400 mb-1">Score</p>
                      <p className={clsx(
                        "font-black text-2xl",
                        Session.score >= 85 ? "text-emerald-500" : Session.score >= 70 ? "text-amber-500" : "text-rose-500"
                      )}>
                        {Session.score}%
                      </p>
                    </div>
                    <div className="w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center group-hover:bg-primary-50 transition-colors">
                      <ChevronRight size={20} className="text-slate-400 group-hover:text-primary-600 transition-colors" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right Column: Protocol Info */}
          <div className="space-y-6">
            <h2 className="section-title text-2xl px-2">Clinical Guidelines</h2>
            <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-primary-900 to-slate-900 text-white shadow-2xl shadow-primary-900/20 p-8 border border-white/10">
              {/* background mesh */}
              <div className="absolute top-0 right-0 p-4 opacity-10 pointer-events-none">
                <svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
                  <defs><pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M 20 0 L 0 0 0 20" fill="none" stroke="white" strokeWidth="1"/></pattern></defs>
                  <rect width="200" height="200" fill="url(#grid)" />
                </svg>
              </div>

              <div className="relative z-10">
                <div className="flex items-center gap-4 mb-8">
                  <div className="p-3 bg-white/10 rounded-xl backdrop-blur-md shadow-inner border border-white/5">
                    <ShieldCheck size={28} className="text-primary-300" />
                  </div>
                  <div>
                    <h3 className="font-extrabold text-xl tracking-wide">Standard Protocol</h3>
                    <p className="text-primary-200 text-sm font-medium">Hughson-Westlake Method</p>
                  </div>
                </div>
                
                <ul className="space-y-5 text-sm text-indigo-50 font-medium mb-8">
                  <li className="flex gap-4 isolate items-start">
                    <span className="flex-none flex items-center justify-center w-6 h-6 rounded-full bg-primary-500/30 text-primary-200 font-bold text-xs ring-1 ring-primary-400/50">1</span>
                    <span className="pt-0.5 leading-relaxed">Test better ear (or Right) first starting at 1000 Hz.</span>
                  </li>
                  <li className="flex gap-4 isolate items-start">
                    <span className="flex-none flex items-center justify-center w-6 h-6 rounded-full bg-primary-500/30 text-primary-200 font-bold text-xs ring-1 ring-primary-400/50">2</span>
                    <span className="pt-0.5 leading-relaxed">Find threshold using <span className="text-white font-bold">down 10, up 5</span> ascending technique.</span>
                  </li>
                  <li className="flex gap-4 isolate items-start">
                    <span className="flex-none flex items-center justify-center w-6 h-6 rounded-full bg-primary-500/30 text-primary-200 font-bold text-xs ring-1 ring-primary-400/50">3</span>
                    <span className="pt-0.5 leading-relaxed">Test higher frequencies (2k, 3k, 4k, 6k, 8k) then lower (500, 250).</span>
                  </li>
                  <li className="flex gap-4 isolate items-start">
                    <span className="flex-none flex items-center justify-center w-6 h-6 rounded-full bg-primary-500/30 text-primary-200 font-bold text-xs ring-1 ring-primary-400/50">4</span>
                    <span className="pt-0.5 leading-relaxed">Identify necessity for AC masking (IA ≥ 40dB).</span>
                  </li>
                </ul>
                
                <button className="w-full py-3 bg-white/10 hover:bg-white/20 transition-all duration-300 rounded-xl font-bold tracking-wide text-sm backdrop-blur-md border border-white/20 hover:shadow-lg hover:-translate-y-0.5">
                  Review Full Guidelines
                </button>
              </div>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}
