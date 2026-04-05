import React, { useState, useEffect } from 'react';
import Modal from '../../components/Modal';
import { apiCreateSubscription, apiUpdateSubscription, apiListUniversities } from '../api/api';
import { University } from '../types';

interface SubscriptionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  subscription?: any | null;
}

export default function SubscriptionModal({ isOpen, onClose, onSuccess, subscription }: SubscriptionModalProps) {
  const [universityId, setUniversityId] = useState<number | undefined>(undefined);
  const [isActive, setIsActive] = useState(true);
  const [expiresAt, setExpiresAt] = useState('');
  const [universities, setUniversities] = useState<University[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (subscription) {
      setUniversityId(subscription.university_id);
      setIsActive(subscription.is_active);
      setExpiresAt(subscription.expires_at ? subscription.expires_at.split('T')[0] : '');
    } else {
      setUniversityId(undefined);
      setIsActive(true);
      setExpiresAt('');
    }
  }, [subscription, isOpen]);

  useEffect(() => {
    if (isOpen) {
      apiListUniversities().then(setUniversities).catch(console.error);
    }
  }, [isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const payload: any = {
        is_active: isActive,
        expires_at: expiresAt ? new Date(expiresAt).toISOString() : null
      };

      if (subscription) {
        await apiUpdateSubscription(subscription.id, payload);
      } else {
        if (!universityId) throw new Error('University is required');
        payload.university_id = universityId;
        await apiCreateSubscription(payload);
      }
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to save subscription');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={subscription ? 'Edit Subscription' : 'Add Subscription'}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 bg-rose-50 text-rose-600 text-sm font-medium rounded-lg border border-rose-100">
            {error}
          </div>
        )}

        <div>
          <label className="block text-sm font-bold text-slate-700 mb-1">University</label>
          <select
            disabled={!!subscription}
            required
            className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all outline-none disabled:bg-slate-100 disabled:cursor-not-allowed"
            value={universityId || ''}
            onChange={(e) => setUniversityId(Number(e.target.value))}
          >
            <option value="">Select University</option>
            {universities.map(u => (
              <option key={u.id} value={u.id}>{u.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-bold text-slate-700 mb-1">Expires At</label>
          <input
            type="date"
            className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all outline-none"
            value={expiresAt}
            onChange={(e) => setExpiresAt(e.target.value)}
          />
          <p className="mt-1 text-[10px] text-slate-400">Leave blank for lifetime subscription</p>
        </div>

        <div className="flex items-center gap-3 p-4 bg-slate-50 rounded-xl border border-slate-100">
          <input
            type="checkbox"
            id="is_active"
            className="w-5 h-5 rounded-lg text-primary-600 border-slate-300 focus:ring-primary-500 transition-all cursor-pointer"
            checked={isActive}
            onChange={(e) => setIsActive(e.target.checked)}
          />
          <label htmlFor="is_active" className="text-sm font-bold text-slate-700 cursor-pointer select-none">
            Subscription is active
          </label>
        </div>

        <div className="pt-2 flex gap-3">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-slate-200 text-slate-600 font-bold rounded-xl hover:bg-slate-50 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="flex-1 px-4 py-2 bg-primary-600 text-white font-bold rounded-xl hover:bg-primary-700 shadow-lg shadow-primary-200 transition-all disabled:opacity-50"
          >
            {loading ? 'Saving...' : (subscription ? 'Save Changes' : 'Create Subscription')}
          </button>
        </div>
      </form>
    </Modal>
  );
}
