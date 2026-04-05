import { useMemo } from 'react';
import type { StoredThreshold } from '../types';

const AC_FREQS = [125, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000];
const ALL_FREQS = AC_FREQS;
const DB_MIN = -10;
const DB_MAX = 120;
const DB_STEP = 10;

const ML = 48;
const MR = 24;
const MT = 28;
const MB = 36;

interface LineGroup {
  key: string;
  color: string;
  dashed: boolean;
  pts: StoredThreshold[];
}

interface AudiogramChartProps {
  storedThresholds: StoredThreshold[];
  actualThresholds?: StoredThreshold[];
  compact?: boolean;
}

function getSymbol(threshold: StoredThreshold): string {
  const symbols: Record<string, string> = {
    'right-AC': 'O',
    'left-AC': 'X',
    'right-AC_masked': '△',
    'left-AC_masked': '□',
    'right-BC': '<',
    'left-BC': '>',
    'right-BC_masked': '[',
    'left-BC_masked': ']',
  };

  return symbols[`${threshold.ear_side}-${threshold.test_type}`] ?? '?';
}

function getColor(ear: string): string {
  return ear === 'right' ? '#ef4444' : '#3b82f6';
}

function getTestTypeOffset(testType: string, compact: boolean): number {
  const unit = compact ? 8 : 12;
  const offsets: Record<string, number> = {
    AC: -unit,
    AC_masked: -unit / 3,
    BC: unit / 3,
    BC_masked: unit,
  };

  return offsets[testType] ?? 0;
}

function buildLineGroups(thresholds: StoredThreshold[], fallbackColor?: string): LineGroup[] {
  const groups: Record<string, StoredThreshold[]> = {};

  thresholds.forEach((threshold) => {
    const key = `${threshold.ear_side}-${threshold.test_type}`;
    if (!groups[key]) groups[key] = [];
    groups[key].push(threshold);
  });

  return Object.entries(groups).map(([key, pts]) => ({
    key,
    color: fallbackColor ?? getColor(key.split('-')[0]),
    dashed: key.includes('BC'),
    pts: [...pts].sort((a, b) => a.frequency - b.frequency),
  }));
}

