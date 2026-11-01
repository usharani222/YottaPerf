'use client';

import React from 'react';
import {
  BarChart3, PieChart as PieIcon, Target, Award, Compass, ShieldAlert
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';

interface AnalyticsViewProps {
  goalStats: any[];
  reviewStats: any;
  competencyStats: any[];
  anomalyStats: any;
}

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4'];

export const AnalyticsView: React.FC<AnalyticsViewProps> = ({
  goalStats,
  reviewStats,
  competencyStats,
  anomalyStats
}) => {
  const ratingData = reviewStats?.rating_distribution || [];
  const anomalyBySeverity = anomalyStats?.by_severity || [];
  const anomalyByType = anomalyStats?.by_type || [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">Management Analytics & Reporting</h1>
        <p className="text-xs text-slate-400">
          Executive visualizations computed from normalized relational telemetry.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 1. Goal Progress by Department */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white">Goal Progress by Department</h3>
              <p className="text-xs text-slate-400">Average weighted Key Result completion (%)</p>
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
                <Bar dataKey="avg_progress" fill="#6366f1" radius={[4, 4, 0, 0]} name="Progress %" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 2. Review Calibration Distribution */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white">Review Calibration Distribution</h3>
              <p className="text-xs text-slate-400">Rating category proportions</p>
            </div>
            <Award className="h-5 w-5 text-purple-400" />
          </div>
          <div className="h-64 w-full flex items-center justify-center">
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
          </div>
        </div>

        {/* 3. Competency Capability Benchmark */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white">Competency Evaluations (1.0 - 5.0)</h3>
              <p className="text-xs text-slate-400">Average 360° multi-source ratings by category</p>
            </div>
            <Compass className="h-5 w-5 text-emerald-400" />
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={competencyStats} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <XAxis dataKey="category" stroke="#64748b" fontSize={11} angle={-25} textAnchor="end" />
                <YAxis stroke="#64748b" fontSize={11} domain={[0, 5]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
                />
                <Bar dataKey="avg_rating" fill="#10b981" radius={[4, 4, 0, 0]} name="Avg Rating" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 4. Anomaly Severity Breakdown */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white">Exception Distribution by Severity</h3>
              <p className="text-xs text-slate-400">Diagnostic severity categorization</p>
            </div>
            <ShieldAlert className="h-5 w-5 text-rose-400" />
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={anomalyBySeverity} margin={{ top: 10, right: 10, left: -20, bottom: 10 }}>
                <XAxis dataKey="severity" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
                />
                <Bar dataKey="count" fill="#f43f5e" radius={[4, 4, 0, 0]} name="Anomalies" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
