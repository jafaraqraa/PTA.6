import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { SessionService } from '../services/sessionService';
import { useSessionStore } from '../store/sessionStore';

// ─────────────────────────────────────────────────────────────
//  useSession — start / reset session flow
// ─────────────────────────────────────────────────────────────
export function useSession() {
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState<string | null>(null);
  const navigate = useNavigate();

  const { userId, session, setSession, resetSession } = useSessionStore();

  const startSession = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const newSession = await SessionService.start();
      setSession(newSession);
      navigate('/session');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to start session');
    } finally {
      setLoading(false);
    }
  }, [userId, setSession, navigate]);

  const endSession = useCallback(() => {
    // Navigate to interpret page — actual API call happens after user enters interpretation
    navigate('/interpret');
  }, [navigate]);

  const newTest = useCallback(() => {
    resetSession();
    navigate('/dashboard');
  }, [resetSession, navigate]);

  return { session, loading, error, startSession, endSession, newTest };
}
