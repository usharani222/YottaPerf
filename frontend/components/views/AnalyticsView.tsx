'use client';

import React, { useState, useEffect } from 'react';
import {
  BarChart3, PieChart as PieIcon, Target, Award, Compass,
  ShieldAlert, GraduationCap, Filter, RefreshCw, CheckCircle2,
  TrendingUp, AlertCircle, ArrowUpRight, Zap
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, CartesianGrid, ReferenceLine
} from 'recharts';
import { api } from '../../services/api';
import { ReviewCycle, DevelopmentPlan } from '../../types';

interface AnalyticsViewProps {
  goalStats: any[];
  reviewStats: any;
  competencyStats: any[];
  anomalyStats: any;
  developmentPlans?: DevelopmentPlan[];
  cycles?: ReviewCycle[];
}

const PALETTE = [
  '#10b981', // Emerald
  '#06b6d4', // Cyan
  '#6366f1', // Indigo
  '#f59e0b', // Amber
  '#f43f5e', // Rose
  '#8b5cf6', // Violet
  '#3b82f6', // Blue
  '#ec4899'  // Pink
];

export const AnalyticsView: React.FC<AnalyticsViewProps> = ({
  goalStats: initialGoalStats,
  reviewStats: initialReviewStats,
  competencyStats: initialCompetencyStats,
  anomalyStats: initialAnomalyStats,
  developmentPlans = [],
  cycles = []
}) => {
  const [selectedDept, setSelectedDept] = useState('ALL');
  const [selectedCycle, setSelectedCycle] = useState('ALL');
  const [isFiltering, setIsFiltering] = useState(false);

  const [filteredGoals, setFilteredGoals] = useState<any[]>(initialGoalStats);
  const [filteredReviews, setFilteredReviews] = useState<any>(initialReviewStats);
  const [filteredCompetencies, setFilteredCompetencies] = useState<any[]>(initialCompetencyStats);

  useEffect(() => {
    setFilteredGoals(initialGoalStats);
  }, [initialGoalStats]);

  useEffect(() => {
    setFilteredReviews(initialReviewStats);
  }, [initialReviewStats]);

  useEffect(() => {
    setFilteredCompetencies(initialCompetencyStats);
  }, [initialCompetencyStats]);

  const departments = [
    'ALL',
    'Engineering',
    'Product',
    'Operations',
    'Sales',
    'Marketing',
    'Customer Success',
    'Finance',
    'HR'
  ];

  const handleFilterChange = async (dept: string, cycle: string) => {
    setIsFiltering(true);
    try {
      const params: { department?: string; review_cycle_id?: string } = {};
      if (dept !== 'ALL') params.department = dept;
      if (cycle !== 'ALL') params.review_cycle_id = cycle;

      const [gRes, rRes, cRes] = await Promise.all([
        api.getGoalAnalytics(params),
        api.getReviewAnalytics(params),
        api.getCompetencyAnalytics(params)
      ]);

      setFilteredGoals(gRes);
      setFilteredReviews(rRes);
      setFilteredCompetencies(cRes);
    } catch (err) {
      console.error('Failed to filter analytics:', err);
    } finally {
      setIsFiltering(false);
    }
  };

  // 1. Goal Progress by Department
  const goalChartData = (filteredGoals && filteredGoals.length > 0)
    ? filteredGoals.map(item => ({
        department: item.department || 'Dept',
        avg_progress: Number(item.avg_progress || item.progress || 0),
        total_goals: Number(item.total_goals || item.total || 0)
      }))
    : [];

  // 2. Review Performance Rating Distribution
  const ratingData = (filteredReviews?.rating_distribution || []).map((r: any) => ({
    category: (r.category || 'RATING').replace(/_/g, ' '),
    count: Number(r.count || 0)
  }));

  // 3. Review Lifecycle Stages (Mutually Exclusive)
  const stageData = (filteredReviews?.stage_distribution || []).map((s: any) => ({
    stage: (s.stage || 'STAGE').replace(/_/g, ' '),
    count: Number(s.count || 0)
  })).filter((s: any) => s.count > 0);

  // 4. Competency Evaluations
  const competencyData = (filteredCompetencies || []).map((c: any) => ({
    category: (c.category || 'COMPETENCY').replace(/_/g, ' '),
    avg_rating: Number(Number(c.avg_rating || 0).toFixed(2)),
    evaluations_count: Number(c.count || 0)
  }));

  // 5. Development Plan Status & Approval Breakdown
  const devPlanStatusCounts: Record<string, number> = {};
  developmentPlans.forEach(p => {
    const statusKey = `${p.approval_status || 'PENDING'} • ${p.status || 'ACTIVE'}`.replace(/_/g, ' ');
    devPlanStatusCounts[statusKey] = (devPlanStatusCounts[statusKey] || 0) + 1;
  });
  const devPlanChartData = Object.entries(devPlanStatusCounts).map(([status, count]) => ({
    status,
    count
  }));

  // 6. Anomaly Severity Breakdown
  const anomalyBySeverity = (initialAnomalyStats?.by_severity || []).map((a: any) => ({
    severity: a.severity,
    count: Number(a.count || 0)
  }));

  const anomalyByType = (initialAnomalyStats?.by_type || []).map((a: any) => ({
    issue_type: (a.issue_type || '').replace(/_/g, ' '),
    count: Number(a.count || 0)
  }));

  return (
    <div className="space-y-6">
      {/* Header and Filter Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-white/[0.08]">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <BarChart3 className="h-6 w-6 text-emerald-400" />
            Executive Performance Intelligence & Telemetry Analytics
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Reconciled enterprise visualizations aggregated directly from normalized relational database tables.
          </p>
        </div>

        {/* Global Chart Filters */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
            <Filter className="h-3.5 w-3.5 text-emerald-400" />
            <span>Chart Scope:</span>
          </div>

          <select
            value={selectedDept}
            onChange={(e) => {
              const val = e.target.value;
              setSelectedDept(val);
              handleFilterChange(val, selectedCycle);
            }}
            className="h-8.5 rounded-lg border border-white/[0.08] bg-slate-900 px-3 text-xs text-slate-200 focus:border-emerald-500 focus:outline-none"
          >
            {departments.map(d => (
              <option key={d} value={d}>
                {d === 'ALL' ? 'All Departments' : d}
              </option>
            ))}
          </select>

          <select
            value={selectedCycle}
            onChange={(e) => {
              const val = e.target.value;
              setSelectedCycle(val);
              handleFilterChange(selectedDept, val);
            }}
            className="h-8.5 rounded-lg border border-white/[0.08] bg-slate-900 px-3 text-xs text-slate-200 focus:border-emerald-500 focus:outline-none"
          >
            <option value="ALL">All Review Cycles</option>
            {cycles.map(c => (
              <option key={c.cycle_id} value={c.cycle_id}>
                {c.cycle_id} ({c.cycle_name})
              </option>
            ))}
            {cycles.length === 0 && (
              <>
                <option value="CYCLE-2026-H1">CYCLE-2026-H1</option>
                <option value="CYCLE-2025-H2">CYCLE-2025-H2</option>
              </>
            )}
          </select>

          {isFiltering && (
            <span className="flex items-center gap-1 text-[11px] text-emerald-400 font-mono">
              <RefreshCw className="h-3 w-3 animate-spin" />
              <span>Querying...</span>
            </span>
          )}
        </div>
      </div>

      {/* 6-Chart Multi-Dimensional Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* 1. Goal Progress by Department */}
        <div className="rounded-2xl border border-white/[0.08] bg-slate-900/40 p-5 backdrop-blur-2xl shadow-xl space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-white/[0.06]">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <Target className="h-4 w-4 text-emerald-400" />
                Departmental Goal Completion (%)
              </h2>
              <p className="text-[11px] text-slate-400">Average weighted Key Result execution by organizational unit</p>
            </div>
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
              Target: 75%
            </span>
          </div>

          <div className="h-64 w-full">
            {goalChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={goalChartData} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
                  <XAxis dataKey="department" stroke="#64748b" fontSize={10} angle={-20} textAnchor="end" />
                  <YAxis stroke="#64748b" fontSize={10} domain={[0, 100]} unit="%" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#090d16', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '10px', color: '#fff', fontSize: '11px' }}
                    formatter={(val: any, name: any, item: any) => [
                      `${val}% (${item?.payload?.total_goals || 0} Total Goals)`,
                      'Avg Progress'
                    ]}
                  />
                  <ReferenceLine y={75} stroke="#10b981" strokeDasharray="4 4" label={{ value: 'Target 75%', fill: '#10b981', fontSize: 10, position: 'top' }} />
                  <Bar dataKey="avg_progress" fill="#10b981" radius={[4, 4, 0, 0]} maxBarSize={40} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-500">
                No goal records match active filters.
              </div>
            )}
          </div>
        </div>

        {/* 2. Employee Performance Distribution */}
        <div className="rounded-2xl border border-white/[0.08] bg-slate-900/40 p-5 backdrop-blur-2xl shadow-xl space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-white/[0.06]">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <Award className="h-4 w-4 text-cyan-400" />
                Performance Rating Calibration Distribution
              </h2>
              <p className="text-[11px] text-slate-400">Standardized rating categories assigned in final calibration</p>
            </div>
            <span className="text-[10px] font-mono text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded-full border border-cyan-500/20">
              Calibrated
            </span>
          </div>

          <div className="h-64 w-full">
            {ratingData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={ratingData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
                  <XAxis dataKey="category" stroke="#64748b" fontSize={10} angle={-15} textAnchor="end" />
                  <YAxis stroke="#64748b" fontSize={10} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#090d16', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '10px', color: '#fff', fontSize: '11px' }}
                    formatter={(val: any) => [`${val} Employees`, 'Count']}
                  />
                  <Bar dataKey="count" fill="#06b6d4" radius={[4, 4, 0, 0]} maxBarSize={45}>
                    {ratingData.map((_: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={PALETTE[index % PALETTE.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-500">
                No rating distributions match active filters.
              </div>
            )}
          </div>
        </div>

        {/* 3. Review Lifecycle Stage Distribution */}
        <div className="rounded-2xl border border-white/[0.08] bg-slate-900/40 p-5 backdrop-blur-2xl shadow-xl space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-white/[0.06]">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-purple-400" />
                Review Workflow Progression
              </h2>
              <p className="text-[11px] text-slate-400">Mutually exclusive status breakdown across the review cycle</p>
            </div>
            <span className="text-[10px] font-mono text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded-full border border-purple-500/20">
              Mutually Exclusive
            </span>
          </div>

          <div className="h-64 w-full flex items-center justify-center">
            {stageData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={stageData}
                    dataKey="count"
                    nameKey="stage"
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={3}
                  >
                    {stageData.map((_: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={PALETTE[index % PALETTE.length]} stroke="rgba(3,7,18,0.8)" strokeWidth={2} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#090d16', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '10px', color: '#fff', fontSize: '11px' }}
                    formatter={(val: any, name: any) => [`${val} Reviews`, name]}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-xs text-slate-500">No review cycle records found.</div>
            )}
          </div>
        </div>

        {/* 4. Competency Evaluations (1.0 - 5.0) */}
        <div className="rounded-2xl border border-white/[0.08] bg-slate-900/40 p-5 backdrop-blur-2xl shadow-xl space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-white/[0.06]">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <Compass className="h-4 w-4 text-emerald-400" />
                360° Competency Capability Benchmarks
              </h2>
              <p className="text-[11px] text-slate-400">Multi-source average evaluation score across core capability pillars</p>
            </div>
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
              1.0 - 5.0 Scale
            </span>
          </div>

          <div className="h-64 w-full">
            {competencyData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={competencyData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
                  <XAxis dataKey="category" stroke="#64748b" fontSize={10} angle={-15} textAnchor="end" />
                  <YAxis stroke="#64748b" fontSize={10} domain={[0, 5]} ticks={[1, 2, 3, 4, 5]} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#090d16', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '10px', color: '#fff', fontSize: '11px' }}
                    formatter={(val: any, name: any, item: any) => [
                      `${val} / 5.0 (${item?.payload?.evaluations_count || 0} reviews)`,
                      'Score'
                    ]}
                  />
                  <Bar dataKey="avg_rating" fill="#10b981" radius={[4, 4, 0, 0]} maxBarSize={45} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-500">
                No competency evaluations recorded.
              </div>
            )}
          </div>
        </div>

        {/* 5. Individual Development Plan (IDP) Execution Status */}
        <div className="rounded-2xl border border-white/[0.08] bg-slate-900/40 p-5 backdrop-blur-2xl shadow-xl space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-white/[0.06]">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <GraduationCap className="h-4 w-4 text-blue-400" />
                Development Plan Status & Approvals
              </h2>
              <p className="text-[11px] text-slate-400">Execution tracking of active employee individual growth roadmaps</p>
            </div>
            <span className="text-[10px] font-mono text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded-full border border-blue-500/20">
              {developmentPlans.length} Total Plans
            </span>
          </div>

          <div className="h-64 w-full">
            {devPlanChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={devPlanChartData} layout="vertical" margin={{ top: 10, right: 20, left: 20, bottom: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
                  <XAxis type="number" stroke="#64748b" fontSize={10} />
                  <YAxis type="category" dataKey="status" stroke="#64748b" fontSize={9} width={130} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#090d16', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '10px', color: '#fff', fontSize: '11px' }}
                    formatter={(val: any) => [`${val} Plans`, 'Count']}
                  />
                  <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} maxBarSize={28} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-500">
                No development plan records found.
              </div>
            )}
          </div>
        </div>

        {/* 6. Exception & Anomaly Distribution by Severity */}
        <div className="rounded-2xl border border-white/[0.08] bg-slate-900/40 p-5 backdrop-blur-2xl shadow-xl space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-white/[0.06]">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <ShieldAlert className="h-4 w-4 text-rose-400" />
                Exception & Anomaly Distribution
              </h2>
              <p className="text-[11px] text-slate-400">Live heuristic scanner breakdown by diagnostic severity tier</p>
            </div>
            <span className="text-[10px] font-mono text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded-full border border-rose-500/20">
              Strictly Isolated
            </span>
          </div>

          <div className="h-64 w-full">
            {anomalyBySeverity.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={anomalyBySeverity} margin={{ top: 10, right: 10, left: -20, bottom: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
                  <XAxis dataKey="severity" stroke="#64748b" fontSize={10} />
                  <YAxis stroke="#64748b" fontSize={10} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#090d16', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '10px', color: '#fff', fontSize: '11px' }}
                    formatter={(val: any) => [`${val} Anomalies`, 'Count']}
                  />
                  <Bar dataKey="count" fill="#f43f5e" radius={[4, 4, 0, 0]} maxBarSize={45}>
                    {anomalyBySeverity.map((entry: any, index: number) => {
                      const color = entry.severity === 'CRITICAL' ? '#ef4444' :
                                    entry.severity === 'HIGH' ? '#f97316' :
                                    entry.severity === 'MEDIUM' ? '#f59e0b' : '#3b82f6';
                      return <Cell key={`cell-${index}`} fill={color} />;
                    })}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-500">
                No exceptions detected.
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};
