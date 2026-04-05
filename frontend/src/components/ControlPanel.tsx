import { useState, useCallback, useRef } from 'react';
import type { EarSide, TestType, StoredThreshold } from '../types';
import { Minus, Plus, Headphones, Save, XCircle, Power } from 'lucide-react';
import clsx from 'clsx';

const AC_FREQS = [125, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000];
const BC_FREQS = [500, 750, 1000, 1500, 2000, 3000, 4000];
const STEP_DEDUPE_MS = 140;
const ACTION_DEDUPE_MS = 250;

function deriveTestType(conduction: 'AC' | 'BC', maskingEnabled: boolean): TestType {
  if (conduction === 'AC') return maskingEnabled ? 'AC_masked' : 'AC';
  return maskingEnabled ? 'BC_masked' : 'BC';
}

interface ControlPanelProps {
  sessionId: number;
  onPlayTone: (params: {
    ear_side: EarSide;
    test_type: TestType;
    frequency: number;
    intensity: number;
    masking_level_db: number | null;
  }) => Promise<'heard' | 'not_heard' | void | undefined>;
  onStoreTone: (params: {
    ear_side: EarSide;
    test_type: TestType;
    frequency: number;
    threshold_db: number;
    is_no_response: boolean;
  }) => Promise<void>;
  lastResponse: 'heard' | 'not_heard' | null;
  isLoading: boolean;
  storedThresholds: StoredThreshold[];
  canStoreToneForSelection: (params: {
    ear_side: EarSide;
    test_type: TestType;
    frequency: number;
    threshold_db: number;
  }) => boolean;
}

function IntensityStepper({
  label,
  value,
  min,
  max,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  onChange: (v: number) => void;
}) {
  const step = 5;

  return (
    <div>
      <label className="label">{label}</label>
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={() => onChange(Math.max(min, value - step))}
          className="flex-none w-10 h-10 rounded-xl border border-slate-200 bg-white hover:bg-slate-50
                     flex items-center justify-center text-slate-500 hover:text-slate-800 hover:border-slate-300
                     shadow-sm transition-all active:scale-95 disabled:opacity-40 disabled:hover:scale-100"
          disabled={value <= min}
        >
          <Minus size={18} strokeWidth={2.5} />
        </button>
        <div className="flex-1 text-center bg-slate-800 rounded-xl py-2 px-3 shadow-inner border border-slate-900 border-t-slate-700">
          <span className="text-2xl font-black text-white font-mono tracking-tight">{value}</span>
          <span className="text-xs font-bold text-slate-400 ml-1.5 uppercase tracking-widest">dB</span>
        </div>
        <button
          type="button"
          onClick={() => onChange(Math.min(max, value + step))}
          className="flex-none w-10 h-10 rounded-xl border border-slate-200 bg-white hover:bg-slate-50
                     flex items-center justify-center text-slate-500 hover:text-slate-800 hover:border-slate-300
                     shadow-sm transition-all active:scale-95 disabled:opacity-40 disabled:hover:scale-100"
          disabled={value >= max}
        >
          <Plus size={18} strokeWidth={2.5} />
        </button>
      </div>
      <div className="mt-2 flex justify-between text-[10px] uppercase font-bold tracking-widest text-slate-400 px-1">
        <span>Min {min} dB</span>
        <span>Max {max} dB</span>
      </div>
    </div>
  );
}

