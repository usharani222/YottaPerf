'use client';

import React from 'react';
import {
  LayoutDashboard, Users, Network, Target, CalendarCheck,
  MessageSquareQuote, Award, Compass, GraduationCap, ShieldAlert,
  BarChart3, History, Sliders
} from 'lucide-react';

export type TabType =
  | 'dashboard'
  | 'employees'
  | 'organization'
  | 'goals'
  | 'checkins'
  | 'feedback'
  | 'reviews'
  | 'competencies'
  | 'development'
  | 'anomalies'
  | 'analytics'
  | 'audit'
  | 'admin';

interface SidebarProps {
  currentTab: TabType;
  onSelectTab: (tab: TabType) => void;
  openAnomalyCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onSelectTab, openAnomalyCount = 0 }) => {
  const navItems = [
    { id: 'dashboard' as TabType, label: 'Dashboard', icon: LayoutDashboard },
    { id: 'employees' as TabType, label: 'Employees', icon: Users },
    { id: 'organization' as TabType, label: 'Organization', icon: Network },
    { id: 'goals' as TabType, label: 'Goals & OKRs', icon: Target },
    { id: 'checkins' as TabType, label: 'Check-ins', icon: CalendarCheck },
    { id: 'feedback' as TabType, label: '360° Feedback', icon: MessageSquareQuote },
    { id: 'reviews' as TabType, label: 'Performance Reviews', icon: Award },
    { id: 'competencies' as TabType, label: 'Competencies', icon: Compass },
    { id: 'development' as TabType, label: 'Development Plans', icon: GraduationCap },
    {
      id: 'anomalies' as TabType,
      label: 'Anomaly Center',
      icon: ShieldAlert,
      badge: openAnomalyCount > 0 ? openAnomalyCount : undefined
    },
    { id: 'analytics' as TabType, label: 'Analytics', icon: BarChart3 },
    { id: 'audit' as TabType, label: 'Audit Logs', icon: History },
    { id: 'admin' as TabType, label: 'Administration', icon: Sliders },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-950 flex flex-col justify-between p-4 min-h-[calc(100vh-4rem)]">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
          Core Workflows
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-sm font-medium transition-all ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`h-4 w-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && (
                <span className={`rounded-full px-2 py-0.5 text-[11px] font-bold ${
                  isActive
                    ? 'bg-white text-indigo-700'
                    : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                }`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-3 mt-6">
        <div className="flex items-center gap-2 text-xs font-medium text-slate-300">
          <div className="h-2 w-2 rounded-full bg-emerald-400" />
          <span>PostgreSQL 3NF Connected</span>
        </div>
        <p className="mt-1 text-[11px] text-slate-500">Seed: 20261022 | Deterministic</p>
      </div>
    </aside>
  );
};
