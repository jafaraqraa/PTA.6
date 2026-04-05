import React from 'react';
import { Activity } from 'lucide-react';

interface NavbarProps {
  leftContent?: React.ReactNode;
  rightContent?: React.ReactNode;
  showBrand?: boolean;
}

export default function Navbar({ leftContent, rightContent, showBrand = true }: NavbarProps) {
  return (
    <header className="sticky top-0 z-50 w-full bg-white/80 backdrop-blur-md border-b border-slate-100 shadow-sm">
      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 flex h-14 items-center justify-between">
        <div className="flex items-center gap-4">
          {showBrand && (
          <div className="flex items-center gap-2.5">
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-primary-600 text-white">
              <Activity size={16} strokeWidth={2.5} />
            </div>
            <span className="font-bold text-slate-800 text-base tracking-tight">
              PTA <span className="text-primary-600">Simulator</span>
            </span>
          </div>
          )}
          {leftContent}
        </div>
        <div className="flex items-center gap-2">{rightContent}</div>
      </div>
    </header>
  );
}