function FrequencyStepper({
  label,
  value,
  freqs,
  onChange,
}: {
  label: string;
  value: number;
  freqs: number[];
  onChange: (v: number) => void;
}) {
  const currentIndex = freqs.indexOf(value);
  const displayValue = value >= 1000 ? `${value / 1000}k` : value;

  return (
    <div className="mb-5">
      <label className="label">{label}</label>
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={() => onChange(freqs[currentIndex - 1])}
          className="flex-none w-10 h-10 rounded-xl border border-slate-200 bg-white hover:bg-slate-50
                     flex items-center justify-center text-slate-500 hover:text-slate-800 hover:border-slate-300
                     shadow-sm transition-all active:scale-95 disabled:opacity-40 disabled:hover:scale-100"
          disabled={currentIndex <= 0}
        >
          <Minus size={18} strokeWidth={2.5} />
        </button>
        <div className="flex-1 text-center bg-slate-800 rounded-xl py-2 px-3 shadow-inner border border-slate-900 border-t-slate-700">
          <span className="text-2xl font-black text-white font-mono tracking-tight">{displayValue}</span>
          <span className="text-xs font-bold text-slate-400 ml-1.5 uppercase tracking-widest">Hz</span>
        </div>
        <button
          type="button"
          onClick={() => onChange(freqs[currentIndex + 1])}
          className="flex-none w-10 h-10 rounded-xl border border-slate-200 bg-white hover:bg-slate-50
                     flex items-center justify-center text-slate-500 hover:text-slate-800 hover:border-slate-300
                     shadow-sm transition-all active:scale-95 disabled:opacity-40 disabled:hover:scale-100"
          disabled={currentIndex >= freqs.length - 1}
        >
          <Plus size={18} strokeWidth={2.5} />
        </button>
      </div>
      <div className="mt-2 flex justify-between text-[10px] uppercase font-bold tracking-widest text-slate-400 px-1">
        <span>Min {freqs[0] >= 1000 ? `${freqs[0] / 1000}k` : freqs[0]} Hz</span>
        <span>Max {freqs[freqs.length - 1] >= 1000 ? `${freqs[freqs.length - 1] / 1000}k` : freqs[freqs.length - 1]} Hz</span>
      </div>
    </div>
  );
}

