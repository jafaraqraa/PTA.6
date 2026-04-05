import { useState } from 'react';
import { useSessionStore } from '../store/sessionStore';
import { useEvaluation } from '../hooks/useEvaluation';
import Navbar from '../components/Navbar';
import AudiogramChart from '../components/AudiogramChart';
import type { EarSide, HearingType, HearingSeverity, HearingConfiguration, FinalInterpretationCreateDTO } from '../types';
import { Sparkles, ArrowRight, ShieldAlert, Activity, CheckCircle2 } from 'lucide-react';
import clsx from 'clsx';

const HEARING_TYPES: HearingType[] = ['Normal', 'Conductive', 'Sensorineural', 'Mixed'];
const SEVERITIES: HearingSeverity[] = ['Normal', 'Mild', 'Moderate', 'Moderately Severe', 'Severe', 'Profound', 'Undetermined'];
const CONFIGURATIONS: HearingConfiguration[] = ['All Frequencies', 'Low Frequencies', 'Mid Frequencies', 'High Frequencies', 'Single Frequency', 'Notch Pattern', 'Other', 'Undetermined'];

const ALLOWED_FREQS = [125, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000];

function validateInterpretation(data: FinalInterpretationCreateDTO): string | null {
  if (!data.overall_type) return 'Overall diagnosis is required.';
  if (!data.severity) return 'Degree of loss is required.';
  if (!data.configuration) return 'Configuration pattern is required.';

  const affected = data.affected_frequencies_hz || [];

  if (data.overall_type === 'Normal' && data.severity !== 'Normal') {
    return 'Normal hearing type must be paired with Normal severity.';
  }

  if (data.severity === 'Normal' && data.overall_type !== 'Normal') {
    return 'Normal severity can only be paired with Normal hearing type.';
  }

  if (data.overall_type === 'Normal' && affected.length > 0) {
    return 'Normal hearing interpretation should not include affected frequencies.';
  }

  if (data.configuration === 'Single Frequency' && affected.length !== 1) {
    return 'Single Frequency configuration requires exactly one affected frequency.';
  }

  const needsAffectedFreqs =
    ['All Frequencies', 'Low Frequencies', 'Mid Frequencies', 'High Frequencies', 'Notch Pattern'].includes(data.configuration) &&
    data.overall_type !== 'Normal';
  if (needsAffectedFreqs && affected.length === 0) {
    return 'This configuration requires affected frequencies to be selected.';
  }

  return null;
}

