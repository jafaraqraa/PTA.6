import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import Session from './pages/Session';
import Interpretation from './pages/Interpretation';
import Evaluation from './pages/Evaluation';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/session" element={<Session />} />
        <Route path="/interpret" element={<Interpretation />} />
        <Route path="/evaluation" element={<Evaluation />} />
      </Routes>
    </BrowserRouter>
  );
}
