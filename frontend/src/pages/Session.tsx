import { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import ControlPanel from '../components/ControlPanel';
import AudiogramChart from '../components/AudiogramChart';
import AttemptHistory from '../components/AttemptHistory';
import { useSession } from '../hooks/useSession';
import { useTone } from '../hooks/useTone';
import { useTimer } from '../hooks/useTimer';
import { useSessionStore } from '../store/sessionStore';
import { Clock, Activity, Flag } from 'lucide-react';

export default function Session() {
  const { session, loading: sessionLoading, error: sessionError, startSession, endSession } = useSession();
  const {
    playTone,
    storeTone,
    lastResponse,
    storedThresholds,
    loading: toneLoading,
    error: toneError,
    canStoreToneForSelection,
  } = useTone();
  const attempts = useSessionStore(s => s.attempts);
  
  // Timer runs as long as there is an active session
  const { formatted: timerDisplay } = useTimer(!!session);
  const [showEndModal, setShowEndModal] = useState(false);

  // Auto-start on mount if no session
  useEffect(() => {
    if (!session && !sessionLoading && !sessionError) {
      startSession();
    }
  }, [session, sessionLoading, sessionError, startSession]);

  if (sessionLoading || (!session && !sessionError)) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="animate-pulse flex flex-col items-center">
          <Activity size={40} className="text-primary-500 mb-4" />
          <p className="text-slate-500 font-bold tracking-widest uppercase text-sm">Initializing Simulator...</p>
        </div>
      </div>
    );
  }

  if (sessionError || !session) {
    return (
      <div className="h-screen flex items-center justify-center bg-slate-50">
        <div className="card p-8 max-w-md text-center border-t-4 border-t-rose-500 shadow-xl shadow-rose-500/10">
          <div className="w-16 h-16 bg-rose-100 text-rose-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <Flag size={24} />
          </div>
          <h2 className="text-2xl font-bold text-slate-800 mb-2">Simulation Error</h2>
          <p className="text-slate-500 mb-6 font-medium">{sessionError || 'Session could not be initialized'}</p>
          <button onClick={() => window.location.reload()} className="btn-primary w-full">Retry Connection</button>
        </div>
      </div>
    );
  }

  const handleEndConfirm = () => {
    setShowEndModal(false);
    endSession();
  };

  return (
    <div className="h-screen bg-slate-50 flex flex-col overflow-hidden selection:bg-primary-100 relative">
      
      {/* Background blobs for premium feel */}
      <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-primary-200/20 rounded-full blur-[120px] pointer-events-none -z-10" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-cyan-200/20 rounded-full blur-[120px] pointer-events-none -z-10" />

      {/* ── Fixed Navbar ── */}
      <div className="glass-nav relative z-20">
        <Navbar
          showBrand={false}
          leftContent={
            <div className="w-full flex items-center justify-between px-2 flex-1">
              <div className="flex items-center gap-5">
                <div className="flex items-center gap-3 bg-white/80 backdrop-blur-md border border-slate-200 shadow-sm rounded-xl p-1.5 pr-5">
                  <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-primary-700 text-white shadow-md shadow-primary-500/20">
                    <Activity size={16} strokeWidth={2.5} />
                  </div>
                  <div className="flex gap-4 items-center">
                    <span className="text-sm font-black text-slate-700 border-r border-slate-200 pr-4">Session #{session.id}</span>
                    <span className="text-sm flex items-center">
                      <span className="text-slate-400 font-bold mr-1.5 text-[11px] uppercase tracking-widest">Patient</span> 
                      <span className="font-black text-slate-800 bg-slate-100 px-2 py-0.5 rounded-md">{session.patient_id}</span>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          }
          rightContent={
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-4 py-2 bg-white/80 backdrop-blur-md border border-slate-200 shadow-sm rounded-xl text-slate-700 font-mono text-base font-bold">
                <Clock size={16} className="text-slate-400" />
                {timerDisplay}
              </div>
              <button 
                onClick={() => setShowEndModal(true)}
                className="btn-danger py-2 px-5 text-sm"
              >
                <Flag size={16} /> 
                <span className="tracking-wide">Finish Test</span>
              </button>
            </div>
          }
        />
      </div>

      {/* ── 3-Column Layout ── */}
      <div className="flex-1 overflow-hidden p-4 relative z-10">
        {toneError && (
          <div className="w-full max-w-[1800px] mx-auto mb-4 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-bold text-rose-800 shadow-sm">
            {toneError}
          </div>
        )}
        <div className="w-full max-w-[1800px] mx-auto h-full grid md:grid-cols-12 gap-4 animate-slide-up">
          
          {/* ── LEFT: Control Panel (col-span-4 lg:col-span-5) ── */}
          <div className="md:col-span-4 lg:col-span-5 h-full min-h-0 overflow-y-auto pr-1">
            <ControlPanel 
              sessionId={session.id}
              onPlayTone={playTone}
              onStoreTone={storeTone}
              lastResponse={lastResponse}
              isLoading={toneLoading}
              storedThresholds={storedThresholds}
              canStoreToneForSelection={canStoreToneForSelection}
            />
          </div>

          {/* ── CENTER: Audiogram Chart (md:col-span-5 lg:col-span-5) ── */}
          <div className="md:col-span-12 lg:col-span-5 h-full flex flex-col min-h-0">
            <div className="card flex-1 flex flex-col p-4 shadow-xl shadow-slate-200/40 overflow-hidden">
              <div className="flex items-center justify-between mb-2 flex-none">
                <div className="flex items-center gap-2">
                  <h2 className="text-xl font-extrabold text-slate-800 tracking-tight">Audiogram</h2>
                  <div className="px-2 py-0.5 rounded-full bg-slate-100 text-[10px] font-bold text-slate-500 uppercase tracking-widest border border-slate-200 shadow-inner">Live</div>
                </div>
                <div className="flex items-center gap-3 bg-slate-50 px-3 py-1.5 rounded-xl border border-slate-100 shadow-sm">
                  <span className="flex items-center gap-1.5 text-[11px] font-bold text-slate-600">
                    <span className="w-2.5 h-2.5 rounded-full bg-red-500 shadow-sm"></span> Right
                  </span>
                  <span className="flex items-center gap-1.5 text-[11px] font-bold text-slate-600">
                    <span className="w-2.5 h-2.5 rounded-full bg-blue-500 shadow-sm"></span> Left
                  </span>
                </div>
              </div>
              <div className="flex-1 bg-white rounded-xl border border-slate-100 shadow-inner overflow-hidden relative flex flex-col items-center justify-center p-4 min-h-0">
                 {/* subtle grid background */}
                <div className="absolute inset-0 opacity-[0.03] pointer-events-none" style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, black 1px, transparent 0)', backgroundSize: '16px 16px' }}></div>
                <div className="w-full h-full flex flex-col items-center justify-center">
                   <div className="w-full h-[85%] flex items-center justify-center">
                     <AudiogramChart storedThresholds={storedThresholds} />
                   </div>
                </div>
              </div>
            </div>
          </div>

          {/* ── RIGHT: History (md:col-span-3 lg:col-span-2) ── */}
          <div className="md:col-span-12 lg:col-span-2 h-[300px] lg:h-full min-h-0">
            <div className="card h-full p-4 shadow-lg shadow-slate-200/40">
              <AttemptHistory attempts={attempts} storedThresholds={storedThresholds} />
            </div>
          </div>

        </div>
      </div>

      {/* ── End Session Modal ── */}
      {showEndModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/40 backdrop-blur-md p-4 animate-fade-in">
          <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-sm w-full animate-slide-up border border-white relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary-500 to-cyan-500"></div>
            
            <div className="w-16 h-16 rounded-full bg-amber-50 text-amber-500 flex items-center justify-center mb-6 mx-auto">
              <Flag size={28} strokeWidth={2.5} />
            </div>
            
            <h3 className="text-2xl font-extrabold text-slate-800 tracking-tight text-center mb-3">Conclude Session?</h3>
            <p className="text-slate-500 text-center font-medium leading-relaxed mb-8">
              Are you confident you've secured accurate thresholds for both ears? You will proceed to interpretation.
            </p>
            
            <div className="flex gap-3">
              <button 
                onClick={() => setShowEndModal(false)}
                className="flex-1 btn-secondary"
              >
                Cancel
              </button>
              <button 
                onClick={handleEndConfirm}
                className="flex-1 btn-primary justify-center shadow-lg shadow-primary-500/20"
              >
                Proceed
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
