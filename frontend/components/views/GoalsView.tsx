'use client';

import React, { useState } from 'react';
import {
  Target, Plus, TrendingUp, History, CheckCircle, AlertCircle,
  Edit3, ExternalLink, FileText, CheckCircle2, Clock, MessageSquare,
  Sparkles, Filter, ChevronRight, ShieldCheck, UserCheck
} from 'lucide-react';
import { Goal, GoalHistory, Employee, ReviewCycle, CheckIn, Evidence } from '../../types';
import { api } from '../../services/api';

interface GoalsViewProps {
  goals: Goal[];
  employees: Employee[];
  cycles: ReviewCycle[];
  onRefresh: () => void;
}

interface TimelineEvent {
  id: string;
  type: 'CREATION' | 'GOAL_UPDATE' | 'CHECK_IN' | 'EVIDENCE' | 'APPROVAL';
  title: string;
  timestamp: string;
  actor?: string;
  description?: string;
  progress?: number;
  evidences?: Evidence[];
  managerFeedback?: string;
  badge?: string;
  badgeColor?: string;
}

export const GoalsView: React.FC<GoalsViewProps> = ({ goals, employees, cycles, onRefresh }) => {
  const [selectedGoal, setSelectedGoal] = useState<Goal | null>(null);
  const [timelineEvents, setTimelineEvents] = useState<TimelineEvent[]>([]);
  const [timelineLoading, setTimelineLoading] = useState(false);
  const [timelineFilter, setTimelineFilter] = useState<'ALL' | 'CHECK_INS' | 'UPDATES'>('ALL');
  const [showTimelineModal, setShowTimelineModal] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showKRModal, setShowKRModal] = useState(false);

  // New Goal State
  const [newTitle, setNewTitle] = useState('');
  const [newEmployeeId, setNewEmployeeId] = useState('');
  const [newCycleId, setNewCycleId] = useState('CYCLE-2026-H1');
  const [newCategory, setNewCategory] = useState('TECHNICAL');
  const [newPriority, setNewPriority] = useState('HIGH');
  const [formError, setFormError] = useState('');

  // KR Update State
  const [activeKRId, setActiveKRId] = useState('');
  const [updateVal, setUpdateVal] = useState<number>(0);

  const viewEvidenceTimeline = async (goal: Goal) => {
    setSelectedGoal(goal);
    setShowTimelineModal(true);
    setTimelineLoading(true);
    try {
      const [histories, checkIns] = await Promise.all([
        api.getGoalHistory(goal.goal_id).catch(() => []),
        api.getCheckIns({ goal_id: goal.goal_id }).catch(() => [])
      ]);

      const events: TimelineEvent[] = [];

      // 1. Inception Event
      events.push({
        id: `init-${goal.goal_id}`,
        type: 'CREATION',
        title: 'Goal Established & Registered in Cycle',
        timestamp: goal.start_date || '2026-01-01',
        actor: goal.created_by || goal.employee_id,
        description: `Objective registered with weight ${goal.weight} and priority ${goal.priority}.`,
        progress: 0,
        badge: 'CREATED',
        badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
      });

      // 2. Goal Version Changes
      histories.forEach((h: GoalHistory) => {
        events.push({
          id: h.history_id,
          type: 'GOAL_UPDATE',
          title: `Goal Version ${h.version_number} Transition: ${h.status}`,
          timestamp: h.changed_at,
          actor: h.changed_by,
          description: `Reason: ${h.change_reason || 'Periodic state reconciliation'}. Progress computed at ${h.calculated_progress}%.`,
          progress: Number(h.calculated_progress),
          badge: `V${h.version_number} • ${h.status}`,
          badgeColor: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
        });
      });

      // 3. Check-ins & Evidence Uploads
      checkIns.forEach((ci: CheckIn) => {
        events.push({
          id: ci.check_in_id,
          type: ci.evidences && ci.evidences.length > 0 ? 'EVIDENCE' : 'CHECK_IN',
          title: `Progress Check-in & Evidence Log (${ci.progress_update}%)`,
          timestamp: ci.check_in_date,
          actor: ci.employee_id,
          description: ci.employee_comments,
          progress: Number(ci.progress_update),
          managerFeedback: ci.manager_comments,
          evidences: ci.evidences,
          badge: ci.evidences && ci.evidences.length > 0 ? 'EVIDENCE ATTACHED' : 'CHECK-IN',
          badgeColor: ci.evidences && ci.evidences.length > 0
            ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20'
            : 'bg-teal-500/10 text-teal-400 border-teal-500/20'
        });
      });

      // Sort chronologically (oldest to newest)
      events.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
      setTimelineEvents(events);
    } catch (err: any) {
      console.error('Failed to construct evidence timeline:', err);
    } finally {
      setTimelineLoading(false);
    }
  };

  const handleCreateGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');
    try {
      const randomSuffix = Math.floor(100 + Math.random() * 900);
      const goalId = `GOAL-${newEmployeeId}-${randomSuffix}`;
      await api.createGoal({
        goal_id: goalId,
        employee_id: newEmployeeId,
        review_cycle_id: newCycleId,
        title: newTitle,
        category: newCategory,
        priority: newPriority,
        start_date: '2026-01-01',
        due_date: '2026-06-30',
        weight: 1.0
      });
      setShowCreateModal(false);
      setNewTitle('');
      onRefresh();
    } catch (err: any) {
      setFormError(err.message || 'Failed to create goal');
    }
  };

  const handleUpdateKR = async (krId: string) => {
    try {
      await api.updateKeyResultValue(krId, Number(updateVal));
      setShowKRModal(false);
      onRefresh();
    } catch (err: any) {
      alert('Error updating Key Result: ' + err.message);
    }
  };

  const filteredEvents = timelineEvents.filter(ev => {
    if (timelineFilter === 'CHECK_INS') return ev.type === 'CHECK_IN' || ev.type === 'EVIDENCE';
    if (timelineFilter === 'UPDATES') return ev.type === 'GOAL_UPDATE' || ev.type === 'CREATION';
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Target className="h-6 w-6 text-emerald-400" />
            Strategic Goals & Measurable Key Results
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            OKR governance with formula-derived progress tracking and immutable chronological evidence audit trails.
          </p>
        </div>
        <button
          onClick={() => {
            setShowCreateModal(true);
            setFormError('');
          }}
          className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 px-4 py-2 text-xs font-semibold text-white shadow-lg shadow-emerald-500/20 hover:from-emerald-400 hover:to-teal-500 transition"
        >
          <Plus className="h-4 w-4" />
          <span>Establish Goal</span>
        </button>
      </div>

      {/* Goals Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {goals.slice(0, 40).map((g) => {
          const progress = Number(g.calculated_progress || 0);
          return (
            <div
              key={g.goal_id}
              className="rounded-2xl border border-white/[0.08] bg-slate-900/40 backdrop-blur-xl p-5 space-y-4 hover:border-emerald-500/40 hover:shadow-xl hover:shadow-emerald-500/5 transition-all duration-300"
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-semibold text-emerald-400">{g.goal_id}</span>
                    <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                      g.priority === 'CRITICAL' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                      g.priority === 'HIGH' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                      'bg-slate-800 text-slate-300 border border-white/[0.05]'
                    }`}>
                      {g.priority}
                    </span>
                    <span className="rounded-full bg-slate-800/60 px-2 py-0.5 text-[10px] font-medium text-slate-400 border border-white/[0.05]">
                      {g.category}
                    </span>
                  </div>
                  <h3 className="text-sm font-semibold text-white mt-1.5">{g.title}</h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Owner: <span className="font-mono text-slate-300">{g.employee_id}</span> | Cycle: {g.review_cycle_id}
                  </p>
                </div>

                <button
                  onClick={() => viewEvidenceTimeline(g)}
                  title="View Chronological Evidence Timeline"
                  className="rounded-xl p-2 text-slate-400 hover:bg-slate-800 hover:text-emerald-400 border border-transparent hover:border-white/[0.05] transition flex items-center gap-1.5 text-xs font-medium"
                >
                  <History className="h-4 w-4 text-emerald-400" />
                  <span className="hidden sm:inline">Timeline</span>
                </button>
              </div>

              {/* Progress Bar */}
              <div>
                <div className="flex items-center justify-between text-xs mb-1.5">
                  <span className="text-slate-400">Calculated Weighted Progress</span>
                  <span className="font-mono font-bold text-emerald-400">{progress}%</span>
                </div>
                <div className="h-2 w-full rounded-full bg-slate-800/80 overflow-hidden">
                  <div
                    className={`h-full transition-all duration-500 ${
                      progress >= 100 ? 'bg-gradient-to-r from-emerald-500 to-teal-400' :
                      progress >= 70 ? 'bg-gradient-to-r from-teal-500 to-cyan-400' :
                      progress >= 40 ? 'bg-gradient-to-r from-amber-500 to-orange-400' : 'bg-rose-500'
                    }`}
                    style={{ width: `${Math.min(100, progress)}%` }}
                  />
                </div>
              </div>

              {/* Child Key Results */}
              {g.key_results && g.key_results.length > 0 && (
                <div className="pt-2 border-t border-slate-800/80 space-y-2">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    Key Results ({g.key_results.length})
                  </span>
                  <div className="space-y-1.5">
                    {g.key_results.map((kr) => (
                      <div
                        key={kr.key_result_id}
                        className="flex items-center justify-between rounded-lg bg-slate-950/60 p-2.5 text-xs border border-slate-800/60"
                      >
                        <div className="space-y-0.5">
                          <p className="font-medium text-slate-200">{kr.metric_name}</p>
                          <p className="text-[10px] text-slate-500">
                            Base: {kr.baseline_value} → Target: {kr.target_value} ({kr.unit}) | Direction: {kr.metric_direction}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold font-mono text-cyan-400">{kr.progress_percentage}%</span>
                          <button
                            onClick={() => {
                              setActiveKRId(kr.key_result_id);
                              setUpdateVal(kr.current_value);
                              setShowKRModal(true);
                            }}
                            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
                            title="Update measured observation"
                          >
                            <Edit3 className="h-3 w-3" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Chronological Evidence Timeline Modal */}
      {showTimelineModal && selectedGoal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
          <div className="w-full max-w-2xl max-h-[90vh] rounded-2xl border border-white/[0.08] bg-slate-950 p-6 shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
            {/* Modal Header */}
            <div className="flex items-start justify-between pb-4 border-b border-white/[0.08]">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-semibold text-emerald-400">{selectedGoal.goal_id}</span>
                  <span className="text-xs text-slate-400">• {selectedGoal.category}</span>
                </div>
                <h3 className="text-base font-bold text-white mt-1">{selectedGoal.title}</h3>
                <p className="text-xs text-slate-400">Owner: {selectedGoal.employee_id} | Cycle: {selectedGoal.review_cycle_id}</p>
              </div>

              <button
                onClick={() => setShowTimelineModal(false)}
                className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white transition"
              >
                ✕
              </button>
            </div>

            {/* Filter buttons */}
            <div className="flex items-center gap-2 py-3 border-b border-white/[0.06] text-xs">
              <span className="text-[11px] text-slate-400 font-medium">Filter Timeline:</span>
              {(['ALL', 'CHECK_INS', 'UPDATES'] as const).map(mode => (
                <button
                  key={mode}
                  onClick={() => setTimelineFilter(mode)}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition ${
                    timelineFilter === mode
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      : 'bg-slate-900 text-slate-400 hover:text-white border border-white/[0.05]'
                  }`}
                >
                  {mode === 'ALL' ? 'All Events' : mode === 'CHECK_INS' ? 'Check-ins & Evidence' : 'Goal Transitions'}
                </button>
              ))}
            </div>

            {/* Timeline Stream */}
            <div className="flex-1 overflow-y-auto py-4 space-y-4 pr-1">
              {timelineLoading ? (
                <div className="py-12 text-center text-xs text-slate-400 flex flex-col items-center gap-2">
                  <div className="h-5 w-5 rounded-full border-2 border-emerald-500 border-t-transparent animate-spin" />
                  <span>Loading chronological audit trail...</span>
                </div>
              ) : filteredEvents.length === 0 ? (
                <div className="py-12 text-center text-xs text-slate-500">
                  No chronological events found for this filter.
                </div>
              ) : (
                <div className="relative pl-6 border-l-2 border-emerald-500/30 space-y-6">
                  {filteredEvents.map((ev) => (
                    <div key={ev.id} className="relative group">
                      {/* Timeline Dot */}
                      <div className="absolute -left-[31px] top-1 h-3.5 w-3.5 rounded-full bg-slate-950 border-2 border-emerald-400 group-hover:scale-125 transition-transform" />

                      <div className="rounded-xl border border-white/[0.08] bg-slate-900/60 p-4 space-y-2">
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <div className="flex items-center gap-2">
                            <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold border ${ev.badgeColor || 'bg-slate-800 text-slate-300'}`}>
                              {ev.badge}
                            </span>
                            <span className="text-xs font-semibold text-white">{ev.title}</span>
                          </div>
                          <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
                            <Clock className="h-3 w-3 text-slate-500" />
                            {ev.timestamp}
                          </span>
                        </div>

                        {ev.description && (
                          <p className="text-xs text-slate-300 leading-relaxed">
                            {ev.description}
                          </p>
                        )}

                        {ev.managerFeedback && (
                          <div className="rounded-lg bg-teal-950/30 border border-teal-500/20 p-2.5 text-xs text-teal-300">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-teal-400 block mb-0.5">Manager Feedback</span>
                            "{ev.managerFeedback}"
                          </div>
                        )}

                        {/* Evidence Artifacts */}
                        {ev.evidences && ev.evidences.length > 0 && (
                          <div className="pt-2 border-t border-white/[0.06] space-y-1.5">
                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                              Verified Evidence Artifacts
                            </span>
                            {ev.evidences.map(art => (
                              <div key={art.evidence_id} className="flex items-center justify-between bg-slate-950/70 p-2 rounded-lg border border-white/[0.05] text-xs">
                                <div className="flex items-center gap-2 truncate">
                                  <FileText className="h-3.5 w-3.5 text-cyan-400 shrink-0" />
                                  <span className="truncate text-slate-300">{art.description || art.evidence_type}</span>
                                </div>
                                <div className="flex items-center gap-2 shrink-0">
                                  <span className="rounded bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold text-emerald-400 border border-emerald-500/20">
                                    {art.verification_status}
                                  </span>
                                  {art.reference_url && (
                                    <a
                                      href={art.reference_url}
                                      target="_blank"
                                      rel="noreferrer"
                                      className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 text-[11px]"
                                    >
                                      <ExternalLink className="h-3 w-3" />
                                      <span>Open Artifact</span>
                                    </a>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        )}

                        <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono pt-1">
                          <span>Recorded by: {ev.actor}</span>
                          {ev.progress !== undefined && (
                            <span className="text-emerald-400 font-bold">Progress: {ev.progress}%</span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="pt-3 border-t border-white/[0.08] flex justify-end">
              <button
                onClick={() => setShowTimelineModal(false)}
                className="rounded-xl bg-slate-800 px-4 py-2 text-xs font-semibold text-white hover:bg-slate-700 transition"
              >
                Close Audit View
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Goal Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl border border-white/[0.08] bg-slate-900 p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white">Establish Strategic Goal</h3>
            <p className="text-xs text-slate-400 mt-1">Create an objective tied to an active review cycle.</p>

            {formError && (
              <div className="mt-3 rounded-lg border border-rose-500/30 bg-rose-950/40 p-2.5 text-xs text-rose-300">
                {formError}
              </div>
            )}

            <form onSubmit={handleCreateGoal} className="mt-4 space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Goal Title</label>
                <input
                  required
                  type="text"
                  placeholder="e.g. Implement Zero-Downtime Blue/Green Deployments"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Goal Owner</label>
                <select
                  required
                  value={newEmployeeId}
                  onChange={(e) => setNewEmployeeId(e.target.value)}
                  className="w-full h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-emerald-500 focus:outline-none"
                >
                  <option value="">Select Employee...</option>
                  {employees.map(e => (
                    <option key={e.employee_id} value={e.employee_id}>
                      {e.full_name} ({e.employee_id})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Category</label>
                  <select
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value)}
                    className="w-full h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-emerald-500 focus:outline-none"
                  >
                    <option value="TECHNICAL">TECHNICAL</option>
                    <option value="DELIVERY">DELIVERY</option>
                    <option value="LEADERSHIP">LEADERSHIP</option>
                    <option value="CUSTOMER">CUSTOMER</option>
                    <option value="LEARNING">LEARNING</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Priority</label>
                  <select
                    value={newPriority}
                    onChange={(e) => setNewPriority(e.target.value)}
                    className="w-full h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-emerald-500 focus:outline-none"
                  >
                    <option value="LOW">LOW</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="HIGH">HIGH</option>
                    <option value="CRITICAL">CRITICAL</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-lg bg-emerald-600 px-4 py-2 text-xs font-semibold text-white hover:bg-emerald-500 shadow-md shadow-emerald-600/30"
                >
                  Create Goal
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Key Result Value Update Modal */}
      {showKRModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-sm rounded-2xl border border-white/[0.08] bg-slate-900 p-6 shadow-2xl">
            <h3 className="text-base font-bold text-white">Record Key Result Metric</h3>
            <p className="text-xs text-slate-400 mt-1">Updates current observation and recalculates goal progress.</p>
            <div className="mt-4">
              <label className="block text-xs font-medium text-slate-300 mb-1">Observed Current Value</label>
              <input
                type="number"
                step="any"
                value={updateVal}
                onChange={(e) => setUpdateVal(Number(e.target.value))}
                className="w-full h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-emerald-500 focus:outline-none"
              />
            </div>
            <div className="mt-4 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowKRModal(false)}
                className="px-3 py-1.5 text-xs text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => handleUpdateKR(activeKRId)}
                className="rounded-lg bg-emerald-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-emerald-500"
              >
                Update & Reconcile
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