function InterpretationForm({ 
  ear, 
  data, 
  onChange,
  showErrors
}: { 
  ear: EarSide; 
  data: FinalInterpretationCreateDTO; 
  onChange: (d: FinalInterpretationCreateDTO) => void;
  showErrors: boolean;
}) {
  const isRight = ear === 'right';
  const colorClass = isRight ? 'text-red-600' : 'text-blue-600';
  const bgClass = isRight ? 'bg-red-50/50 border-red-200' : 'bg-blue-50/50 border-blue-200';
  const accentClass = isRight ? 'bg-red-500' : 'bg-blue-500';
  const severityOptions =
    data.overall_type === 'Normal'
      ? ['Normal']
      : SEVERITIES.filter((item) => item !== 'Normal');

  const updateField = (field: keyof FinalInterpretationCreateDTO, value: any) => {
    const next = { ...data, [field]: value };

    if (field === 'overall_type' && value === 'Normal') {
      next.severity = 'Normal';
      next.affected_frequencies_hz = [];
    }

    if (field === 'severity' && value === 'Normal') {
      next.overall_type = 'Normal';
      next.affected_frequencies_hz = [];
    }

    onChange(next);
  };

  const toggleFreq = (f: number) => {
    const current = data.affected_frequencies_hz || [];
    const updated = current.includes(f) ? current.filter(x => x !== f) : [...current, f].sort((a,b)=>a-b);
    updateField('affected_frequencies_hz', updated);
  };

  return (
    <div className={`card p-6 border-t-4 ${isRight ? 'border-t-red-500' : 'border-t-blue-500'} shadow-lg shadow-slate-200/50 hover:shadow-xl transition-shadow`}>
      <div className="flex items-center justify-between mb-8">
        <div className={`inline-flex items-center gap-2 px-4 py-1.5 rounded-xl border font-black uppercase tracking-widest ${colorClass} ${bgClass} shadow-sm`}>
          <div className={`w-2.5 h-2.5 rounded-full ${accentClass} shadow-sm`} />
          {isRight ? 'Right Ear' : 'Left Ear'}
        </div>
        
        {data.overall_type && data.severity && data.configuration && (
          <CheckCircle2 size={24} className="text-emerald-500 animate-slide-up" />
        )}
      </div>

      <div className="space-y-6">
        {/* Type */}
        <div>
          <label className={clsx("label flex justify-between", showErrors && !data.overall_type && "text-rose-500")}>Overall Diagnosis {showErrors && !data.overall_type && <span className="text-[10px] text-rose-500 font-bold uppercase">* Required</span>}</label>
          <div className="relative">
            <select 
              className={clsx("input w-full cursor-pointer appearance-none font-medium text-slate-700 bg-white", showErrors && !data.overall_type && "border-rose-300 ring-2 ring-rose-100")}
              value={data.overall_type || ''}
              onChange={(e) => updateField('overall_type', e.target.value)}
            >
              <option value="" disabled>Select Hearing Type...</option>
              {HEARING_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
            <div className="absolute inset-y-0 right-4 flex items-center pointer-events-none">
              <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
            </div>
          </div>
        </div>

        {/* Severity */}
        <div>
          <label className={clsx("label flex justify-between", showErrors && !data.severity && "text-rose-500")}>Degree of Loss {showErrors && !data.severity && <span className="text-[10px] text-rose-500 font-bold uppercase">* Required</span>}</label>
          <div className="relative">
            <select 
              className={clsx("input w-full cursor-pointer appearance-none font-medium text-slate-700 bg-white", showErrors && !data.severity && "border-rose-300 ring-2 ring-rose-100")}
              value={data.severity || ''}
              onChange={(e) => updateField('severity', e.target.value)}
            >
              <option value="" disabled>Select Severity...</option>
              {severityOptions.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
            <div className="absolute inset-y-0 right-4 flex items-center pointer-events-none">
              <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
            </div>
          </div>
        </div>

        {/* Configuration */}
        <div>
          <label className={clsx("label flex justify-between", showErrors && !data.configuration && "text-rose-500")}>Configuration Pattern {showErrors && !data.configuration && <span className="text-[10px] text-rose-500 font-bold uppercase">* Required</span>}</label>
          <div className="relative">
            <select 
              className={clsx("input w-full cursor-pointer appearance-none font-medium text-slate-700 bg-white", showErrors && !data.configuration && "border-rose-300 ring-2 ring-rose-100")}
              value={data.configuration || ''}
              onChange={(e) => updateField('configuration', e.target.value)}
            >
              <option value="" disabled>Select Configuration...</option>
              {CONFIGURATIONS.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
            <div className="absolute inset-y-0 right-4 flex items-center pointer-events-none">
              <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
            </div>
          </div>
        </div>

        {/* Affected Frequencies */}
        <div className={clsx(data.overall_type === 'Normal' && 'opacity-40 grayscale pointer-events-none transition-all')}>
          <label className="label flex justify-between items-end mb-3">
            <span>Affected Frequencies</span>
            <span className="text-[10px] text-slate-400 font-bold bg-slate-100 px-2 py-0.5 rounded-full border border-slate-200 uppercase tracking-widest">Optional</span>
          </label>
          <div className="flex flex-wrap gap-2">
            {ALLOWED_FREQS.map(f => (
              <button
                key={f} type="button"
                onClick={() => toggleFreq(f)}
                className={clsx(
                  'px-2.5 py-1.5 rounded-lg border text-xs font-bold transition-all shadow-sm',
                  (data.affected_frequencies_hz || []).includes(f)
                    ? 'bg-slate-800 text-white border-slate-800 shadow-slate-900/30 ring-2 ring-slate-800/20 ring-offset-1'
                    : 'bg-white text-slate-500 border-slate-200 hover:border-slate-400 hover:text-slate-800'
                )}
              >
                {f >= 1000 ? `${f/1000}k` : f}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Interpretation() {
  const { session, storedThresholds } = useSessionStore();
  const { submitInterpretation, loading, error } = useEvaluation();

  const [rightData, setRightData] = useState<FinalInterpretationCreateDTO>({ ear_side: 'right', affected_frequencies_hz: [] });
  const [leftData, setLeftData] = useState<FinalInterpretationCreateDTO>({ ear_side: 'left', affected_frequencies_hz: [] });
  const [showErrors, setShowErrors] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const isFormComplete = rightData.overall_type && rightData.severity && rightData.configuration &&
                         leftData.overall_type && leftData.severity && leftData.configuration;

  const handleSubmit = () => {
    if (!isFormComplete) {
      setShowErrors(true);
      return;
    }

    const rightError = validateInterpretation(rightData);
    if (rightError) {
      setShowErrors(true);
      setValidationError(`Right ear: ${rightError}`);
      return;
    }

    const leftError = validateInterpretation(leftData);
    if (leftError) {
      setShowErrors(true);
      setValidationError(`Left ear: ${leftError}`);
      return;
    }

    setValidationError(null);
    submitInterpretation([rightData, leftData]);
  };

  return (
    <div className="min-h-screen bg-slate-50 pb-32 relative overflow-hidden selection:bg-indigo-100">
      
      <div className="absolute top-[-20%] left-[10%] w-[600px] h-[600px] bg-primary-200/20 rounded-full blur-[120px] pointer-events-none -z-10" />

      <div className="glass-nav relative z-20">
        <Navbar 
          rightContent={
            <div className="flex items-center gap-3">
              <span className="badge badge-slate shadow-sm bg-white border border-slate-200 px-3 py-1.5 text-xs font-black uppercase tracking-widest">
                Step 3 of 4
              </span>
              <span className="flex items-center gap-2 text-primary-600 font-bold bg-primary-50 px-3 py-1.5 rounded-lg border border-primary-100">
                <Sparkles size={16} /> Interpretation
              </span>
            </div>
          } 
        />
      </div>

      <main className="max-w-5xl mx-auto px-4 mt-12 animate-fade-in relative z-10">
        
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-100 to-primary-200 text-primary-600 mb-6 shadow-inner">
            <Activity size={32} />
          </div>
          <h1 className="text-4xl font-extrabold text-slate-800 tracking-tight mb-3">Clinical Evaluation</h1>
          <p className="text-slate-500 mt-2 text-lg font-medium max-w-2xl mx-auto">
            Analyze the audiogram below and provide your clinical diagnosis for each ear. This simulates the reporting phase.
          </p>
        </div>

        {(validationError || error) && (
          <div className="mb-8 p-4 bg-rose-50 border border-rose-200 rounded-2xl flex items-start gap-4 text-rose-800 shadow-sm animate-slide-up">
            <ShieldAlert size={24} className="flex-none mt-0.5" />
            <div className="text-sm font-bold leading-relaxed">{validationError || error}</div>
          </div>
        )}

        <div className="card p-6 mb-10 shadow-lg shadow-slate-200/40 border-0 bg-white/90">
          <div className="flex items-center justify-between mb-6 px-4">
            <h2 className="text-sm font-black text-slate-400 uppercase tracking-widest">Generated Audiogram</h2>
            <div className="flex gap-4">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                 <span className="w-2.5 h-2.5 rounded-full bg-red-400"></span> Right
              </span>
              <span className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                 <span className="w-2.5 h-2.5 rounded-full bg-blue-400"></span> Left
              </span>
            </div>
          </div>
          <div className="bg-slate-50/50 rounded-2xl p-4 border border-slate-100 shadow-inner flex justify-center">
            <div className="w-full max-w-3xl">
              <AudiogramChart storedThresholds={storedThresholds} compact />
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-8 mb-12">
          <InterpretationForm ear="right" data={rightData} onChange={setRightData} showErrors={showErrors} />
          <InterpretationForm ear="left" data={leftData} onChange={setLeftData} showErrors={showErrors} />
        </div>

        <div className="fixed bottom-0 left-0 right-0 p-4 glass-nav border-t border-slate-200 flex justify-center shadow-[0_-10px_30px_rgba(0,0,0,0.05)] z-50">
          <div className="max-w-5xl w-full flex items-center justify-between px-4">
            <span className="text-sm font-bold text-slate-500">
              {isFormComplete ? 'Ready to submit!' : 'Please complete both ears.'}
            </span>
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="btn-primary py-4 px-10 text-lg shadow-xl shadow-primary-500/30 hover:shadow-primary-500/50"
            >
              {loading ? (
                <>Analyzing...</>
              ) : (
                <>
                  Submit for Evaluation
                  <ArrowRight size={20} className="ml-2" />
                </>
              )}
            </button>
          </div>
        </div>

      </main>
    </div>
  );
}