export default function ControlPanel({
  onPlayTone,
  onStoreTone,
  lastResponse,
  isLoading,
  storedThresholds,
  canStoreToneForSelection,
}: ControlPanelProps) {
  const [ear, setEar] = useState<EarSide>('right');
  const [conduction, setConduction] = useState<'AC' | 'BC'>('AC');
  const [frequency, setFrequency] = useState(1000);
  const [intensity, setIntensity] = useState(40);
  const [maskingEnabled, setMaskingEnabled] = useState(false);
  const [maskingLevel, setMaskingLevel] = useState(30);

  const intensityClickAtRef = useRef(0);
  const frequencyClickAtRef = useRef(0);
  const maskingClickAtRef = useRef(0);
  const toggleClickAtRef = useRef(0);
  const playClickAtRef = useRef(0);
  const storeClickAtRef = useRef(0);

  const freqs = conduction === 'AC' ? AC_FREQS : BC_FREQS;
  const intensityMax = conduction === 'AC' ? 120 : 70;
  const testType = deriveTestType(conduction, maskingEnabled);
  const maskingEar: EarSide = ear === 'right' ? 'left' : 'right';

  const acceptClick = useCallback((ref: React.MutableRefObject<number>, windowMs: number) => {
    const now = Date.now();
    if ((now - ref.current) < windowMs) {
      return false;
    }
    ref.current = now;
    return true;
  }, []);

  const handleConduction = useCallback((nextConduction: 'AC' | 'BC') => {
    if (!acceptClick(toggleClickAtRef, STEP_DEDUPE_MS)) return;
    setConduction(nextConduction);
    const allowed = nextConduction === 'AC' ? AC_FREQS : BC_FREQS;
    if (!allowed.includes(frequency)) setFrequency(1000);
    if (nextConduction === 'BC' && intensity > 70) setIntensity(70);
  }, [acceptClick, frequency, intensity]);

  const handleEarSelect = useCallback((nextEar: EarSide) => {
    if (!acceptClick(toggleClickAtRef, STEP_DEDUPE_MS)) return;
    setEar(nextEar);
  }, [acceptClick]);

  const handleFrequencyChange = useCallback((nextFrequency: number) => {
    if (!acceptClick(frequencyClickAtRef, STEP_DEDUPE_MS)) return;
    setFrequency(nextFrequency);
  }, [acceptClick]);

  const handleIntensityChange = useCallback((nextIntensity: number) => {
    if (!acceptClick(intensityClickAtRef, STEP_DEDUPE_MS)) return;
    setIntensity(nextIntensity);
  }, [acceptClick]);

  const handleMaskingLevelChange = useCallback((nextMaskingLevel: number) => {
    if (!acceptClick(maskingClickAtRef, STEP_DEDUPE_MS)) return;
    setMaskingLevel(nextMaskingLevel);
  }, [acceptClick]);

  const handleMaskingToggle = useCallback(() => {
    if (!acceptClick(toggleClickAtRef, STEP_DEDUPE_MS)) return;
    setMaskingEnabled((value) => !value);
  }, [acceptClick]);

  const handlePlay = async () => {
    if (!acceptClick(playClickAtRef, ACTION_DEDUPE_MS)) return;
    await onPlayTone({
      ear_side: ear,
      test_type: testType,
      frequency,
      intensity,
      masking_level_db: maskingEnabled ? maskingLevel : null,
    });
  };

  const handleStore = async (noResponse: boolean) => {
    if (!acceptClick(storeClickAtRef, ACTION_DEDUPE_MS)) return;
    await onStoreTone({
      ear_side: ear,
      test_type: testType,
      frequency,
      threshold_db: intensity,
      is_no_response: noResponse,
    });
  };

  const alreadyStored = storedThresholds.some(
    (threshold) =>
      threshold.ear_side === ear &&
      threshold.test_type === testType &&
      threshold.frequency === frequency
  );

  const canStoreCurrentSelection = canStoreToneForSelection({
    ear_side: ear,
    test_type: testType,
    frequency,
    threshold_db: intensity,
  });

  const toneStyle = lastResponse === 'heard'
    ? 'bg-emerald-500 hover:bg-emerald-600 text-white shadow-[0_0_20px_rgba(16,185,129,0.5)] border-emerald-400'
    : lastResponse === 'not_heard'
      ? 'bg-rose-500 hover:bg-rose-600 text-white shadow-[0_0_20px_rgba(244,63,94,0.5)] border-rose-400'
      : 'bg-primary-600 hover:bg-primary-700 text-white shadow-[0_10px_20px_rgba(79,70,229,0.3)] border-primary-500';

  return (
    <div className="card p-6 shadow-xl shadow-slate-200/50 relative overflow-hidden">
      <div className="flex flex-col gap-6">
        <div className="flex flex-col md:flex-row gap-6">
          <div className="flex-1 bg-slate-50/50 rounded-2xl p-5 border border-slate-100 shadow-inner">
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-primary-700 flex items-center justify-center shadow-inner">
                  <span className="text-sm font-black text-white">1</span>
                </div>
                <span className="text-sm font-black text-slate-800 uppercase tracking-widest">Main Stimulus</span>
              </div>
              <div className="px-3 py-1 bg-white rounded-lg shadow-sm border border-slate-200 text-xs font-bold text-slate-500">
                Mode: <span className="text-primary-600 ml-1">{testType.replace('_', ' ')}</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-5">
              <div>
                <label className="label text-[10px]">Ear Selector</label>
                <div className="flex p-1 bg-white rounded-xl shadow-sm border border-slate-200">
                  {(['right', 'left'] as EarSide[]).map((earSide) => (
                    <button
                      key={earSide}
                      type="button"
                      onClick={() => handleEarSelect(earSide)}
                      className={clsx(
                        'flex-1 py-1.5 rounded-lg text-xs font-bold transition-all',
                        ear === earSide
                          ? earSide === 'right'
                            ? 'bg-red-500 text-white shadow-md shadow-red-500/30'
                            : 'bg-blue-500 text-white shadow-md shadow-blue-500/30'
                          : 'bg-transparent text-slate-500 hover:bg-slate-50'
                      )}
                    >
                      {earSide === 'right' ? 'Right' : 'Left'}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="label text-[10px]">Transducer</label>
                <div className="flex p-1 bg-white rounded-xl shadow-sm border border-slate-200">
                  {(['AC', 'BC'] as const).map((mode) => (
                    <button
                      key={mode}
                      type="button"
                      onClick={() => handleConduction(mode)}
                      className={clsx(
                        'flex-1 py-1.5 rounded-lg text-xs font-bold transition-all flex justify-center',
                        conduction === mode
                          ? 'bg-slate-800 text-white shadow-md'
                          : 'bg-transparent text-slate-500 hover:bg-slate-50'
                      )}
                    >
                      {mode === 'AC' ? 'AC' : 'BC'}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <FrequencyStepper
              label="Frequency (Hz)"
              value={frequency}
              freqs={freqs}
              onChange={handleFrequencyChange}
            />

            <IntensityStepper
              label="Stimulus Level"
              value={intensity}
              min={-10}
              max={intensityMax}
              onChange={handleIntensityChange}
            />
          </div>

          <div
            className={clsx(
              'flex-1 rounded-2xl p-5 border transition-all duration-300',
              maskingEnabled
                ? 'bg-amber-50/50 border-amber-200 shadow-inner'
                : 'bg-slate-50/40 border-slate-100 opacity-60'
            )}
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center shadow-inner">
                  <span className="text-sm font-black text-white">2</span>
                </div>
                <span className="text-sm font-black text-slate-800 uppercase tracking-widest">Masking</span>
              </div>
              <button
                type="button"
                onClick={handleMaskingToggle}
                className={clsx(
                  'px-3 py-1.5 rounded-lg text-[10px] uppercase font-bold transition-all flex items-center gap-1.5 shadow-sm border',
                  maskingEnabled
                    ? 'bg-amber-500 text-white border-amber-600 shadow-amber-500/30'
                    : 'bg-white text-slate-500 border-slate-200 hover:bg-slate-50 hover:text-slate-700'
                )}
              >
                <Power size={14} strokeWidth={3} />
                {maskingEnabled ? 'ACTIVE' : 'OFF'}
              </button>
            </div>

            <div className={clsx('transition-all duration-300', maskingEnabled ? '' : 'pointer-events-none opacity-40 grayscale')}>
              <div className="mb-4 flex items-center justify-between text-xs font-bold text-slate-500 bg-white border border-slate-200 rounded-xl px-3 py-2.5 shadow-sm">
                <span className="uppercase tracking-widest text-[10px]">Noise Routing</span>
                <span
                  className={clsx(
                    'px-2 py-0.5 rounded-md flex items-center gap-1.5',
                    maskingEar === 'right' ? 'bg-red-50 text-red-600' : 'bg-blue-50 text-blue-600'
                  )}
                >
                  <span className={clsx('w-2 h-2 rounded-full', maskingEar === 'right' ? 'bg-red-500' : 'bg-blue-500')} />
                  To {maskingEar === 'right' ? 'Right' : 'Left'} Ear
                </span>
              </div>

              <IntensityStepper
                label="Noise Level"
                value={maskingLevel}
                min={-10}
                max={120}
                onChange={handleMaskingLevelChange}
              />
            </div>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-100 flex flex-col items-center gap-3">
          <button
            type="button"
            onClick={handlePlay}
            disabled={isLoading}
            className={clsx(
              'relative w-full py-3 rounded-xl font-black text-base tracking-wide flex items-center justify-center gap-3',
              'transition-all duration-300 active:scale-95 border disabled:opacity-60 disabled:cursor-not-allowed group overflow-hidden shadow-md',
              toneStyle
            )}
          >
            <div className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity" />
            <Headphones size={22} className={isLoading ? 'animate-pulse' : ''} />
            <span className="relative z-10">{isLoading ? 'Stimulating...' : 'Present Tone'}</span>
          </button>

          <div className="w-full grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => handleStore(false)}
              disabled={isLoading || lastResponse === null || !canStoreCurrentSelection}
              className={clsx(
                'py-2.5 text-sm rounded-xl font-bold flex items-center justify-center gap-2',
                'transition-all duration-300 active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed border shadow-sm bg-white border-slate-200 text-slate-700 hover:border-emerald-300 hover:bg-emerald-50 hover:text-emerald-700'
              )}
            >
              <Save size={18} />
              Store
            </button>

            <button
              type="button"
              onClick={() => handleStore(true)}
              disabled={isLoading || !canStoreCurrentSelection}
              className="py-2.5 text-sm rounded-xl font-bold flex items-center justify-center gap-2
                         bg-white border border-slate-200 text-slate-700 hover:border-rose-300 hover:bg-rose-50 hover:text-rose-700
                         transition-all shadow-sm duration-300 active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <XCircle size={18} />
              Store NR
            </button>
          </div>

          {alreadyStored && (
            <div className="w-full rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-[11px] font-bold uppercase tracking-widest text-amber-700 text-center">
              A threshold is already stored for this slot. Saving again will replace the final value.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
