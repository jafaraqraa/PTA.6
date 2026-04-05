import React, { useEffect, useState } from 'react';
import { apiListUniversities, apiCreateUniversity } from '../../api/api';
import { University } from '../../types';
import { Plus, School, Globe, Edit2 } from 'lucide-react';

export default function UniversitiesPage() {
  const [universities, setUniversities] = useState<University[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchUniversities() {
      try {
        const data = await apiListUniversities();
        setUniversities(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchUniversities();
  }, []);

  if (loading) return <div className="p-8 text-slate-500 font-bold uppercase tracking-widest text-xs">Syncing Universities...</div>;

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Universities</h1>
          <p className="text-slate-500 font-medium">Manage institutional tenants and their domains.</p>
        </div>
        <button className="btn-primary py-3 px-6 rounded-xl flex items-center gap-2 group">
          <Plus size={20} className="group-hover:rotate-90 transition-transform duration-300" />
          Add University
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {universities.map((uni) => (
          <div key={uni.id} className="card p-6 group hover:border-primary-200 transition-all duration-300">
            <div className="flex items-start justify-between mb-6">
              <div className="w-12 h-12 rounded-2xl bg-primary-50 text-primary-600 flex items-center justify-center group-hover:scale-110 transition-transform">
                <School size={24} />
              </div>
              <button className="p-2 text-slate-300 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors">
                <Edit2 size={18} />
              </button>
            </div>

            <h3 className="text-xl font-bold text-slate-900 mb-2">{uni.name}</h3>

            <div className="flex items-center gap-2 text-slate-500 font-medium mb-4">
              <Globe size={16} className="text-slate-400" />
              <span className="text-sm">{uni.domain}.localhost</span>
            </div>

            <div className="pt-6 border-t border-slate-50 mt-auto">
              <div className="flex items-center justify-between">
                <div className="text-[10px] uppercase font-bold text-slate-400 tracking-widest">ID: {uni.id}</div>
                <div className="px-2 py-1 bg-emerald-50 text-emerald-700 text-[10px] font-bold uppercase tracking-wider rounded-md">
                  Active Tenant
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
