import type { AttemptDTO, StoredThreshold } from '../types';
import { Volume2 } from 'lucide-react';

interface AttemptHistoryProps {
  attempts: AttemptDTO[];
  storedThresholds?: StoredThreshold[];
}

function getSymbol(ear: string, testType: string, nr = false): string {
  const map: Record<string, string> = {
    'right-AC':        'O',
    'left-AC':         'X',
    'right-AC_masked': '△',
    'left-AC_masked':  '□',
    'right-BC':        '<',
    'left-BC':         '>',
    'right-BC_masked': '[',
    'left-BC_masked':  ']',
  };
  const key = `${ear}-${testType}`;
  const sym = map[key] ?? '?';
  return nr ? sym + '↓' : sym;
}

export default function AttemptHistory({ attempts, storedThresholds }: AttemptHistoryProps) {
  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center gap-2 mb-3 flex-none">
        <Volume2 size={15} className="text-primary-500" />
        <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">Attempt History</span>
      </div>

      {/* Scrollable list */}
      <div className="flex-1 overflow-y-auto space-y-1.5 min-h-0 pr-1">
        {attempts.length === 0 && (!storedThresholds || storedThresholds.length === 0) ? (
          <div className="flex flex-col items-center justify-center h-24 text-slate-400">
            <Volume2 size={22} className="mb-1 opacity-40" />
            <p className="text-xs">No entries yet</p>
          </div>
        ) : (
          (() => {
            const merged = [
              ...attempts.map(a => ({ type: 'attempt' as const, data: a, time: a.created_at })),
              ...(storedThresholds || []).map(st => ({ type: 'store' as const, data: st as any, time: st.created_at }))
            ].sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime());

            return merged.map((evt, i) => {
              if (evt.type === 'store') {
                const st = evt.data;
                return (
                  <div key={`st-${st.id}`} className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs border transition-all bg-amber-100 border-amber-300 text-amber-900 shadow-sm relative">
                    <span className="font-bold w-5 text-[14px] text-center flex-none text-amber-600">
                      {getSymbol(st.ear_side, st.test_type, st.is_no_response)}
                    </span>
                    <span className="font-semibold flex-none">{st.frequency} Hz</span>
                    <span className="flex-none font-bold">{st.threshold_db} dB</span>
                    <span className="ml-auto font-bold flex-none text-[10px] uppercase tracking-widest px-1.5 py-0.5 rounded bg-amber-200/50 text-amber-700">
                      STORED
                    </span>
                  </div>
                );
              } else {
                const a = evt.data;
                return (
                  <div
                    key={`at-${a.id}`}
                    className={`flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs border transition-all
                      ${a.response === 'heard'
                        ? 'bg-emerald-50 border-emerald-100 text-emerald-800'
                        : 'bg-rose-50 border-rose-100 text-rose-800'
                      }`}
                  >
                    <span
                      className={`font-bold w-5 text-[14px] text-center flex-none
                        ${a.ear_side === 'right' ? 'text-red-500' : 'text-blue-500'}`}
                    >
                      {getSymbol(a.ear_side, a.test_type)}
                    </span>
                    <span className="font-semibold flex-none">{a.frequency} Hz</span>
                    <span className="flex-none font-bold">{a.intensity} dB</span>
                    <span
                      className={`ml-auto font-bold flex-none text-[10px] uppercase tracking-widest px-1.5 py-0.5 rounded
                        ${a.response === 'heard' ? 'text-emerald-600' : 'text-rose-500'}`}
                    >
                      {a.response === 'heard' ? '✓' : '✗'}
                    </span>
                  </div>
                );
              }
            });
          })()
        )}
      </div>
    </div>
  );
}
