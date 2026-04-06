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
        if (data.recent_sessions) {
          setRecentSessions(data.recent_sessions);
        } else {
          setRecentSessions([]);
        }
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
