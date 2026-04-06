import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { EvaluationService } from '../services/evaluationService';
import { useSessionStore } from '../store/sessionStore';
import { apiSubmitQuiz } from '../api/api';
import type { FinalInterpretationCreateDTO } from '../types';

// ─────────────────────────────────────────────────────────────
//  useEvaluation — submit interpretations → get evaluation
// ─────────────────────────────────────────────────────────────
export function useEvaluation() {
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState<string | null>(null);
  const navigate = useNavigate();

  const { session, evaluation, setEvaluation, activeQuizId, setActiveQuizId } = useSessionStore();

  const submitInterpretation = useCallback(async (
    interpretations: FinalInterpretationCreateDTO[]
  ) => {
    if (!session) { setError('No active session'); return; }
    setLoading(true);
    setError(null);
    try {
      const result = await EvaluationService.endAndEvaluate(session.id, interpretations);

      // If this session is part of a quiz, submit to quiz system
      if (activeQuizId) {
        try {
          await apiSubmitQuiz({
            quiz_id: activeQuizId,
            session_id: session.id,
            score: result.summary.overall_score
          });
        } catch (quizErr) {
          console.error("Failed to link simulator result to quiz", quizErr);
        }
        // Don't clear activeQuizId yet so evaluation page can show quiz-specific UI if needed
        // but we've successfully linked them.
      }

      setEvaluation(result);
      navigate('/evaluation');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Evaluation failed');
    } finally {
      setLoading(false);
    }
  }, [session, setEvaluation, navigate, activeQuizId]);

  return { evaluation, loading, error, submitInterpretation };
}
