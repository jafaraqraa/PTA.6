import React, { useState, useEffect } from 'react';
import Modal from '../../components/Modal';
import { apiCreateUniversity, apiUpdateUniversity } from '../../api/api';
import { University } from '../../types';

interface UniversityModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  university?: University | null;
}

export default function UniversityModal({ isOpen, onClose, onSuccess, university }: UniversityModalProps) {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (university) {
      setName(university.name);
    } else {
      setName('');
    }
  }, [university, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (university) {
        await apiUpdateUniversity(university.id, { name });
      } else {
        await apiCreateUniversity({ name });
      }
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to save university');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={university ? 'Edit University' : 'Add University'}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 bg-rose-50 text-rose-600 text-sm font-medium rounded-lg border border-rose-100">
            {error}
          </div>
        )}

        <div>
          <label className="block text-sm font-bold text-slate-700 mb-1">University Name</label>
          <input
            type="text"
            required
            className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all outline-none"
            placeholder="e.g. An-Najah University"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
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
            {loading ? 'Saving...' : (university ? 'Save Changes' : 'Create University')}
          </button>
        </div>
      </form>
    </Modal>
  );
}
