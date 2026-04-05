import type { SessionEvaluationDTO, RecentSession } from '../types';

// ── Mock Recent Sessions ──────────────────────────────────────
export const MOCK_RECENT_SESSIONS: RecentSession[] = [
  { id: 101, patientId: 12, date: '2026-04-01', score: 87, duration: '18m 42s', completed: true },
  { id: 98,  patientId: 9,  date: '2026-03-30', score: 73, duration: '22m 05s', completed: true },
  { id: 95,  patientId: 7,  date: '2026-03-28', score: 91, duration: '15m 30s', completed: true },
  { id: 90,  patientId: 4,  date: '2026-03-25', score: 65, duration: '28m 10s', completed: true },
];

// ── Mock Dashboard Stats ──────────────────────────────────────
export const MOCK_STATS = {
  totalSessions: 24,
  completed: 21,
  avgScore: 79,
  lastScore: 87,
};

// ── Mock Evaluation ───────────────────────────────────────────
export const MOCK_EVALUATION: SessionEvaluationDTO = {
  summary: {
    session_id: 102,
    patient_id: 13,
    duration_seconds: 1142,
    overall_score: 84.5,
    threshold_accuracy_score: 88,
    interpretation_score: 78,
    protocol_feedback_summary:
      'Good adherence to standard protocol. Minor deviations in masking procedure.',
    strengths: [
      'Accurate threshold detection at speech frequencies',
      'Correct bilateral testing order',
      'Proper use of AC before BC',
    ],
    improvement_points: [
      'Masking level was too low at 4000 Hz for right ear',
      'Interpretation severity underestimated for left ear',
    ],
  },
  protocol_metrics: [
    { code: 'FREQ_ORDER', label: 'Frequency Order', score: 90, max_score: 100, status: 'good', details: 'Tested frequencies in correct clinical order' },
    { code: 'EAR_ORDER', label: 'Ear Order', score: 100, max_score: 100, status: 'excellent', details: 'Started with better ear correctly' },
    { code: 'MASKING', label: 'Masking Protocol', score: 70, max_score: 100, status: 'fair', details: 'Masking applied but level was suboptimal at some frequencies' },
    { code: 'THRESHOLD_METHOD', label: 'Threshold Method', score: 88, max_score: 100, status: 'good', details: 'Ascending method used consistently' },
    { code: 'RESPONSE_CONFIRM', label: 'Response Confirmation', score: 82, max_score: 100, status: 'good', details: 'Confirmations at threshold level performed' },
  ],
  threshold_comparisons: [
    { ear_side: 'right', test_type: 'AC', frequency: 500,  true_threshold_db: 25,   detected_threshold_db: 25,   true_is_no_response: false, detected_is_no_response: false, absolute_error_db: 0,  score: 100, status: 'exact',   note: 'Perfect match' },
    { ear_side: 'right', test_type: 'AC', frequency: 1000, true_threshold_db: 30,   detected_threshold_db: 35,   true_is_no_response: false, detected_is_no_response: false, absolute_error_db: 5,  score: 90,  status: 'close',   note: '5 dB off' },
    { ear_side: 'right', test_type: 'AC', frequency: 2000, true_threshold_db: 40,   detected_threshold_db: 40,   true_is_no_response: false, detected_is_no_response: false, absolute_error_db: 0,  score: 100, status: 'exact',   note: 'Perfect match' },
    { ear_side: 'right', test_type: 'AC', frequency: 4000, true_threshold_db: 65,   detected_threshold_db: 55,   true_is_no_response: false, detected_is_no_response: false, absolute_error_db: 10, score: 75,  status: 'off',     note: '10 dB error' },
    { ear_side: 'left',  test_type: 'AC', frequency: 500,  true_threshold_db: 15,   detected_threshold_db: 20,   true_is_no_response: false, detected_is_no_response: false, absolute_error_db: 5,  score: 90,  status: 'close',   note: '5 dB off' },
    { ear_side: 'left',  test_type: 'AC', frequency: 1000, true_threshold_db: 20,   detected_threshold_db: 20,   true_is_no_response: false, detected_is_no_response: false, absolute_error_db: 0,  score: 100, status: 'exact',   note: 'Perfect match' },
    { ear_side: 'left',  test_type: 'AC', frequency: 2000, true_threshold_db: 25,   detected_threshold_db: 25,   true_is_no_response: false, detected_is_no_response: false, absolute_error_db: 0,  score: 100, status: 'exact',   note: 'Perfect match' },
    { ear_side: 'left',  test_type: 'AC', frequency: 4000, true_threshold_db: null, detected_threshold_db: null, true_is_no_response: true,  detected_is_no_response: true,  absolute_error_db: null, score: 100, status: 'exact', note: 'NR correctly identified' },
    { ear_side: 'right', test_type: 'BC', frequency: 500,  true_threshold_db: 25,   detected_threshold_db: 25,   true_is_no_response: false, detected_is_no_response: false, absolute_error_db: 0,  score: 100, status: 'exact',   note: 'Perfect match' },
    { ear_side: 'right', test_type: 'BC', frequency: 1000, true_threshold_db: 30,   detected_threshold_db: 30,   true_is_no_response: false, detected_is_no_response: false, absolute_error_db: 0,  score: 100, status: 'exact',   note: 'Perfect match' },
  ],
  interpretation_evaluations: [
    {
      ear_side: 'right',
      score: 80,
      max_score: 100,
      scorable_fields: ['overall_type', 'severity', 'configuration'],
      undetermined_fields: {},
      reference_summary: { overall_type: 'Sensorineural', severity: 'Moderate', configuration: 'High Frequencies' },
      submitted_summary: { overall_type: 'Sensorineural', severity: 'Mild', configuration: 'High Frequencies' },
      field_scores: [
        { field_name: 'overall_type',  expected_value: 'Sensorineural', submitted_value: 'Sensorineural', score: 100, max_score: 100, is_scorable: true, status: 'correct',   note: 'Correct' },
        { field_name: 'severity',      expected_value: 'Moderate',      submitted_value: 'Mild',          score: 40,  max_score: 100, is_scorable: true, status: 'incorrect', note: 'One level off' },
        { field_name: 'configuration', expected_value: 'High Frequencies', submitted_value: 'High Frequencies', score: 100, max_score: 100, is_scorable: true, status: 'correct', note: 'Correct' },
      ],
    },
    {
      ear_side: 'left',
      score: 76,
      max_score: 100,
      scorable_fields: ['overall_type', 'severity'],
      undetermined_fields: {},
      reference_summary: { overall_type: 'Conductive', severity: 'Mild', configuration: 'All Frequencies' },
      submitted_summary: { overall_type: 'Conductive', severity: 'Mild', configuration: 'All Frequencies' },
      field_scores: [
        { field_name: 'overall_type',  expected_value: 'Conductive', submitted_value: 'Conductive', score: 100, max_score: 100, is_scorable: true, status: 'correct',   note: 'Correct' },
        { field_name: 'severity',      expected_value: 'Mild',       submitted_value: 'Mild',       score: 100, max_score: 100, is_scorable: true, status: 'correct',   note: 'Correct' },
        { field_name: 'configuration', expected_value: 'All Frequencies', submitted_value: 'All Frequencies', score: 100, max_score: 100, is_scorable: true, status: 'correct', note: 'Correct' },
      ],
    },
  ],
  ai_feedback: {
    status: 'success',
    provider: 'openai',
    model: 'gpt-4o',
    summary:
      'Overall a strong session. You demonstrated good protocol adherence and accurate threshold detection at most speech frequencies. Your main area for improvement is in masking levels at high frequencies and fine-tuning severity classification.',
    strengths: [
      'Excellent bilateral testing order',
      'Accurate thresholds at 500–2000 Hz',
      'Correct NR identification at 4000 Hz left ear',
    ],
    improvement_points: [
      'Increase masking level at high frequencies (≥3000 Hz)',
      'Re-evaluate severity classification criteria for sensorineural loss',
    ],
    next_session_tips: [
      'Practice BC masking scenarios',
      'Review WHO severity classification thresholds',
      'Try a mixed hearing loss patient profile',
    ],
  },
};

// ── Mock Attempt History for Simulator ───────────────────────
export const MOCK_ATTEMPTS = [
  { id: 1, ear_side: 'right', test_type: 'AC', frequency: 1000, intensity: 40, response: 'heard',     created_at: '' },
  { id: 2, ear_side: 'right', test_type: 'AC', frequency: 1000, intensity: 30, response: 'heard',     created_at: '' },
  { id: 3, ear_side: 'right', test_type: 'AC', frequency: 1000, intensity: 20, response: 'not_heard', created_at: '' },
  { id: 4, ear_side: 'right', test_type: 'AC', frequency: 1000, intensity: 25, response: 'not_heard', created_at: '' },
  { id: 5, ear_side: 'right', test_type: 'AC', frequency: 1000, intensity: 30, response: 'heard',     created_at: '' },
  { id: 6, ear_side: 'right', test_type: 'AC', frequency: 2000, intensity: 45, response: 'heard',     created_at: '' },
  { id: 7, ear_side: 'right', test_type: 'AC', frequency: 2000, intensity: 35, response: 'not_heard', created_at: '' },
  { id: 8, ear_side: 'right', test_type: 'AC', frequency: 2000, intensity: 40, response: 'heard',     created_at: '' },
];
