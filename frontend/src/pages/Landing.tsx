import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { Activity, ShieldCheck, Stethoscope, ChevronRight, PlayCircle, Sparkles } from 'lucide-react';

export default function Landing() {
  return (
    <div className="min-h-screen flex flex-col pt-14 selection:bg-primary-100">
      
      {/* ── Fixed Premium Navbar ── */}
      <div className="fixed top-0 left-0 right-0 z-50 glass-nav">
        <Navbar rightContent={
          <Link to="/dashboard" className="btn-secondary py-2 px-5 text-sm rounded-xl shadow-none hover:shadow-md border-slate-200">
            Sign In
          </Link>
        } />
      </div>

      {/* ── Hero Section (Premium SaaS Style) ── */}
      <section className="relative flex-1 flex flex-col items-center justify-center text-center px-4 py-32 overflow-hidden">
        {/* Background Decorative Blobs */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary-200/30 rounded-full blur-[120px] pointer-events-none -z-10 animate-pulse" style={{ animationDuration: '8s' }} />
        <div className="absolute top-1/4 right-1/4 w-[400px] h-[400px] bg-cyan-200/20 rounded-full blur-[100px] pointer-events-none -z-10" />

        <div className="max-w-4xl mx-auto relative z-10 animate-slide-up">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/60 border border-slate-200 shadow-sm backdrop-blur-md mb-8">
            <Sparkles size={16} className="text-amber-500" />
            <span className="text-sm font-semibold text-slate-700">Next-gen Clinical Training Platform</span>
          </div>
          
          <h1 className="text-5xl sm:text-7xl font-extrabold text-transparent bg-clip-text bg-gradient-to-br from-slate-900 via-slate-800 to-slate-500 tracking-tight leading-[1.1] mb-8">
            Master Pure-Tone Audiometry <br/>
            <span className="bg-clip-text bg-gradient-to-r from-primary-600 to-cyan-500">Without the Lab.</span>
          </h1>
          
          <p className="text-lg sm:text-xl text-slate-600 mb-12 max-w-2xl mx-auto leading-relaxed font-medium">
            The most advanced clinical PTA simulator for audiology students. Practice threshold testing, masking, and audiogram interpretation with instant, AI-driven feedback.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/dashboard" className="btn-primary text-lg px-8 py-4 rounded-xl w-full sm:w-auto shadow-primary-500/30">
              <PlayCircle size={20} />
              Get Started
            </Link>
            <a href="#how-it-works" className="btn-secondary text-lg px-8 py-4 rounded-xl w-full sm:w-auto group">
              See How It Works
              <ChevronRight size={18} className="text-slate-400 group-hover:text-slate-900 transition-colors" />
            </a>
          </div>
        </div>
      </section>

      {/* ── How It Works ── */}
      <section id="how-it-works" className="relative py-32 px-4 bg-slate-50/50">
        <div className="max-w-screen-xl mx-auto">
          <div className="text-center mb-20 animate-slide-up">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary-100/50 text-primary-700 font-bold text-xs uppercase tracking-widest mb-4">
              Simple Process
            </div>
            <h2 className="text-4xl font-extrabold text-slate-900 tracking-tight mb-5">How it Works</h2>
            <p className="text-lg text-slate-500 max-w-2xl mx-auto font-medium">Master the audiometer in three simple steps.</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-12 relative">
            {/* Connecting lines for desktop */}
            <div className="hidden md:block absolute top-[50px] left-[20%] right-[20%] h-[2px] bg-gradient-to-r from-primary-200 via-emerald-200 to-amber-200 z-0"></div>

            <div className="relative z-10 flex flex-col items-center text-center group">
              <div className="w-24 h-24 rounded-full bg-white border-4 border-primary-100 flex items-center justify-center text-primary-600 text-3xl font-black mb-6 shadow-xl shadow-primary-500/10 group-hover:scale-110 transition-transform duration-500">
                1
              </div>
              <h3 className="text-xl font-bold text-slate-800 mb-3">Connect & Setup</h3>
              <p className="text-slate-500 font-medium leading-relaxed">System generates a unique virtual patient with specific hearing loss characteristics.</p>
            </div>

            <div className="relative z-10 flex flex-col items-center text-center group">
              <div className="w-24 h-24 rounded-full bg-white border-4 border-emerald-100 flex items-center justify-center text-emerald-600 text-3xl font-black mb-6 shadow-xl shadow-emerald-500/10 group-hover:scale-110 transition-transform duration-500">
                2
              </div>
              <h3 className="text-xl font-bold text-slate-800 mb-3">Present Stimulus</h3>
              <p className="text-slate-500 font-medium leading-relaxed">Use the clinical audiometer to find thresholds. Apply masking when necessary.</p>
            </div>

            <div className="relative z-10 flex flex-col items-center text-center group">
              <div className="w-24 h-24 rounded-full bg-white border-4 border-amber-100 flex items-center justify-center text-amber-600 text-3xl font-black mb-6 shadow-xl shadow-amber-500/10 group-hover:scale-110 transition-transform duration-500">
                3
              </div>
              <h3 className="text-xl font-bold text-slate-800 mb-3">Diagnose</h3>
              <p className="text-slate-500 font-medium leading-relaxed">Interpret the resulting audiogram and receive instant AI feedback on your protocol.</p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Key Features ── */}
      <section className="relative py-32 px-4 border-t border-slate-200/50">
        <div className="absolute inset-0 bg-white/40 backdrop-blur-3xl -z-10" />
        <div className="max-w-screen-xl mx-auto">
          <div className="text-center mb-20 animate-slide-up" style={{ animationDelay: '0.1s' }}>
            <h2 className="text-4xl font-extrabold text-slate-900 tracking-tight mb-5">Everything you need to practice safely</h2>
            <p className="text-lg text-slate-500 max-w-2xl mx-auto font-medium">Experience a hyper-realistic control panel, dynamic patient models, and clinical-grade evaluation protocols before interacting with real patients.</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="card-hover p-10 text-center flex flex-col items-center group">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-50 to-primary-100 text-primary-600 flex items-center justify-center mb-8 shadow-inner group-hover:scale-110 transition-transform duration-500">
                <Stethoscope size={36} strokeWidth={1.5} />
              </div>
              <h3 className="text-2xl font-bold text-slate-800 mb-4">Realistic Patients</h3>
              <p className="text-slate-600 leading-relaxed font-medium">System generates dynamic patients with varying degrees of hearing loss, naturally incorporating fatigue and false positives.</p>
            </div>
            
            <div className="card-hover p-10 text-center flex flex-col items-center group relative z-10 scale-105 shadow-[0_20px_50px_rgba(0,0,0,0.1)] border-primary-100">
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-b from-white to-primary-50/20 -z-10" />
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-amber-50 to-orange-100 text-amber-600 flex items-center justify-center mb-8 shadow-inner group-hover:scale-110 transition-transform duration-500">
                <Activity size={36} strokeWidth={1.5} />
              </div>
              <h3 className="text-2xl font-bold text-slate-800 mb-4">Full Audiometer Control</h3>
              <p className="text-slate-600 leading-relaxed font-medium">Complete control over frequency, intensity, AC/BC transducers, and standard clinical masking application.</p>
            </div>
            
            <div className="card-hover p-10 text-center flex flex-col items-center group">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-teal-50 to-emerald-100 text-emerald-600 flex items-center justify-center mb-8 shadow-inner group-hover:scale-110 transition-transform duration-500">
                <ShieldCheck size={36} strokeWidth={1.5} />
              </div>
              <h3 className="text-2xl font-bold text-slate-800 mb-4">AI-Driven Evaluation</h3>
              <p className="text-slate-600 leading-relaxed font-medium">Receive instant feedback on your protocol adherence, threshold accuracy, and diagnostic interpretative skills.</p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="bg-slate-900 border-t border-slate-800 py-12 px-4 text-center">
        <div className="max-w-screen-xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <Activity className="text-primary-500" />
            <span className="text-white font-bold tracking-wide">PTA Simulator</span>
          </div>
          <p className="text-slate-400 font-medium text-sm">
            © 2026 Advanced Agentic Coding Project. Built for Excellence.
          </p>
        </div>
      </footer>
    </div>
  );
}
