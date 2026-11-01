'use client';

import React from 'react';
import {
  LayoutDashboard, Users, Network, Target, CalendarCheck,
  MessageSquareQuote, Award, Compass, GraduationCap, ShieldAlert,
  BarChart3, History, Sliders, Activity, Cpu, Sparkles
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
  const navSections = [
    {
      title: 'Command & Hierarchy',
      items: [
        { id: 'dashboard' as TabType, label: 'Executive Dashboard', icon: LayoutDashboard },
        { id: 'employees' as TabType, label: 'Employee Directory', icon: Users },
        { id: 'organization' as TabType, label: 'Org Graph & Hierarchy', icon: Network },
      ]
    },
    {
      title: 'Performance Engine',
      items: [
        { id: 'goals' as TabType, label: 'Goals & OKRs', icon: Target },
        { id: 'checkins' as TabType, label: 'Check-ins & Evidence', icon: CalendarCheck },
        { id: 'feedback' as TabType, label: '360° Feedback', icon: MessageSquareQuote },
        { id: 'reviews' as TabType, label: 'Review Calibration', icon: Award },
      ]
    },
    {
      title: 'Talent & Capabilities',
      items: [
        { id: 'competencies' as TabType, label: 'Competency Framework', icon: Compass },
        { id: 'development' as TabType, label: 'Development Plans', icon: GraduationCap },
      ]
    },
    {
      title: 'Governance & Operations',
      items: [
        {
          id: 'anomalies' as TabType,
          label: 'Anomaly Defense Center',
          icon: ShieldAlert,
          badge: openAnomalyCount > 0 ? openAnomalyCount : undefined
        },
        { id: 'analytics' as TabType, label: 'Advanced Analytics', icon: BarChart3 },
        { id: 'audit' as TabType, label: 'Cryptographic Audit', icon: History },
        { id: 'admin' as TabType, label: 'Platform Operations', icon: Sliders },
      ]
    }
  ];

  return (
    <aside className="w-64 border-r border-white/[0.08] bg-slate-950/70 backdrop-blur-2xl flex flex-col justify-between p-3.5 min-h-[calc(100vh-4rem)]">
      <div className="space-y-4">
        {navSections.map((section, sIdx) => (
          <div key={sIdx} className="space-y-1">
            <div className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-500">
              {section.title}
            </div>
            {section.items.map((item) => {
              const Icon = item.icon;
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onSelectTab(item.id)}
                  className={`group relative flex w-full items-center justify-between rounded-xl px-3 py-2 text-xs font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-emerald-500/20 via-teal-500/10 to-transparent text-emerald-300 border border-emerald-500/30 shadow-[0_0_20px_rgba(16,185,129,0.12)]'
                      : 'text-slate-400 hover:bg-slate-900/60 hover:text-slate-200 hover:border hover:border-white/[0.05]'
                  }`}
                >
                  {/* Left glowing neon pip for active tab */}
                  {isActive && (
                    <span className="absolute left-0 top-1.5 bottom-1.5 w-1 rounded-r-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
                  )}

                  <div className="flex items-center gap-2.5">
                    <Icon className={`h-4 w-4 transition-colors ${isActive ? 'text-emerald-400' : 'text-slate-400 group-hover:text-slate-200'}`} />
                    <span>{item.label}</span>
                  </div>

                  {item.badge !== undefined && (
                    <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                      isActive
                        ? 'bg-rose-500 text-white shadow-sm'
                        : 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
                    }`}>
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        ))}
      </div>

      {/* System Telemetry Capsule */}
      <div className="rounded-2xl border border-white/[0.08] bg-slate-900/50 p-3 mt-4 space-y-2 backdrop-blur-xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-200">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span>PostgreSQL 3NF</span>
          </div>
          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
            HEALTHY
          </span>
        </div>
        <div className="text-[10px] text-slate-400 flex items-center justify-between font-mono pt-1 border-t border-white/[0.05]">
          <span>Seed: 20261022</span>
          <span>Port: 5434</span>
        </div>
      </div>
    </aside>
  );
};
