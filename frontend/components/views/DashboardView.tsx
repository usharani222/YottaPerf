'use client';

import React from 'react';
import {
  Users, UserCheck, RefreshCw, Target, TrendingUp, CheckCircle,
  GraduationCap, AlertTriangle, ArrowUpRight, Award, Compass
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';
import { DashboardKPIs } from '../../types';

interface DashboardViewProps {
  kpis: DashboardKPIs | null;
  goalStats: any[];
  reviewStats: any;
  onNavigate: (tab: any) => void;
  onRefresh: () => void;
  loading: boolean;
}

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export const DashboardView: React.FC<DashboardViewProps> = ({
  kpis,
  goalStats,
  reviewStats,
  onNavigate,
  onRefresh,
  loading
}) => {
  const cards = [
    {
      label: 'Total Employees',
      value: kpis?.total_employees ?? '—',
      icon: Users,
      color: 'from-blue-600 to-indigo-600',
      action: () => onNavigate('employees')
    },
    {
      label: 'Total Managers',
      value: kpis?.total_managers ?? '—',
      icon: UserCheck,
      color: 'from-indigo-600 to-purple-600',
      action: () => onNavigate('organization')
    },
    {
      label: 'Active Cycles',
      value: kpis?.active_review_cycles ?? '—',
      icon: RefreshCw,
      color: 'from-emerald-600 to-teal-600',
      action: () => onNavigate('reviews')
    },
    {
      label: 'Total Goals / OKRs',
      value: kpis?.total_goals ?? '—',
      icon: Target,
      color: 'from-cyan-600 to-blue-600',
      action: () => onNavigate('goals')
    },
    {
      label: 'Avg Goal Progress',
      value: kpis ? `${kpis.average_goal_progress}%` : '—',
      icon: TrendingUp,
      color: 'from-amber-600 to-orange-600',
      action: () => onNavigate('goals')
    },
    {
      label: 'Completed Reviews',
      value: kpis?.completed_reviews ?? '—',
      icon: CheckCircle,
      color: 'from-violet-600 to-purple-600',
      action: () => onNavigate('reviews')
    },
    {
      label: 'Active Dev Plans',
      value: kpis?.development_plans_in_progress ?? '—',
      icon: GraduationCap,
      color: 'from-emerald-600 to-green-600',
      action: () => onNavigate('development')
    },
    {
      label: 'Open Anomalies',
      value: kpis?.open_anomalies ?? '—',
      icon: AlertTriangle,
      color: 'from-rose-600 to-red-600',
      action: () => onNavigate('anomalies'),
      alert: (kpis?.open_anomalies ?? 0) > 0
    },
  ];

  const ratingData = reviewStats?.rating_distribution || [];

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 rounded-2xl border border-slate-800 bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 p-6 shadow-xl">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Executive Performance Command Center</h1>
          <p className="mt-1 text-sm text-slate-400">
            Real-time organizational telemetry, evidence-verified OKRs, and calibrated reviews.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={onRefresh}
            disabled={loading}
            className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-800/80 px-4 py-2 text-sm font-medium text-slate-200 transition hover:bg-slate-700 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh Telemetry</span>
          </button>
          <button
            onClick={() => onNavigate('anomalies')}
            className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-500 shadow-md shadow-indigo-600/30"
          >
            <AlertTriangle className="h-4 w-4" />
            <span>Investigate Exceptions</span>
          </button>
        </div>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {cards.map((c, i) => {
          const Icon = c.icon;
          return (
            <div
              key={i}
              onClick={c.action}
              className={`group cursor-pointer rounded-xl border p-4 transition-all hover:scale-[1.02] shadow-sm ${
                c.alert
                  ? 'border-rose-500/30 bg-rose-950/20 hover:border-rose-500/50'
                  : 'border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400">{c.label}</span>
                <div className={`flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-tr ${c.color} text-white shadow-sm`}>
                  <Icon className="h-4 w-4" />
                </div>
              </div>
              <div className="mt-3 flex items-baseline justify-between">
                <span className={`text-2xl font-bold tracking-tight ${c.alert ? 'text-rose-400' : 'text-white'}`}>
                  {c.value}
                </span>
                <ArrowUpRight className="h-4 w-4 text-slate-600 transition group-hover:text-slate-300 group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
              </div>
            </div>
          );
        })}
      </div>

      {/* Live Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Goal Completion by Department */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-semibold text-white">Goal Progress by Department</h2>
              <p className="text-xs text-slate-400">Average weighted key result completion</p>
            </div>
            <Target className="h-5 w-5 text-indigo-400" />
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={goalStats} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <XAxis dataKey="department" stroke="#64748b" fontSize={11} angle={-25} textAnchor="end" />
                <YAxis stroke="#64748b" fontSize={11} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
                />
                <Bar dataKey="avg_progress" fill="#6366f1" radius={[4, 4, 0, 0]} name="Avg Progress %" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Performance Review Ratings Distribution */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-semibold text-white">Review Calibration Distribution</h2>
              <p className="text-xs text-slate-400">Calibrated ratings distribution across cycles</p>
            </div>
            <Award className="h-5 w-5 text-purple-400" />
          </div>
          <div className="h-64 w-full flex items-center justify-center">
            {ratingData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={ratingData}
                    dataKey="count"
                    nameKey="category"
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={4}
                  >
                    {ratingData.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-xs text-slate-500">Loading distribution metrics...</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
