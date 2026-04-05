import type {
  EarSide,
  TestType,
  AttemptDTO,
  StoredThreshold,
} from '../types';
import { apiPlayTone, apiStoreTone } from '../api/api';

// ─────────────────────────────────────────────────────────────
//  Tone Service — play tone + store threshold logic
// ─────────────────────────────────────────────────────────────

export interface PlayToneParams {
  sessionId: number;
  earSide: EarSide;
  testType: TestType;
  frequency: number;
  intensity: number;
  maskingLevelDb: number | null;
}

export interface PlayToneResult {
  response: 'heard' | 'not_heard';
  attempt: AttemptDTO;
}

export const ToneService = {
  async play(params: PlayToneParams): Promise<PlayToneResult> {
    const result = await apiPlayTone({
      session_id: params.sessionId,
      ear_side: params.earSide,
      test_type: params.testType,
      frequency: params.frequency,
      intensity: params.intensity,
      masking_level_db: params.maskingLevelDb,
    });

    return {
      response: result.response,
      attempt: result.attempt as AttemptDTO,
    };
  },

  async store(params: {
    sessionId: number;
    attemptId: number;
    earSide: EarSide;
    testType: TestType;
    frequency: number;
    thresholdDb: number;
    isNoResponse: boolean;
  }): Promise<StoredThreshold> {
    const result = await apiStoreTone({
      session_id: params.sessionId,
      attempt_id: params.attemptId,
      ear_side: params.earSide,
      test_type: params.testType,
      frequency: params.frequency,
      threshold_db: params.thresholdDb,
      is_no_response: params.isNoResponse,
      is_final: true,
    });

    return result.data;
  },
};
