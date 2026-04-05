import type { FinalInterpretationCreateDTO, SessionEvaluationDTO } from '../types';
import { apiEndSession } from '../api/api';

// ─────────────────────────────────────────────────────────────
//  Evaluation Service — end session and retrieve evaluation
// ─────────────────────────────────────────────────────────────

export const EvaluationService = {
  async endAndEvaluate(
    sessionId: number,
    interpretations: FinalInterpretationCreateDTO[]
  ): Promise<SessionEvaluationDTO> {
    return apiEndSession({
      session_id: sessionId,
      interpretations,
    });
  },
};
