import { useState, useEffect } from 'react';
import { apiGetDashboardStats } from '../api/api';
import type { RecentSession } from '../types';

export function useDashboard() {
  const [stats,          setStats]          = useState<any | null>(null);
  const [recentSessions, setRecentSessions] = useState<RecentSession[]>([]);
  const [loading,        setLoading]        = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await apiGetDashboardStats();
        setStats(data);
        // Still using mock for sessions as they are user-specific and not yet in analytics API
        const { MOCK_RECENT_SESSIONS } = await import('../api/mockData');
        setRecentSessions(MOCK_RECENT_SESSIONS);
      } catch (err) {
        console.error("Failed to fetch dashboard stats", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  return { stats, recentSessions, loading };
}
