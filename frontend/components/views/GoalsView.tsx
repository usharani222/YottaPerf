'use client';

import React, { useState } from 'react';
import { Target, Plus, TrendingUp, History, CheckCircle, AlertCircle, Edit3 } from 'lucide-react';
import { Goal, GoalHistory, Employee, ReviewCycle } from '../../types';
import { api } from '../../services/api';

interface GoalsViewProps {
  goals: Goal[];
  employees: Employee[];
  cycles: ReviewCycle[];
  onRefresh: () => void;
}

export const GoalsView: React.FC<GoalsViewProps> = ({ goals, employees, cycles, onRefresh }) => {
  const [selectedGoal, setSelectedGoal] = useState<Goal | null>(null);
  const [historyList, setHistoryList] = useState<GoalHistory[]>([]);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
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

  const viewHistory = async (goal: Goal) => {
    setSelectedGoal(goal);
    try {
      const hist = await api.getGoalHistory(goal.goal_id);
      setHistoryList(hist);
      setShowHistoryModal(true);
    } catch (e: any) {
      alert('Error fetching goal history: ' + e.message);
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

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Strategic Goals & Measurable Key Results</h1>
          <p className="text-xs text-slate-400">
            OKR governance with formula-derived progress tracking.
          </p>
        </div>
        <button
          onClick={() => {
            setShowCreateModal(true);
            setFormError('');
          }}
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-500 transition shadow-md shadow-indigo-600/30"
        >
          <Plus className="h-4 w-4" />
          <span>Establish Goal</span>
        </button>
      </div>

      {/* Goals Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {goals.slice(0, 30).map((g) => {
          const progress = Number(g.calculated_progress || 0);
          return (
            <div
              key={g.goal_id}
              className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 space-y-4 hover:border-slate-700 transition"
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-semibold text-indigo-400">{g.goal_id}</span>
                    <span className={`rounded px-1.5 py-0.5 text-[10px] font-bold ${
                      g.priority === 'CRITICAL' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                      g.priority === 'HIGH' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                      'bg-slate-800 text-slate-300'
                    }`}>
                      {g.priority}
                    </span>
                    <span className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] font-medium text-slate-400">
                      {g.category}
                    </span>
                  </div>
                  <h3 className="text-sm font-semibold text-white mt-1.5">{g.title}</h3>
                  <p className="text-xs text-slate-400">Owner: <span className="font-mono text-slate-300">{g.employee_id}</span> | Cycle: {g.review_cycle_id}</p>
                </div>

                <button
                  onClick={() => viewHistory(g)}
                  title="View Version History"
                  className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white transition"
                >
                  <History className="h-4 w-4" />
                </button>
              </div>

              {/* Progress Bar */}
              <div>
                <div className="flex items-center justify-between text-xs mb-1.5">
                  <span className="text-slate-400">Calculated Weighted Progress</span>
                  <span className="font-bold text-white">{progress}%</span>
                </div>
                <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className={`h-full transition-all duration-500 ${
                      progress >= 100 ? 'bg-emerald-500' :
                      progress >= 70 ? 'bg-indigo-500' :
                      progress >= 40 ? 'bg-amber-500' : 'bg-rose-500'
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
                        className="flex items-center justify-between rounded-lg bg-slate-950/60 p-2 text-xs border border-slate-800/60"
                      >
                        <div className="space-y-0.5">
                          <p className="font-medium text-slate-200">{kr.metric_name}</p>
                          <p className="text-[10px] text-slate-500">
                            Base: {kr.baseline_value} → Target: {kr.target_value} ({kr.unit}) | Direction: {kr.metric_direction}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-indigo-400">{kr.progress_percentage}%</span>
                          <button
                            onClick={() => {
                              setActiveKRId(kr.key_result_id);
                              setUpdateVal(kr.current_value);
                              setShowKRModal(true);
                            }}
                            className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800 transition"
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

      {/* Version History Modal */}
      {showHistoryModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white">Immutable Goal History Snapshot</h3>
            <p className="text-xs text-slate-400 mt-1">Audit log of versioned state transitions for {selectedGoal?.goal_id}</p>

            <div className="mt-4 max-h-72 overflow-y-auto space-y-3">
              {historyList.map((h) => (
                <div key={h.history_id} className="rounded-lg border border-slate-800 bg-slate-950 p-3 text-xs">
                  <div className="flex items-center justify-between text-indigo-400 font-semibold mb-1">
                    <span>Version {h.version_number} • {h.status}</span>
                    <span className="text-[10px] text-slate-500">{h.changed_at}</span>
                  </div>
                  <p className="text-slate-300 font-medium">{h.title}</p>
                  <p className="text-slate-500 text-[11px] mt-1">
                    Progress: {h.calculated_progress}% | Reason: {h.change_reason}
                  </p>
                </div>
              ))}
            </div>

            <div className="mt-4 flex justify-end">
              <button
                onClick={() => setShowHistoryModal(false)}
                className="rounded-lg bg-slate-800 px-4 py-2 text-xs font-semibold text-white hover:bg-slate-700"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Goal Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
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
                  className="w-full h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Goal Owner</label>
                <select
                  required
                  value={newEmployeeId}
                  onChange={(e) => setNewEmployeeId(e.target.value)}
                  className="w-full h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-indigo-500 focus:outline-none"
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
                    className="w-full h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-indigo-500 focus:outline-none"
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
                    className="w-full h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-indigo-500 focus:outline-none"
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
                  className="rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-500 shadow-md shadow-indigo-600/30"
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
          <div className="w-full max-w-sm rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
            <h3 className="text-base font-bold text-white">Record Key Result Metric</h3>
            <p className="text-xs text-slate-400 mt-1">Updates current observation and recalculates goal progress.</p>
            <div className="mt-4">
              <label className="block text-xs font-medium text-slate-300 mb-1">Observed Current Value</label>
              <input
                type="number"
                step="any"
                value={updateVal}
                onChange={(e) => setUpdateVal(Number(e.target.value))}
                className="w-full h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-indigo-500 focus:outline-none"
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
                className="rounded-lg bg-indigo-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-indigo-500"
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
