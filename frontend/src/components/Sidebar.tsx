import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  School,
  CreditCard,
  Activity,
  BarChart3,
  UserCircle,
  Play
} from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import clsx from 'clsx';

export default function Sidebar() {
  const { user } = useAuthStore();

  const navItems = [
    {
      label: 'Dashboard',
      to: '/dashboard',
      icon: LayoutDashboard,
      roles: ['super_admin', 'university_admin', 'lab_admin', 'student']
    },
    {
      label: 'Universities',
      to: '/universities',
      icon: School,
      roles: ['super_admin']
    },
    {
      label: 'Subscriptions',
      to: '/subscriptions',
      icon: CreditCard,
      roles: ['super_admin']
    },
    {
      label: 'Users',
      to: '/users',
      icon: Users,
      roles: ['super_admin', 'university_admin']
    },
    {
      label: 'Lab Admins',
      to: '/lab-admins',
      icon: ShieldCheck, // Custom Icon if needed
      roles: ['university_admin']
    },
    {
      label: 'Students',
      to: '/students',
      icon: Users,
      roles: ['university_admin', 'lab_admin']
    },
    {
      label: 'Sessions',
      to: '/sessions',
      icon: Activity,
      roles: ['university_admin', 'lab_admin', 'student']
    },
    {
      label: 'Reports',
      to: '/reports',
      icon: BarChart3,
      roles: ['university_admin', 'lab_admin']
    },
    {
      label: 'Profile',
      to: '/profile',
      icon: UserCircle,
      roles: ['super_admin', 'university_admin', 'lab_admin', 'student']
    },
  ];

  const allowedItems = navItems.filter(item => item.roles.includes(user?.role || ''));

  return (
    <aside className="w-64 bg-white border-r border-slate-200 h-[calc(100vh-3.5rem)] sticky top-14 hidden md:block">
      <nav className="p-4 space-y-1">
        {allowedItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => clsx(
              "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
              isActive
                ? "bg-primary-50 text-primary-600"
                : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
            )}
          >
            <item.icon size={18} />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

// Add ShieldCheck to the imports
import { ShieldCheck } from 'lucide-react';
