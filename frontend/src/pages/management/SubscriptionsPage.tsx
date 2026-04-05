import React, { useEffect, useState } from 'react';
import { apiListSubscriptions } from '../../api/api';
import { Plus, CreditCard, Calendar, CheckCircle, XCircle } from 'lucide-react';
import clsx from 'clsx';
import SubscriptionModal from './SubscriptionModal';

export default function SubscriptionsPage() {
  const [subscriptions, setSubscriptions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedSubscription, setSelectedSubscription] = useState<any | null>(null);

  const fetchSubscriptions = async () => {
    setLoading(true);
    try {
      const data = await apiListSubscriptions();
      setSubscriptions(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubscriptions();
  }, []);

  const handleEdit = (sub: any) => {
    setSelectedSubscription(sub);
    setIsModalOpen(true);
  };

  const handleAdd = () => {
    setSelectedSubscription(null);
    setIsModalOpen(true);
  };

  if (loading && subscriptions.length === 0) return <div className="p-8">Syncing Subscriptions...</div>;

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">University Subscriptions</h1>
        <button
          onClick={handleAdd}
          className="btn-primary py-3 px-6 rounded-xl flex items-center gap-2 group"
        >
          <Plus size={20} className="group-hover:rotate-90 transition-transform duration-300" />
          Add Subscription
        </button>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-6 py-3 text-xs font-bold text-slate-500 uppercase tracking-wider">University ID</th>
              <th className="px-6 py-3 text-xs font-bold text-slate-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-xs font-bold text-slate-500 uppercase tracking-wider">Expires At</th>
              <th className="px-6 py-3 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {subscriptions.map((sub) => (
              <tr key={sub.id} className="hover:bg-slate-50/50 transition-colors">
                <td className="px-6 py-4 font-bold text-slate-900">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-500">
                      <CreditCard size={16} />
                    </div>
                    <span>#{sub.university_id}</span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className={clsx(
                    "px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider",
                    sub.is_active ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"
                  )}>
                    {sub.is_active ? 'Active' : 'Deactivated'}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-slate-500 font-medium">
                  {sub.expires_at ? new Date(sub.expires_at).toLocaleDateString() : 'Never'}
                </td>
                <td className="px-6 py-4 text-right">
                   <button
                    onClick={() => handleEdit(sub)}
                    className="p-1.5 text-slate-400 hover:text-primary-600 rounded-md hover:bg-primary-50 font-bold text-xs uppercase tracking-widest"
                   >
                      Modify
                    </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <SubscriptionModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={fetchSubscriptions}
        subscription={selectedSubscription}
      />
    </div>
  );
}
