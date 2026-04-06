import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import Session from './pages/Session';
import Interpretation from './pages/Interpretation';
import Evaluation from './pages/Evaluation';
import Login from './pages/Login';
import Unauthorized from './pages/Unauthorized';
import SubscriptionExpired from './pages/SubscriptionExpired';
import ProtectedRoute from './components/ProtectedRoute';
import AppLayout from './components/AppLayout';
import UsersPage from './pages/management/UsersPage';
import UniversitiesPage from './pages/management/UniversitiesPage';
import SubscriptionsPage from './pages/management/SubscriptionsPage';
import QuizzesPage from './pages/management/QuizzesPage';
import StudentQuizzes from './pages/management/StudentQuizzes';
import { useAuthStore } from './store/authStore';

export default function App() {
  const { user } = useAuthStore();
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/unauthorized" element={<Unauthorized />} />
        <Route path="/subscription-expired" element={<SubscriptionExpired />} />

        {/* Protected App Routes */}
        <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/session" element={<Session />} />
          <Route path="/interpret" element={<Interpretation />} />
          <Route path="/evaluation" element={<Evaluation />} />

          {/* Management Routes */}
          <Route path="/users" element={
            <ProtectedRoute allowedRoles={['super_admin', 'university_admin', 'lab_admin']}>
              <UsersPage />
            </ProtectedRoute>
          } />
          <Route path="/quizzes" element={
            user?.role === 'student' ? <StudentQuizzes /> : <QuizzesPage />
          } />
          <Route path="/universities" element={
            <ProtectedRoute allowedRoles={['super_admin']}>
              <UniversitiesPage />
            </ProtectedRoute>
          } />
          <Route path="/subscriptions" element={
            <ProtectedRoute allowedRoles={['super_admin']}>
              <SubscriptionsPage />
            </ProtectedRoute>
          } />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
