import { useState, useCallback, useRef } from 'react';
import { ToneService } from '../services/toneService';
import { useSessionStore } from '../store/sessionStore';
import type { AttemptDTO, EarSide, TestType } from '../types';

// ─────────────────────────────────────────────────────────────
//  useTone — play tone + store threshold
// ─────────────────────────────────────────────────────────────
export function useTone() {
  const [loading,      setLoading]      = useState(false);
  const [error,        setError]        = useState<string | null>(null);
  const [lastResponse, setLastResponse] = useState<'heard' | 'not_heard' | null>(null);
  const lastAttemptRef = useRef<AttemptDTO | null>(null);
  const playRequestInFlightRef = useRef(false);
  const storeRequestInFlightRef = useRef(false);

  const {
    session,
    addAttempt,
    addStoredThreshold,
    storedThresholds,
  } = useSessionStore();

  const playTone = useCallback(async (params: {
    ear_side: EarSide;
    test_type: TestType;
    frequency: number;
    intensity: number;
    masking_level_db: number | null;
  }) => {
    if (!session) return;
    if (playRequestInFlightRef.current) return;
    playRequestInFlightRef.current = true;
    setLoading(true);
    setError(null);
    try {
      const result = await ToneService.play({
        sessionId:     session.id,
        earSide:       params.ear_side,
        testType:      params.test_type,
        frequency:     params.frequency,
        intensity:     params.intensity,
        maskingLevelDb: params.masking_level_db,
      });
      setLastResponse(result.response);
      addAttempt(result.attempt);
      lastAttemptRef.current = result.attempt;
      return result.response;
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Tone play failed');
    } finally {
      playRequestInFlightRef.current = false;
      setLoading(false);
    }
  }, [session, addAttempt]);

  const canStoreToneForSelection = useCallback((params: {
    ear_side: EarSide;
    test_type: TestType;
    frequency: number;
    threshold_db: number;
  }) => {
    const lastAttempt = lastAttemptRef.current;
    if (!lastAttempt) return false;

    return (
      lastAttempt.ear_side === params.ear_side &&
      lastAttempt.test_type === params.test_type &&
      lastAttempt.frequency === params.frequency &&
      Math.abs(lastAttempt.intensity - params.threshold_db) <= 0.1
    );
  }, []);

  const storeTone = useCallback(async (params: {
    ear_side: EarSide;
    test_type: TestType;
    frequency: number;
    threshold_db: number;
    is_no_response: boolean;
  }) => {
    if (!session) return;
    if (storeRequestInFlightRef.current) return;
    if (!canStoreToneForSelection(params)) {
      setError('Present a tone on the same ear, transducer, frequency, and level before storing this threshold.');
      return;
    }
    storeRequestInFlightRef.current = true;
    setLoading(true);
    setError(null);
    try {
      const attemptId = lastAttemptRef.current?.id;
      if (attemptId == null) {
        setError('Present a tone before storing a threshold.');
        return;
      }

      const threshold = await ToneService.store({
        sessionId:    session.id,
        attemptId,
        earSide:      params.ear_side,
        testType:     params.test_type,
        frequency:    params.frequency,
        thresholdDb:  params.threshold_db,
        isNoResponse: params.is_no_response,
      });
      addStoredThreshold(threshold);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Store tone failed');
    } finally {
      storeRequestInFlightRef.current = false;
      setLoading(false);
    }
  }, [session, addStoredThreshold, canStoreToneForSelection]);

  return {
    loading,
    error,
    lastResponse,
    storedThresholds,
    playTone,
    storeTone,
    canStoreToneForSelection,
  };
}
