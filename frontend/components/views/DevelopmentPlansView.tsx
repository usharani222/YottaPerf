'use client';

import React, { useState } from 'react';
import { GraduationCap, Plus, CheckCircle2, Clock, BookOpen, AlertCircle } from 'lucide-react';
import { DevelopmentPlan, Employee, Competency } from '../../types';
import { api } from '../../services/api';

interface DevelopmentPlansViewProps {
  plans: DevelopmentPlan[];
  employees: Employee[];
  competencies: Competency[];
  onRefresh: () => void;
}

export const DevelopmentPlansView: React.FC<DevelopmentPlansViewProps> = ({
  plans,
  employees,
  competencies,
  onRefresh
}) => {
  const [showModal, setShowModal] = useState(false);
  const [employeeId, setEmployeeId] = useState('');
  const [competencyId, setCompetencyId] = useState('COMP-TECH-01');
  const [currentLevel, setCurrentLevel] = useState('Intermediate');
  const [targetLevel, setTargetLevel] = useState('Senior');
  const [recommendedAction, setRecommendedAction] = useState('');
  const [learningResources, setLearningResources] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    try {
      const planId = `DP-${Math.floor(100000 + Math.random() * 900000)}`;
      await api.createDevelopmentPlan({
        plan_id: planId,
        employee_id: employeeId,
        competency_id: competencyId,
        current_level: currentLevel,
        target_level: targetLevel,
        recommended_action: recommendedAction,
        learning_resources: learningResources,
        start_date: '2026-02-01',
        target_completion_date: '2026-08-31'
      });
      setShowModal(false);
      onRefresh();
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to create plan');
    }
  };

  const handleApprove = async (planId: string) => {
    try {
      await api.approveDevelopmentPlan(planId, 'APPROVED', 'Approved by manager.');
      onRefresh();
    } catch (err: any) {
      alert('Error approving plan: ' + err.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Employee Development Plans</h1>
          <p className="text-xs text-slate-400">
            Targeted capability gap remediation and structured career growth roadmaps.
          </p>
        </div>
        <button
          onClick={() => {
            setShowModal(true);
            setErrorMsg('');
          }}
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-500 transition shadow-md shadow-indigo-600/30"
        >
          <Plus className="h-4 w-4" />
          <span>Formulate Development Plan</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {plans.map((p) => (
          <div
            key={p.plan_id}
            className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 space-y-3 hover:border-slate-700 transition"
          >
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-bold text-indigo-400">{p.plan_id}</span>
              <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold border ${
                p.approval_status === 'APPROVED' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                'bg-amber-500/10 text-amber-400 border-amber-500/20'
              }`}>
                {p.approval_status}
              </span>
            </div>

            <div>
              <p className="text-xs font-semibold text-white">Owner: <span className="font-mono text-indigo-300">{p.employee_id}</span></p>
              <p className="text-[11px] text-slate-400">Target: <span className="font-mono text-slate-300">{p.competency_id}</span></p>
              <div className="mt-2 flex items-center gap-2 text-xs">
                <span className="rounded bg-slate-800 px-1.5 py-0.5 text-slate-300">{p.current_level}</span>
                <span className="text-slate-500">→</span>
                <span className="rounded bg-indigo-900/40 border border-indigo-500/30 px-1.5 py-0.5 text-indigo-300 font-medium">{p.target_level}</span>
              </div>
            </div>

            <div className="rounded-lg bg-slate-950/60 p-2.5 text-xs text-slate-300 border border-slate-800/40 space-y-1.5">
              <span className="font-semibold text-slate-400 text-[10px] uppercase block">Action Plan</span>
              <p className="text-slate-300">{p.recommended_action}</p>
              {p.learning_resources && (
                <p className="text-[11px] text-indigo-400 pt-1 border-t border-slate-800/60">
                  Resources: {p.learning_resources}
                </p>
              )}
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-slate-800 text-xs">
              <span className="text-slate-500 text-[11px]">{p.start_date} to {p.target_completion_date}</span>
              {p.approval_status === 'PENDING' && (
                <button
                  onClick={() => handleApprove(p.plan_id)}
                  className="rounded bg-emerald-600 px-2.5 py-1 text-[11px] font-semibold text-white hover:bg-emerald-500"
                >
                  Approve Plan
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white">Create Development Plan</h3>
            <p className="text-xs text-slate-400 mt-1">Address competency gaps through concrete learning roadmaps.</p>

            {errorMsg && (
              <div className="mt-3 rounded-lg border border-rose-500/30 bg-rose-950/40 p-2.5 text-xs text-rose-300">
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleCreate} className="mt-4 space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Target Employee</label>
                <select
                  required
                  value={employeeId}
                  onChange={(e) => setEmployeeId(e.target.value)}
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

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Target Competency</label>
                <select
                  value={competencyId}
                  onChange={(e) => setCompetencyId(e.target.value)}
                  className="w-full h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-indigo-500 focus:outline-none"
                >
                  {competencies.map(c => (
                    <option key={c.competency_id} value={c.competency_id}>
                      {c.name} ({c.category})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Current Level</label>
                  <input
                    type="text"
                    value={currentLevel}
                    onChange={(e) => setCurrentLevel(e.target.value)}
                    className="w-full h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-indigo-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Target Level</label>
                  <input
                    type="text"
                    value={targetLevel}
                    onChange={(e) => setTargetLevel(e.target.value)}
                    className="w-full h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-indigo-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Recommended Action</label>
                <textarea
                  required
                  rows={2}
                  value={recommendedAction}
                  onChange={(e) => setRecommendedAction(e.target.value)}
                  placeholder="e.g. Lead system architecture review and complete cloud certification..."
                  className="w-full rounded-lg border border-slate-800 bg-slate-950 p-2.5 text-xs text-white focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-500 shadow-md shadow-indigo-600/30"
                >
                  Create Plan
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
