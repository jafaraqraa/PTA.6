import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { EvaluationService } from '../services/evaluationService';
import { useSessionStore } from '../store/sessionStore';
import type { FinalInterpretationCreateDTO } from '../types';

// ─────────────────────────────────────────────────────────────
//  useEvaluation — submit interpretations → get evaluation
// ─────────────────────────────────────────────────────────────
export function useEvaluation() {
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState<string | null>(null);
  const navigate = useNavigate();

  const { session, evaluation, setEvaluation } = useSessionStore();

  const submitInterpretation = useCallback(async (
    interpretations: FinalInterpretationCreateDTO[]
  ) => {
    if (!session) { setError('No active session'); return; }
    setLoading(true);
    setError(null);
    try {
      const result = await EvaluationService.endAndEvaluate(session.id, interpretations);
      setEvaluation(result);
      navigate('/evaluation');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Evaluation failed');
    } finally {
      setLoading(false);
    }
  }, [session, setEvaluation, navigate]);

  return { evaluation, loading, error, submitInterpretation };
}
