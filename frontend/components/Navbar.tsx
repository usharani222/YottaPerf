'use client';

import React, { useState } from 'react';
import { Shield, Sparkles, Bell, User, CheckCircle2, ChevronDown, RefreshCw, LogIn } from 'lucide-react';
import { UserProfile } from '../types';
import { api } from '../services/api';

interface NavbarProps {
  currentUser: UserProfile | null;
  activeCycleName: string;
  onRefresh?: () => void;
}

const DEMO_PERSONAS = [
  { username: 'eleanor.vance', name: 'Eleanor Vance', title: 'CEO', role: 'ADMIN, MANAGER' },
  { username: 'marcus.chen', name: 'Marcus Chen', title: 'VP People Ops', role: 'HR_PARTNER' },
  { username: 'devon.ross', name: 'Devon Ross', title: 'Director Cloud Eng', role: 'IT_OPS' },
  { username: 'sarah.jenkins', name: 'Sarah Jenkins', title: 'Eng Manager', role: 'MANAGER' },
  { username: 'david.miller', name: 'David Miller', title: 'Senior Backend Eng', role: 'EMPLOYEE' },
];

export const Navbar: React.FC<NavbarProps> = ({ currentUser, activeCycleName, onRefresh }) => {
  const [showPersonaMenu, setShowPersonaMenu] = useState(false);
  const [isSwitching, setIsSwitching] = useState(false);

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

        {/* Refresh Button */}
        {onRefresh && (
          <button
            onClick={onRefresh}
            title="Refresh Data Telemetry"
            className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-800 bg-slate-900/60 text-slate-400 hover:text-white hover:border-slate-700 transition"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        )}

        {/* User Profile & Persona Switcher Capsule */}
        <div className="relative">
          <button
            onClick={() => setShowPersonaMenu(!showPersonaMenu)}
            disabled={isSwitching}
            className="flex items-center gap-3 rounded-lg border border-slate-800 bg-slate-900/80 p-1.5 pl-3 hover:border-slate-700 transition"
          >
            <div className="flex flex-col text-right">
              <span className="text-xs font-semibold text-white">
                {currentUser?.full_name || 'Eleanor Vance (CEO)'}
              </span>
              <span className="text-[10px] text-indigo-400 font-mono">
                {currentUser?.roles ? currentUser.roles.join(', ') : 'ADMIN, MANAGER'}
              </span>
            </div>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600/30 text-indigo-300 border border-indigo-500/30">
              {isSwitching ? <RefreshCw className="h-4 w-4 animate-spin" /> : <User className="h-4 w-4" />}
            </div>
            <ChevronDown className="h-3.5 w-3.5 text-slate-500" />
          </button>

          {/* Persona Switcher Dropdown */}
          {showPersonaMenu && (
            <div className="absolute right-0 mt-2 w-64 rounded-xl border border-slate-800 bg-slate-900 p-2 shadow-2xl z-50 animate-in fade-in slide-in-from-top-2 duration-150">
              <div className="px-2 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-slate-400 border-b border-slate-800 mb-1">
                Switch Test Persona (RBAC)
              </div>
              <div className="space-y-1">
                {DEMO_PERSONAS.map((persona) => {
                  const isCurrent = currentUser?.username === persona.username;
                  return (
                    <button
                      key={persona.username}
                      onClick={() => handleSwitchPersona(persona.username)}
                      className={`flex w-full items-center justify-between rounded-lg px-2.5 py-2 text-left text-xs transition ${
                        isCurrent
                          ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 font-semibold'
                          : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                      }`}
                    >
                      <div>
                        <div className="font-medium text-slate-200">{persona.name}</div>
                        <div className="text-[10px] text-slate-400">{persona.title}</div>
                      </div>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
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
