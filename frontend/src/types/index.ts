// ============================================================
//  Domain Enums (mirrors backend enums.py)
// ============================================================
export type EarSide = 'left' | 'right';
export type TestType = 'AC' | 'AC_masked' | 'BC' | 'BC_masked';
export type ResponseType = 'heard' | 'not_heard';

export type HearingType = 'Normal' | 'Conductive' | 'Sensorineural' | 'Mixed';
export type HearingSeverity =
  | 'Normal' | 'Mild' | 'Moderate' | 'Moderately Severe'
  | 'Severe' | 'Profound' | 'Undetermined';
export type HearingConfiguration =
  | 'All Frequencies' | 'Low Frequencies' | 'Mid Frequencies'
  | 'High Frequencies' | 'Single Frequency' | 'Notch Pattern'
  | 'Other' | 'Undetermined';

// ============================================================
//  Session
// ============================================================
export interface SessionDTO {
  id: number;
  user_id: number;
  patient_id: number | null;
  start_time: string;
  end_time: string | null;
}

// ============================================================
//  Audiogram / Patient
// ============================================================
export interface AudiogramPoint {
  id?: number;
  test_type: TestType;
  frequency: number;
  threshold_db: number;
  is_no_response: boolean;
}

export interface EarDTO {
  id?: number;
  side: EarSide;
  hearing_type?: HearingType;
  audiogram_points: AudiogramPoint[];
}

export interface PatientDTO {
  id?: number;
  source_type: 'real' | 'synthetic';
  ears: EarDTO[];
}

// ============================================================
//  Attempt
// ============================================================
export interface AttemptCreateDTO {
  session_id: number;
  ear_side: EarSide;
  test_type: TestType;
  frequency: number;
  intensity: number;
  masking_level_db?: number | null;
  response?: ResponseType | null;
}

export interface AttemptDTO extends AttemptCreateDTO {
  id: number;
  created_at: string;
}

// ============================================================
//  Stored Threshold
// ============================================================
export interface StoredThreshold {
  id: number;
  session_id: number;
  attempt_id: number;
  ear_side: EarSide;
  test_type: TestType;
  frequency: number;
  threshold_db: number;
  is_no_response: boolean;
  is_final: boolean;
  created_at: string;
}

export interface CreateStoredThresholdDTO {
  session_id: number;
  attempt_id: number;
  ear_side: EarSide;
  test_type: TestType;
  frequency: number;
  threshold_db: number;
  is_no_response: boolean;
  is_final: boolean;
}

// ============================================================
//  Final Interpretation (input)
// ============================================================
export interface FinalInterpretationCreateDTO {
  ear_side: EarSide;
  overall_type?: HearingType | null;
  severity?: HearingSeverity | null;
  configuration?: HearingConfiguration | null;
  affected_frequencies_hz: number[];
}

export interface EndSessionDTO {
  session_id: number;
  interpretations: FinalInterpretationCreateDTO[];
}

// ============================================================
//  Evaluation (response from endSession)
// ============================================================
export interface ProtocolMetric {
  code: string;
  label: string;
  score: number;
  max_score: number;
  status: string;
  details: string;
}

export interface ThresholdComparison {
  ear_side: EarSide;
  test_type: TestType;
  frequency: number;
  true_threshold_db: number | null;
  detected_threshold_db: number | null;
  true_is_no_response: boolean;
  detected_is_no_response: boolean;
  absolute_error_db: number | null;
  score: number;
  status: string;
  note: string;
}

export interface InterpretationFieldScore {
  field_name: string;
  expected_value: unknown;
  submitted_value: unknown;
  score: number;
  max_score: number;
  is_scorable: boolean;
  status: string;
  note: string;
}

export interface EarInterpretationEvaluation {
  ear_side: EarSide;
  score: number;
  max_score: number;
  scorable_fields: string[];
  undetermined_fields: Record<string, string>;
  reference_summary: Record<string, unknown>;
  submitted_summary?: Record<string, unknown> | null;
  field_scores: InterpretationFieldScore[];
}

export interface AIFeedback {
  status: string;
  provider?: string;
  model?: string;
  summary?: string;
  strengths: string[];
  improvement_points: string[];
  next_session_tips: string[];
  message?: string;
}

export interface EvaluationSummary {
  session_id: number;
  patient_id?: number | null;
  duration_seconds?: number | null;
  overall_score: number;
  threshold_accuracy_score: number;
  interpretation_score: number;
  protocol_feedback_summary?: string | null;
  strengths: string[];
  improvement_points: string[];
}

export interface SessionEvaluationDTO {
  summary: EvaluationSummary;
  protocol_metrics: ProtocolMetric[];
  threshold_comparisons: ThresholdComparison[];
  interpretation_evaluations: EarInterpretationEvaluation[];
  ai_feedback?: AIFeedback | null;
}

// ============================================================
//  UI local types
// ============================================================
export interface RecentSession {
  id: number;
  patientId: number;
  date: string;
  score: number;
  duration: string;
  completed: boolean;
}

// ============================================================
//  Authentication & User
// ============================================================
export type UserRole = 'super_admin' | 'university_admin' | 'lab_admin' | 'student';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  university_id: number | null;
  is_active: boolean;
  created_at: string;
}

export interface University {
  id: number;
  name: string;
  domain: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}
