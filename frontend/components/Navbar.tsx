'use client';

import React, { useState } from 'react';
import { 
  Zap, 
  Sparkles, 
  User, 
  ChevronDown, 
  RefreshCw, 
  Search, 
  Activity, 
  ShieldCheck,
  CheckCircle2
} from 'lucide-react';
import { UserProfile } from '../types';
import { api } from '../services/api';

interface NavbarProps {
  currentUser: UserProfile | null;
  activeCycleName: string;
  onRefresh?: () => void;
}

const DEMO_PERSONAS = [
  { username: 'eleanor.vance', name: 'Eleanor Vance', title: 'CEO', role: 'ADMIN, MANAGER', color: 'from-emerald-500 to-teal-600', badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' },
  { username: 'marcus.chen', name: 'Marcus Chen', title: 'VP People Ops', role: 'HR_PARTNER', color: 'from-cyan-500 to-blue-600', badgeColor: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30' },
  { username: 'devon.ross', name: 'Devon Ross', title: 'Director Cloud Eng', role: 'IT_OPS', color: 'from-amber-500 to-orange-600', badgeColor: 'bg-amber-500/10 text-amber-400 border-amber-500/30' },
  { username: 'sarah.jenkins', name: 'Sarah Jenkins', title: 'Eng Manager', role: 'MANAGER', color: 'from-indigo-500 to-purple-600', badgeColor: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30' },
  { username: 'david.miller', name: 'David Miller', title: 'Senior Backend Eng', role: 'EMPLOYEE', color: 'from-violet-500 to-fuchsia-600', badgeColor: 'bg-violet-500/10 text-violet-400 border-violet-500/30' },
];

export const Navbar: React.FC<NavbarProps> = ({ currentUser, activeCycleName, onRefresh }) => {
  const [showPersonaMenu, setShowPersonaMenu] = useState(false);
  const [isSwitching, setIsSwitching] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSwitchPersona = async (username: string) => {
    setIsSwitching(true);
    setShowPersonaMenu(false);
    try {
      await api.login(username, 'Password123!');
      if (onRefresh) {
        onRefresh();
      }
    } catch (e: any) {
      alert(`Login failed for ${username}: ${e.message}`);
    } finally {
      setIsSwitching(false);
    }
  };

  return (
    <header className="sticky top-0 z-50 flex h-16 w-full items-center justify-between border-b border-white/[0.08] bg-slate-950/80 px-6 backdrop-blur-2xl">
      {/* Brand & Identity */}
      <div className="flex items-center gap-4">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-emerald-500 via-teal-500 to-cyan-500 p-0.5 shadow-lg shadow-emerald-500/20">
          <div className="flex h-full w-full items-center justify-center rounded-[10px] bg-slate-950">
            <Zap className="h-5 w-5 text-emerald-400 fill-emerald-400" />
          </div>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="text-lg font-extrabold tracking-tight gradient-text-aurora">
              YottaPerf
            </span>
            <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold tracking-wide text-emerald-400 border border-emerald-500/30">
              AURORA ENTERPRISE
            </span>
          </div>
          <p className="text-[11px] text-slate-400 hidden sm:block">Performance Intelligence & Growth Engineering</p>
        </div>
      </div>

      {/* Global Quick Search */}
      <div className="hidden lg:flex items-center relative w-96">
        <Search className="absolute left-3.5 top-2.5 h-4 w-4 text-slate-500" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Quick search OKRs, employees, metrics..."
          className="w-full bg-slate-900/60 border border-white/[0.08] rounded-xl pl-9 pr-12 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/30 transition-all"
        />
        <kbd className="absolute right-3 top-2 px-1.5 py-0.5 text-[10px] font-mono text-slate-500 bg-slate-800/80 rounded border border-slate-700/60">
          ⌘K
        </kbd>
      </div>

      {/* Right Controls & User Profile */}
      <div className="flex items-center gap-3">
        {/* Active Cycle Capsule */}
        <div className="hidden md:flex items-center gap-2 rounded-xl border border-white/[0.08] bg-slate-900/40 px-3.5 py-1.5 text-xs text-slate-300">
          <div className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </div>
          <span className="text-[11px] font-medium text-slate-400">Review Window:</span>
          <span className="text-xs font-semibold text-emerald-400 font-mono">
            {activeCycleName || 'CYCLE-2026-H1'}
          </span>
        </div>

        {/* Telemetry Refresh Button */}
        {onRefresh && (
          <button
            onClick={onRefresh}
            title="Reload telemetry data"
            className="flex h-9 w-9 items-center justify-center rounded-xl border border-white/[0.08] bg-slate-900/40 text-slate-400 hover:text-emerald-400 hover:border-emerald-500/30 hover:bg-slate-900/80 transition-all duration-200"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        )}

        {/* Persona Switcher Capsule */}
        <div className="relative">
          <button
            onClick={() => setShowPersonaMenu(!showPersonaMenu)}
            disabled={isSwitching}
            className="flex items-center gap-3 rounded-xl border border-white/[0.08] bg-slate-900/50 p-1.5 pl-3 hover:border-emerald-500/30 hover:bg-slate-900/80 transition-all duration-200"
          >
            <div className="flex flex-col text-right">
              <span className="text-xs font-semibold text-slate-100">
                {currentUser?.full_name || 'Eleanor Vance (CEO)'}
              </span>
              <span className="text-[10px] text-emerald-400 font-mono font-medium">
                {currentUser?.roles ? currentUser.roles.join(', ') : 'ADMIN, MANAGER'}
              </span>
            </div>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-tr from-emerald-500 to-teal-600 text-white shadow-sm shadow-emerald-500/20">
              {isSwitching ? (
                <RefreshCw className="h-4 w-4 animate-spin text-white" />
              ) : (
                <User className="h-4 w-4 text-white" />
              )}
            </div>
            <ChevronDown className={`h-3.5 w-3.5 text-slate-500 transition-transform duration-200 ${showPersonaMenu ? 'rotate-180' : ''}`} />
          </button>

          {/* Persona Switcher Dropdown */}
          {showPersonaMenu && (
            <div className="absolute right-0 mt-2 w-72 rounded-2xl border border-white/[0.1] bg-slate-950/95 p-2 shadow-2xl backdrop-blur-2xl z-50">
              <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-slate-400 border-b border-white/[0.06] mb-1 flex items-center justify-between">
                <span>Switch Role Persona</span>
                <span className="text-[9px] text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">RBAC Live</span>
              </div>
              <div className="space-y-1">
                {DEMO_PERSONAS.map((persona) => {
                  const isCurrent = currentUser?.username === persona.username;
                  return (
                    <button
                      key={persona.username}
                      onClick={() => handleSwitchPersona(persona.username)}
                      className={`flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-left text-xs transition-all ${
                        isCurrent
                          ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 font-semibold shadow-sm'
                          : 'text-slate-300 hover:bg-slate-900 hover:text-white'
                      }`}
                    >
                      <div className="flex items-center gap-2.5">
                        <div className={`h-7 w-7 rounded-lg bg-gradient-to-tr ${persona.color} flex items-center justify-center text-white text-[11px] font-bold shadow-sm`}>
                          {persona.name.charAt(0)}
                        </div>
                        <div>
                          <div className="font-semibold text-slate-200">{persona.name}</div>
                          <div className="text-[10px] text-slate-400">{persona.title}</div>
                        </div>
                      </div>
                      <span className={`text-[9px] font-mono font-medium px-2 py-0.5 rounded-full border ${persona.badgeColor}`}>
                        {persona.role}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
