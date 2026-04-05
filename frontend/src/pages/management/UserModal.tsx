import React, { useState, useEffect } from 'react';
import Modal from '../../components/Modal';
import { apiCreateUser, apiUpdateUser, apiListUniversities } from '../api/api';
import { User, University } from '../types';
import { useAuthStore } from '../store/authStore';

interface UserModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  user?: User | null;
}

export default function UserModal({ isOpen, onClose, onSuccess, user }: UserModalProps) {
  const { user: currentUser } = useAuthStore();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<string>('student');
  const [universityId, setUniversityId] = useState<number | undefined>(undefined);
  const [universities, setUniversities] = useState<University[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (user) {
      setFullName(user.full_name);
      setEmail(user.email);
      setPassword('');
      setRole(user.role);
      setUniversityId(user.university_id || undefined);
    } else {
      setFullName('');
      setEmail('');
      setPassword('');
      setRole(currentUser?.role === 'lab_admin' ? 'student' : 'student');
      setUniversityId(currentUser?.role === 'super_admin' ? undefined : currentUser?.university_id || undefined);
    }
  }, [user, isOpen, currentUser]);

  useEffect(() => {
    if (currentUser?.role === 'super_admin' && isOpen) {
      apiListUniversities().then(setUniversities).catch(console.error);
    }
  }, [currentUser, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const payload: any = {
        full_name: fullName,
        email,
        role,
        university_id: universityId || null
      };
      if (password) payload.password = password;

      if (user) {
        await apiUpdateUser(user.id, payload);
      } else {
        if (!password) throw new Error('Password is required for new users');
        await apiCreateUser(payload);
      }
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to save user');
    } finally {
      setLoading(false);
    }
  };

  const availableRoles = () => {
    if (currentUser?.role === 'super_admin') {
      return ['super_admin', 'university_admin', 'lab_admin', 'student'];
    } else if (currentUser?.role === 'university_admin') {
      return ['lab_admin', 'student'];
    } else if (currentUser?.role === 'lab_admin') {
      return ['student'];
    }
    return [];
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={user ? 'Edit User' : 'Add User'}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 bg-rose-50 text-rose-600 text-sm font-medium rounded-lg border border-rose-100">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 gap-4">
          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">Full Name</label>
            <input
              type="text"
              required
              className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all outline-none"
              placeholder="e.g. John Doe"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">Email Address</label>
            <input
              type="email"
              required
              className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all outline-none"
              placeholder="name@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">
              {user ? 'New Password (Optional)' : 'Password'}
            </label>
            <input
              type="password"
              required={!user}
              className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all outline-none"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1">Role</label>
              <select
                required
                className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all outline-none"
                value={role}
                onChange={(e) => setRole(e.target.value)}
              >
                {availableRoles().map(r => (
                  <option key={r} value={r}>{r.replace('_', ' ').toUpperCase()}</option>
                ))}
              </select>
            </div>

            {currentUser?.role === 'super_admin' && (
              <div>
                <label className="block text-sm font-bold text-slate-700 mb-1">University</label>
                <select
                  className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all outline-none"
                  value={universityId || ''}
                  onChange={(e) => setUniversityId(e.target.value ? Number(e.target.value) : undefined)}
                >
                  <option value="">System (None)</option>
                  {universities.map(u => (
                    <option key={u.id} value={u.id}>{u.name}</option>
                  ))}
                </select>
              </div>
            )}
          </div>
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
            {loading ? 'Saving...' : (user ? 'Save Changes' : 'Create User')}
          </button>
        </div>
      </form>
    </Modal>
  );
}