export default function AudiogramChart({
  storedThresholds,
  actualThresholds,
  compact = false,
}: AudiogramChartProps) {
  const W = compact ? 400 : 700;
  const H = compact ? 320 : 600;

  const innerW = W - ML - MR;
  const innerH = H - MT - MB;

  const xScale = useMemo(() => {
    const n = ALL_FREQS.length - 1;
    return (freq: number) => {
      const i = ALL_FREQS.indexOf(freq);
      return ML + (i / n) * innerW;
    };
  }, [innerW]);

  const yScale = (db: number) => {
    const ratio = (db - DB_MIN) / (DB_MAX - DB_MIN);
    return MT + ratio * innerH;
  };

  const plottedStoredThresholds = useMemo(
    () => storedThresholds.filter((threshold) => threshold.is_final),
    [storedThresholds]
  );

  const plottedActualThresholds = useMemo(
    () => (actualThresholds ?? []).filter((threshold) => threshold.is_final),
    [actualThresholds]
  );

  const getPointX = (threshold: StoredThreshold) =>
    xScale(threshold.frequency) + getTestTypeOffset(threshold.test_type, compact);

  const storedLines = useMemo(
    () => buildLineGroups(plottedStoredThresholds),
    [plottedStoredThresholds]
  );

  const actualLines = useMemo(
    () => buildLineGroups(plottedActualThresholds, '#94a3b8'),
    [plottedActualThresholds]
  );

  const renderLinesAndSymbols = (
    thresholds: StoredThreshold[],
    lineGroups: LineGroup[],
    isActual: boolean
  ) => (
    <g opacity={isActual ? 0.6 : 1}>
      {lineGroups.map(({ key, color, dashed, pts }) =>
        pts.filter((point) => !point.is_no_response).length > 1 ? (
          <polyline
            key={`line-${isActual ? 'actual' : 'detected'}-${key}`}
            points={pts
              .filter((point) => !point.is_no_response)
              .map((point) => `${getPointX(point)},${yScale(point.threshold_db)}`)
              .join(' ')}
            fill="none"
            stroke={color}
            strokeWidth={isActual ? 1.5 : 2}
            strokeDasharray={dashed ? '5 3' : undefined}
          />
        ) : null
      )}

      {thresholds.map((threshold) => {
        const x = getPointX(threshold);
        const y = threshold.is_no_response ? yScale(DB_MAX) + 8 : yScale(threshold.threshold_db);
        const color = isActual ? '#64748b' : getColor(threshold.ear_side);
        const fontSize = compact ? 14 : 18;

        return (
          <g key={`${isActual ? 'actual' : 'detected'}-${threshold.id}`}>
            <text
              x={x}
              y={y + fontSize / 3}
              textAnchor="middle"
              fontSize={fontSize}
              fontWeight={700}
              fill={color}
            >
              {getSymbol(threshold)}
            </text>
            {threshold.is_no_response && (
              <text
                x={x}
                y={y + fontSize}
                textAnchor="middle"
                fontSize={fontSize - 2}
                fill={color}
              >
                ↓
              </text>
            )}
          </g>
        );
      })}
    </g>
  );

  const dbLevels = [];
  for (let db = DB_MIN; db <= DB_MAX; db += DB_STEP) {
    dbLevels.push(db);
  }

  return (
    <div className="w-full">
      <svg
        viewBox={`0 0 ${W} ${H}`}
        width="100%"
        preserveAspectRatio="xMidYMid meet"
        style={{ width: '100%', height: 'auto', fontFamily: 'Inter, system-ui, sans-serif' }}
      >
        {dbLevels.map((db) => {
          const y = yScale(db);
          return (
            <g key={db}>
              <line
                x1={ML}
                y1={y}
                x2={ML + innerW}
                y2={y}
                stroke={db === 25 ? '#94a3b8' : '#e2e8f0'}
                strokeWidth={db === 25 ? 0.8 : 0.5}
                strokeDasharray={db === 25 ? '4 3' : undefined}
              />
              <text
                x={ML - 6}
                y={y + 4}
                textAnchor="end"
                fontSize={compact ? 12 : 14}
                fill="#64748b"
                fontWeight={700}
              >
                {db}
              </text>
            </g>
          );
        })}

        {ALL_FREQS.map((freq) => {
          const x = xScale(freq);
          return (
            <g key={freq}>
              <line x1={x} y1={MT} x2={x} y2={MT + innerH} stroke="#e2e8f0" strokeWidth={0.5} />
              <text
                x={x}
                y={MT - 8}
                textAnchor="middle"
                fontSize={compact ? 11 : 13}
                fill="#64748b"
                fontWeight={800}
              >
                {freq >= 1000 ? `${freq / 1000}k` : freq}
              </text>
            </g>
          );
        })}

        <rect x={ML} y={MT} width={innerW} height={yScale(25) - MT} fill="#f0fdf4" opacity={0.6} />

        <rect x={ML} y={MT} width={innerW} height={innerH} fill="none" stroke="#cbd5e1" strokeWidth={1} />

        <text
          x={ML + innerW / 2}
          y={H - 4}
          textAnchor="middle"
          fontSize={compact ? 8 : 10}
          fill="#64748b"
          fontWeight={600}
        >
          Frequency (Hz)
        </text>
        <text
          transform={`rotate(-90,${compact ? 10 : 12},${MT + innerH / 2})`}
          x={compact ? 10 : 12}
          y={MT + innerH / 2}
          textAnchor="middle"
          fontSize={compact ? 8 : 10}
          fill="#64748b"
          fontWeight={600}
        >
          Hearing Level (dB HL)
        </text>

        <g transform={`translate(${ML + innerW - (compact ? 80 : 120)}, ${MT + 6})`}>
          <rect width={compact ? 78 : 118} height={compact ? 28 : 34} rx={6} fill="white" stroke="#e2e8f0" />
          <circle cx={10} cy={compact ? 9 : 11} r={5} fill="none" stroke="#ef4444" strokeWidth={1.5} />
          <text x={18} y={compact ? 13 : 15} fontSize={compact ? 7 : 9} fill="#475569">
            Right ear
          </text>
          <text x={18} y={compact ? 24 : 29} fontSize={compact ? 7 : 9} fill="#475569">
            Left ear
          </text>
          <text
            x={10}
            y={compact ? 24 : 29}
            textAnchor="middle"
            fontSize={compact ? 9 : 11}
            fill="#3b82f6"
            fontWeight={700}
          >
            X
          </text>
        </g>

        {plottedActualThresholds.length > 0 &&
          renderLinesAndSymbols(plottedActualThresholds, actualLines, true)}

        {renderLinesAndSymbols(plottedStoredThresholds, storedLines, false)}

        {plottedStoredThresholds.length === 0 && plottedActualThresholds.length === 0 && (
          <text x={ML + innerW / 2} y={MT + innerH / 2} textAnchor="middle" fontSize={11} fill="#cbd5e1">
            No thresholds stored
          </text>
        )}
      </svg>
    </div>
  );
}
