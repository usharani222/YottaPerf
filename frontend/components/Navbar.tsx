'use client';

import React from 'react';
import { Shield, Sparkles, Bell, User, CheckCircle2 } from 'lucide-react';
import { UserProfile } from '../types';

interface NavbarProps {
  currentUser: UserProfile | null;
  activeCycleName: string;
  onRefresh?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentUser, activeCycleName, onRefresh }) => {
  return (
    <header className="sticky top-0 z-40 flex h-16 w-full items-center justify-between border-b border-slate-800 bg-slate-950/80 px-6 backdrop-blur-md">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-600 shadow-lg shadow-indigo-500/20">
          <Shield className="h-5 w-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold tracking-tight text-white">YottaPerf</span>
            <span className="rounded-full bg-indigo-500/10 px-2 py-0.5 text-xs font-semibold text-indigo-400 border border-indigo-500/20">
              Enterprise v1.0
            </span>
          </div>
          <p className="text-xs text-slate-400 hidden sm:block">Employee Performance & Development Platform</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Active Cycle Badge */}
        <div className="hidden md:flex items-center gap-2 rounded-lg border border-slate-800 bg-slate-900/60 px-3 py-1.5 text-xs text-slate-300">
          <div className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="font-medium text-slate-400">Cycle:</span>
          <span className="font-semibold text-slate-200">{activeCycleName || 'CYCLE-2026-H1 (Active)'}</span>
        </div>

        {/* User Profile Capsule */}
        <div className="flex items-center gap-3 rounded-lg border border-slate-800 bg-slate-900/80 p-1.5 pl-3">
          <div className="flex flex-col text-right">
            <span className="text-xs font-semibold text-white">
              {currentUser?.full_name || 'Eleanor Vance (CEO)'}
            </span>
            <span className="text-[10px] text-indigo-400 font-mono">
              {currentUser?.roles ? currentUser.roles.join(', ') : 'ADMIN, MANAGER'}
            </span>
          </div>
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600/30 text-indigo-300 border border-indigo-500/30">
            <User className="h-4 w-4" />
          </div>
        </div>
      </div>
    </header>
  );
};
