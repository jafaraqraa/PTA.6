import { Link, Navigate } from 'react-router-dom';
import { useSessionStore } from '../store/sessionStore';
import Navbar from '../components/Navbar';
import { Target, CheckCircle, BrainCircuit, Sparkles, AlertTriangle, RefreshCcw, ChevronDown, Clock, Activity, BarChart3, LineChart } from 'lucide-react';
import AudiogramChart from '../components/AudiogramChart';
import clsx from 'clsx';
import { useState } from 'react';

function getFieldScoreBadge(fs: any) {
  if (fs.status === 'undetermined') return { label: 'NOT SCORED', className: 'text-slate-400' };
  if (fs.status === 'missing') return { label: 'MISSING', className: 'text-rose-500' };
  if (Number(fs.score) >= 100) return { label: 'MATCH', className: 'text-emerald-500' };
  if (Number(fs.score) > 0) return { label: 'PARTIAL', className: 'text-amber-500' };
  return { label: 'MISMATCH', className: 'text-rose-500' };
}

function ScoreCircle({ score, label, primary = false }: { score: number, label: string, primary?: boolean }) {
  const color = score >= 85 ? 'text-emerald-500' : score >= 70 ? 'text-amber-500' : 'text-rose-500';
  const ring = score >= 85 ? 'ring-emerald-400' : score >= 70 ? 'ring-amber-400' : 'ring-rose-400';
  
  if (primary) {
    return (
      <div className="flex flex-col items-center">
        <div className={`relative w-40 h-40 flex items-center justify-center rounded-full bg-white shadow-2xl ring-8 ${ring} ring-offset-4 mb-4`}>
          <div className="absolute inset-0 rounded-full border-8 border-slate-50 -z-10"></div>
          <span className={`text-5xl font-black ${color} tracking-tighter`}>{Math.round(score)}<span className="text-3xl text-slate-300 ml-1">%</span></span>
        </div>
        <span className="text-sm font-black text-slate-400 uppercase tracking-widest text-center mt-2">{label}</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center">
      <div className={`relative w-24 h-24 flex items-center justify-center rounded-full bg-slate-50 border-4 border-slate-100 mb-3 shadow-inner ring-2 ring-offset-2 ${ring}`}>
        <span className={`text-2xl font-black ${color}`}>{Math.round(score)}%</span>
      </div>
      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest text-center">{label}</span>
    </div>
  );
}

export default function Evaluation() {
  const { evaluation: activeEvaluation, resetSession } = useSessionStore();
  const [showDetails, setShowDetails] = useState(false);
  const [compareMode, setCompareMode] = useState<'both' | 'detected' | 'actual'>('both');

  const evalData = activeEvaluation;

  if (!evalData) return <Navigate to="/dashboard" />;

  const { summary, protocol_metrics, ai_feedback, interpretation_evaluations, threshold_comparisons } = evalData;

  const handleNewTest = () => resetSession();

  const actualThresholds: any = threshold_comparisons?.filter((tc: any) => tc.true_threshold_db !== null || tc.true_is_no_response).map((tc: any, i: number) => ({ id: i, session_id: 0, attempt_id: 0, ear_side: tc.ear_side, test_type: tc.test_type, frequency: tc.frequency, threshold_db: tc.true_threshold_db ?? 0, is_no_response: tc.true_is_no_response, is_final: true, created_at: '' })) || [];
  const detectedThresholds: any = threshold_comparisons?.filter((tc: any) => tc.detected_threshold_db !== null || tc.detected_is_no_response).map((tc: any, i: number) => ({ id: i, session_id: 0, attempt_id: 0, ear_side: tc.ear_side, test_type: tc.test_type, frequency: tc.frequency, threshold_db: tc.detected_threshold_db ?? 0, is_no_response: tc.detected_is_no_response, is_final: true, created_at: '' })) || [];
  const rightActualThresholds = actualThresholds.filter((t: any) => t.ear_side === 'right');
  const leftActualThresholds = actualThresholds.filter((t: any) => t.ear_side === 'left');
  const rightDetectedThresholds = detectedThresholds.filter((t: any) => t.ear_side === 'right');
  const leftDetectedThresholds = detectedThresholds.filter((t: any) => t.ear_side === 'left');

  return (
    <div className="min-h-screen bg-slate-50 pb-32">
      
      <div className="absolute top-0 left-0 right-0 h-[400px] bg-gradient-to-b from-slate-800 to-slate-900 overflow-hidden">
        <div className="absolute inset-0 opacity-20" style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)', backgroundSize: '40px 40px' }}></div>
      </div>

      <div className="relative z-20">
        <header className="max-w-screen-xl mx-auto px-6 py-6 flex justify-between items-center text-white">
           <div className="flex items-center gap-3">
             <span className="badge bg-white/10 text-white border-white/20 px-3 py-1 text-xs">Patient #{summary.patient_id ?? 'N/A'}</span>
           </div>
           <div className="flex gap-3">
             <Link to="/dashboard" onClick={handleNewTest} className="btn-secondary py-2 px-4 shadow-xl shadow-black/20 text-sm border-0 bg-white/10 hover:bg-white/20 text-white">
                Dashboard
             </Link>
             <Link to="/session" onClick={handleNewTest} className="btn-primary py-2 px-4 shadow-xl shadow-black/20 text-sm border-0 flex items-center gap-2">
                <RefreshCcw size={16} /> Start New Session
             </Link>
           </div>
        </header>

        <main className="max-w-screen-xl mx-auto px-4 mt-4 space-y-12 animate-fade-in relative z-10">
          
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h1 className="text-5xl font-extrabold text-white tracking-tight mb-4 drop-shadow-md">Session Report</h1>
            <p className="text-indigo-200 text-lg font-medium">Comprehensive AI analysis of your protocol, accuracy, and diagnosis.</p>
          </div>

          {/* ── Scores Dashboard & Session Stats ── */}
          <section className="bg-white rounded-3xl p-10 shadow-2xl border border-slate-100 mx-auto -mt-8 relative overflow-hidden mb-8">
            <div className="absolute top-0 left-0 right-0 h-2 bg-gradient-to-r from-emerald-400 via-amber-400 to-primary-500"></div>
            
            <div className="grid lg:grid-cols-3 gap-12 items-center">
              {/* Overall Grade Card */}
              <div className="flex flex-col items-center col-span-1">
                <ScoreCircle score={summary.overall_score} label="Overall Grade" primary />
              </div>
              
              {/* Detailed Scores */}
              <div className="flex justify-center gap-8 border-t lg:border-t-0 lg:border-l lg:border-r border-slate-100 py-8 lg:py-0 px-8 col-span-1">
                <ScoreCircle score={protocol_metrics?.reduce((a: number, b: any)=>a+b.score, 0) / (protocol_metrics?.length || 1) || summary.overall_score} label="Protocol" />
                <ScoreCircle score={summary.threshold_accuracy_score} label="Thresholds" />
                <ScoreCircle score={summary.interpretation_score} label="Interpretation" />
              </div>

              {/* Session Statistics */}
              <div className="flex flex-col justify-center gap-5 col-span-1">
                <h3 className="text-sm font-black text-slate-400 uppercase tracking-widest flex items-center gap-2 mb-2"><Activity size={16}/> Session Statistics</h3>
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 flex items-center justify-between">
                  <span className="text-slate-500 font-bold text-sm flex items-center gap-2"><Clock size={16} className="text-primary-500" /> Duration</span>
                  <span className="font-black text-slate-800 text-lg">{Math.floor((summary.duration_seconds || 0) / 60)}m {(summary.duration_seconds || 0) % 60}s</span>
                </div>
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 flex items-center justify-between">
                  <span className="text-slate-500 font-bold text-sm flex items-center gap-2"><LineChart size={16} className="text-emerald-500" /> Total Thresholds</span>
                  <span className="font-black text-slate-800 text-lg">{detectedThresholds.length}</span>
                </div>
              </div>
            </div>
          </section>

          {/* ── Audiogram Comparison ── */}
          <section className="bg-white rounded-3xl p-10 shadow-2xl border border-slate-100 mb-12">
            <div className="flex items-center justify-between mb-8 max-sm:flex-col gap-4">
              <h3 className="font-extrabold text-2xl text-slate-800 flex items-center gap-3">
                <Target size={28} className="text-primary-500" />
                Audiogram Analysis
              </h3>
              <div className="bg-slate-100 p-1.5 rounded-xl flex gap-1 shadow-inner border border-slate-200">
                {(['both', 'detected', 'actual'] as const).map(mode => (
                  <button key={mode} onClick={() => setCompareMode(mode)} className={clsx("px-5 py-2 rounded-lg text-sm font-bold capitalize transition-all", compareMode === mode ? "bg-white text-slate-800 shadow-sm" : "text-slate-500 hover:text-slate-700")}>
                    {mode === 'both' ? 'Comparison' : mode}
                  </button>
                ))}
              </div>
            </div>
             
            <div className="grid lg:grid-cols-2 gap-6">
              <div className="bg-slate-50 border border-slate-100 rounded-2xl p-6 overflow-hidden">
                <div className="flex items-center gap-3 mb-5">
                  <span className="w-3 h-3 rounded-full bg-red-500 shadow-sm shadow-red-500/30"></span>
                  <h4 className="text-lg font-extrabold text-slate-800 uppercase tracking-wide">Right Ear</h4>
                </div>
                <div className="flex items-center justify-center">
                  <div className="w-full max-w-xl flex items-center justify-center">
                    <AudiogramChart
                      storedThresholds={compareMode === 'actual' ? [] : rightDetectedThresholds}
                      actualThresholds={compareMode === 'detected' ? undefined : rightActualThresholds}
                      compact
                    />
                  </div>
                </div>
              </div>

              <div className="bg-slate-50 border border-slate-100 rounded-2xl p-6 overflow-hidden">
                <div className="flex items-center gap-3 mb-5">
                  <span className="w-3 h-3 rounded-full bg-blue-500 shadow-sm shadow-blue-500/30"></span>
                  <h4 className="text-lg font-extrabold text-slate-800 uppercase tracking-wide">Left Ear</h4>
                </div>
                <div className="flex items-center justify-center">
                  <div className="w-full max-w-xl flex items-center justify-center">
                    <AudiogramChart
                      storedThresholds={compareMode === 'actual' ? [] : leftDetectedThresholds}
                      actualThresholds={compareMode === 'detected' ? undefined : leftActualThresholds}
                      compact
                    />
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* ── Threshold Details Table ── */}
          <section className="bg-white rounded-3xl p-10 shadow-2xl border border-slate-100 mb-12">
            <h3 className="font-extrabold text-2xl text-slate-800 mb-8 flex items-center gap-3">
              <BarChart3 size={28} className="text-primary-500" /> Threshold Comparison
            </h3>
            <div className="overflow-hidden rounded-2xl border border-slate-200 shadow-sm">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider block">
                  <tr className="table w-full table-fixed">
                    <th className="px-6 py-5">Ear & Test</th>
                    <th className="px-6 py-5">Frequency</th>
                    <th className="px-6 py-5">Detected</th>
                    <th className="px-6 py-5">Actual</th>
                    <th className="px-6 py-5">Difference</th>
                    <th className="px-6 py-5">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-medium bg-white block max-h-[300px] overflow-y-auto w-full">
                  {threshold_comparisons?.map((tc: any, i: number) => (
                    <tr key={i} className="hover:bg-slate-50/50 transition-colors table w-full table-fixed">
                      <td className="px-6 py-4 flex items-center gap-3">
                        <span className={clsx("w-3 h-3 rounded-full shadow-sm", tc.ear_side === 'right' ? "bg-red-500 shadow-red-500/30" : "bg-blue-500 shadow-blue-500/30")}></span>
                        <span className="capitalize font-bold text-slate-700">{tc.ear_side}</span>
                        <span className="text-[10px] uppercase text-slate-500 font-black px-2 py-1 bg-slate-100 rounded-md border border-slate-200">{tc.test_type.replace('_', ' ')}</span>
                      </td>
                      <td className="px-6 py-4 text-slate-600 font-bold">{tc.frequency} Hz</td>
                      <td className="px-6 py-4 font-black text-slate-800">{tc.detected_is_no_response ? 'NR' : `${tc.detected_threshold_db} dB`}</td>
                      <td className="px-6 py-4 font-black text-slate-500">{tc.true_is_no_response ? 'NR' : `${tc.true_threshold_db} dB`}</td>
                      <td className="px-6 py-4">
                        {tc.absolute_error_db !== null ? (
                           <span className={clsx("px-2.5 py-1 rounded-lg font-bold text-xs uppercase tracking-widest", tc.absolute_error_db === 0 ? "bg-emerald-100 text-emerald-700" : tc.absolute_error_db <= 5 ? "bg-amber-100 text-amber-700" : "bg-rose-100 text-rose-700")}>{tc.absolute_error_db} dB</span>
                        ) : <span className="text-slate-300">-</span>}
                      </td>
                      <td className="px-6 py-4">
                        <span className={clsx("capitalize font-black text-sm", tc.status === 'exact' ? "text-emerald-500" : tc.status === 'close' ? "text-amber-500" : "text-rose-500")}>{tc.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <div className="grid lg:grid-cols-3 gap-8 pt-8">
            
            <div className="space-y-8">
              {/* ── AI Feedback ── */}
              {ai_feedback && (
                <section className="card p-8 bg-gradient-to-br from-indigo-900 via-slate-800 to-indigo-900 text-white shadow-2xl shadow-indigo-900/40 relative overflow-hidden h-full">
                  
                  <div className="absolute top-0 right-0 opacity-10 p-4">
                    <BrainCircuit size={120} strokeWidth={1} />
                  </div>

                  <div className="relative z-10">
                    <div className="flex items-center gap-3 mb-6 mix-blend-screen text-indigo-300">
                      <Sparkles size={24} />
                      <h3 className="font-extrabold tracking-widest uppercase text-sm">AI Coach Feedback</h3>
                    </div>
                    
                    <p className="text-white text-base leading-relaxed mb-8 bg-white/5 p-5 rounded-2xl border border-white/10 backdrop-blur-md shadow-inner">
                      {ai_feedback.summary}
                    </p>

                    <div className="space-y-6">
                      <div className="bg-emerald-500/10 p-4 rounded-2xl border border-emerald-500/20">
                        <h4 className="text-xs font-black uppercase tracking-widest text-emerald-400 mb-3 flex items-center gap-2">
                          <CheckCircle size={14} /> Strengths
                        </h4>
                        <ul className="space-y-2 text-sm text-emerald-50 font-medium">
                          {ai_feedback.strengths.map((str, idx) => (
                            <li key={idx} className="flex gap-2 isolate">
                              <span className="text-emerald-500/50 mt-0.5">•</span>
                              <span>{str}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div className="bg-rose-500/10 p-4 rounded-2xl border border-rose-500/20">
                        <h4 className="text-xs font-black uppercase tracking-widest text-rose-400 mb-3 flex items-center gap-2">
                          <Target size={14} /> Areas for Improvement
                        </h4>
                        <ul className="space-y-2 text-sm text-rose-50 font-medium">
                          {ai_feedback.improvement_points.map((pt, idx) => (
                            <li key={idx} className="flex gap-2 isolate">
                              <span className="text-rose-500/50 mt-0.5">•</span>
                              <span>{pt}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                </section>
              )}
            </div>

            <div className="lg:col-span-2 space-y-8">
              {/* ── Interpretation Evaluations ── */}
              <section className="grid sm:grid-cols-2 gap-6">
                {interpretation_evaluations.map((ie, i) => (
                  <div key={i} className={`card p-6 border-t-8 ${ie.ear_side === 'right' ? 'border-t-red-500' : 'border-t-blue-500'} shadow-xl shadow-slate-200/50`}>
                    <div className="flex justify-between items-start mb-6">
                      <h3 className="font-extrabold text-slate-800 text-lg uppercase tracking-wider flex items-center gap-2">
                        <span className={`w-3 h-3 rounded-full ${ie.ear_side==='right'?'bg-red-500':'bg-blue-500'}`}></span>
                        {ie.ear_side} Ear Diagnosis
                      </h3>
                      <span className={clsx("font-black text-xl", ie.score >= 80 ? "text-emerald-500" : "text-amber-500")}>{ie.score}%</span>
                    </div>
                    <div className="space-y-4">
                      {ie.field_scores.map((fs, idx) => (
                        <div key={idx} className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                          <div className="flex justify-between mb-2 text-[10px] font-black text-slate-400 uppercase tracking-widest">
                            <span>{fs.field_name.replace('_', ' ')}</span>
                            <span className={getFieldScoreBadge(fs).className}>
                              {getFieldScoreBadge(fs).label}
                            </span>
                          </div>
                          
                          <div className="flex gap-4">
                            <div className="flex-1">
                               <span className="block text-slate-800 font-bold text-sm bg-white border border-slate-200 px-2 py-1 rounded shadow-sm">{String(fs.submitted_value)}</span>
                               {fs.status !== 'undetermined' && fs.status !== 'missing' && Number(fs.score) < 100 && <span className="text-[10px] text-slate-400 font-bold ml-1">Your Ans</span>}
                            </div>
                            {fs.status !== 'undetermined' && fs.status !== 'missing' && Number(fs.score) < 100 && (
                              <div className="flex-1">
                                <span className="block text-emerald-700 font-bold text-sm bg-emerald-50 border border-emerald-200 px-2 py-1 rounded shadow-sm">{String(fs.expected_value)}</span>
                                <span className="text-[10px] text-emerald-600/70 font-bold ml-1">Correct</span>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </section>

              {/* ── Protocol Metrics ── */}
              <section className="card overflow-hidden shadow-xl shadow-slate-200/50 border-0">
                <button onClick={() => setShowDetails(!showDetails)} className="w-full bg-slate-800 px-6 py-5 flex items-center justify-between text-white hover:bg-slate-700 transition-colors">
                  <h3 className="font-extrabold flex items-center gap-3 text-lg"><Target size={20} className="text-primary-400" /> Protocol Metrics Breakdown</h3>
                  <ChevronDown className={clsx("transition-transform duration-300", showDetails ? "rotate-180" : "rotate-0")} />
                </button>
                
                <div className={clsx("divide-y divide-slate-100 transition-all duration-300", showDetails ? "block" : "hidden")}>
                  {protocol_metrics.map((pm, i) => (
                    <div key={i} className="p-6 hover:bg-slate-50 transition-colors flex max-sm:flex-col items-center gap-4">
                      {pm.score === 100 ? (
                        <div className="w-12 h-12 rounded-full bg-emerald-100 text-emerald-500 flex items-center justify-center flex-none">
                          <CheckCircle size={24} strokeWidth={2.5} />
                        </div>
                      ) : (
                        <div className="w-12 h-12 rounded-full bg-amber-100 text-amber-500 flex items-center justify-center flex-none">
                          <AlertTriangle size={24} strokeWidth={2.5} />
                        </div>
                      )}
                      
                      <div className="flex-1 text-center sm:text-left">
                        <h4 className="font-bold text-slate-800 text-lg">{pm.label}</h4>
                        <p className="text-sm border-l-2 border-slate-200 pl-3 ml-1 mt-1 text-slate-500 font-medium leading-relaxed">{pm.details}</p>
                      </div>
                      
                      <div className="flex-none text-right">
                        <span className={clsx("font-black text-2xl tracking-tighter", pm.score >= 80 ? "text-emerald-500" : pm.score >= 50 ? "text-amber-500" : "text-rose-500")}>
                          {pm.score}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </section>

            </div>

          </div>
        </main>
      </div>
    </div>
  );
}
