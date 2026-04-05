import { useState, useEffect } from 'react';
import { MOCK_STATS, MOCK_RECENT_SESSIONS } from '../api/mockData';
import type { RecentSession } from '../types';

// ─────────────────────────────────────────────────────────────
//  useDashboard — load dashboard stats & recent sessions
//  Currently uses mock data; swap to real API when ready
// ─────────────────────────────────────────────────────────────
export interface DashboardStats {
  totalSessions: number;
  completed: number;
  avgScore: number;
  lastScore: number;
}

export function useDashboard() {
  const [stats,          setStats]          = useState<DashboardStats | null>(null);
  const [recentSessions, setRecentSessions] = useState<RecentSession[]>([]);
  const [loading,        setLoading]        = useState(true);

  useEffect(() => {
    // Simulate async fetch
    const timer = setTimeout(() => {
      setStats(MOCK_STATS);
      setRecentSessions(MOCK_RECENT_SESSIONS);
      setLoading(false);
    }, 400);
    return () => clearTimeout(timer);
  }, []);

  return { stats, recentSessions, loading };
}
