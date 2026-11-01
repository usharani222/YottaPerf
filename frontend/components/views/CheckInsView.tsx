'use client';

import React, { useState } from 'react';
import { CalendarCheck, Plus, Link as LinkIcon, CheckCircle2, AlertCircle, FileText, ExternalLink } from 'lucide-react';
import { CheckIn, Goal, Employee } from '../../types';
import { api } from '../../services/api';

interface CheckInsViewProps {
  checkIns: CheckIn[];
  goals: Goal[];
  employees: Employee[];
  onRefresh: () => void;
}

export const CheckInsView: React.FC<CheckInsViewProps> = ({ checkIns, goals, employees, onRefresh }) => {
  const [showModal, setShowModal] = useState(false);
  const [goalId, setGoalId] = useState('');
  const [employeeComments, setEmployeeComments] = useState('');
  const [managerComments, setManagerComments] = useState('');
  const [progressUpdate, setProgressUpdate] = useState<number>(50);
  const [blockers, setBlockers] = useState('');
  const [nextSteps, setNextSteps] = useState('');
  const [evidenceUrl, setEvidenceUrl] = useState('');
  const [evidenceType, setEvidenceType] = useState('CODE_PR');
  const [evidenceDesc, setEvidenceDesc] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    try {
      const selectedGoal = goals.find(g => g.goal_id === goalId);
      if (!selectedGoal) throw new Error('Goal not selected');

      const chkId = `CHK-${Math.floor(100000 + Math.random() * 900000)}`;
      await api.submitCheckIn({
        check_in_id: chkId,
        employee_id: selectedGoal.employee_id,
        goal_id: goalId,
        review_cycle_id: selectedGoal.review_cycle_id,
        check_in_date: new Date().toISOString().split('T')[0],
        progress_update: Number(progressUpdate),
        employee_comments: employeeComments,
        manager_comments: managerComments || undefined,
        blockers: blockers || undefined,
        next_steps: nextSteps || undefined,
        evidence_reference_url: evidenceUrl || undefined,
        evidence_type: evidenceType,
        evidence_description: evidenceDesc || undefined
      });
      setShowModal(false);
      onRefresh();
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to submit check-in');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Periodic Employee Check-ins</h1>
          <p className="text-xs text-slate-400">
            Cadence check-ins, sprint milestones, blocker escalation, and evidentiary tracking.
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
          <span>Record Check-in</span>
        </button>
      </div>

      {/* Check-ins Timeline */}
      <div className="space-y-4">
        {checkIns.slice(0, 30).map((chk) => (
          <div
            key={chk.check_in_id}
            className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 space-y-3 hover:border-slate-700 transition"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-indigo-400">{chk.check_in_id}</span>
                <span className="text-xs text-slate-400">• Goal:</span>
                <span className="font-mono text-xs text-slate-300 font-semibold">{chk.goal_id}</span>
                <span className="text-xs text-slate-400">• Owner:</span>
                <span className="font-mono text-xs text-slate-300">{chk.employee_id}</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-slate-400">{chk.check_in_date}</span>
                <span className="rounded-full bg-indigo-500/10 px-2.5 py-0.5 text-xs font-bold text-indigo-400 border border-indigo-500/20">
                  {chk.progress_update}% Progress
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div>
                <span className="font-semibold text-slate-400 uppercase tracking-wider text-[10px]">
                  Employee Commentary
                </span>
                <p className="mt-1 text-slate-300 leading-relaxed bg-slate-950/40 p-2.5 rounded-lg border border-slate-800/40">
                  {chk.employee_comments}
                </p>
              </div>

              <div>
                <span className="font-semibold text-slate-400 uppercase tracking-wider text-[10px]">
                  Manager Guidance
                </span>
                <p className="mt-1 text-slate-300 leading-relaxed bg-slate-950/40 p-2.5 rounded-lg border border-slate-800/40">
                  {chk.manager_comments || <span className="text-slate-500 italic">No manager feedback recorded yet</span>}
                </p>
              </div>
            </div>

            {(chk.blockers || chk.next_steps) && (
              <div className="flex flex-wrap gap-4 text-xs pt-2">
                {chk.blockers && chk.blockers !== 'None' && (
                  <div className="flex items-center gap-1.5 text-rose-400">
                    <AlertCircle className="h-3.5 w-3.5" />
                    <span>Blocker: {chk.blockers}</span>
                  </div>
                )}
                {chk.next_steps && (
                  <div className="flex items-center gap-1.5 text-emerald-400">
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    <span>Next: {chk.next_steps}</span>
                  </div>
                )}
              </div>
            )}

            {/* Evidences */}
            {chk.evidences && chk.evidences.length > 0 && (
              <div className="pt-2 border-t border-slate-800/60">
                <div className="flex items-center gap-2 text-[11px] font-semibold text-slate-400 mb-2">
                  <LinkIcon className="h-3.5 w-3.5 text-indigo-400" />
                  <span>Substantiating Evidences ({chk.evidences.length})</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {chk.evidences.map((ev) => (
                    <a
                      key={ev.evidence_id}
                      href={ev.reference_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-950 px-2.5 py-1 text-[11px] text-slate-300 hover:border-indigo-500/50 hover:text-white transition"
                    >
                      <span className="font-mono text-indigo-400">{ev.evidence_type}:</span>
                      <span className="truncate max-w-xs">{ev.description}</span>
                      <ExternalLink className="h-3 w-3 text-slate-500" />
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Record Check-in Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white">Record Progress Check-in</h3>
            <p className="text-xs text-slate-400 mt-1">Submit periodic milestone commentary and attach verifiable evidence.</p>

            {errorMsg && (
              <div className="mt-3 rounded-lg border border-rose-500/30 bg-rose-950/40 p-2.5 text-xs text-rose-300">
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleSubmit} className="mt-4 space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Target Goal</label>
                <select
                  required
                  value={goalId}
                  onChange={(e) => setGoalId(e.target.value)}
                  className="w-full h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-indigo-500 focus:outline-none"
                >
                  <option value="">Select Goal...</option>
                  {goals.map(g => (
                    <option key={g.goal_id} value={g.goal_id}>
                      {g.title} ({g.goal_id} - Owner: {g.employee_id})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Reported Progress %</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={progressUpdate}
                  onChange={(e) => setProgressUpdate(Number(e.target.value))}
                  className="w-full h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Employee Commentary</label>
                <textarea
                  required
                  rows={2}
                  placeholder="Detail sprint progress, completed sub-tasks, and key milestones hit..."
                  value={employeeComments}
                  onChange={(e) => setEmployeeComments(e.target.value)}
                  className="w-full rounded-lg border border-slate-800 bg-slate-950 p-2.5 text-xs text-white focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Blockers (optional)</label>
                  <input
                    type="text"
                    placeholder="None"
                    value={blockers}
                    onChange={(e) => setBlockers(e.target.value)}
                    className="w-full h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-indigo-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Next Steps</label>
                  <input
                    type="text"
                    placeholder="e.g. Merge staging build"
                    value={nextSteps}
                    onChange={(e) => setNextSteps(e.target.value)}
                    className="w-full h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-indigo-500 focus:outline-none"
                  />
                </div>
              </div>

              {/* Evidence Attachment Section */}
              <div className="pt-2 border-t border-slate-800 space-y-2">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                  Attach Verifiable Evidence
                </span>
                <div className="grid grid-cols-3 gap-2">
                  <select
                    value={evidenceType}
                    onChange={(e) => setEvidenceType(e.target.value)}
                    className="h-9 rounded-lg border border-slate-800 bg-slate-950 px-2 text-xs text-white focus:border-indigo-500 focus:outline-none"
                  >
                    <option value="CODE_PR">CODE_PR</option>
                    <option value="METRIC_DASHBOARD">METRIC_DASHBOARD</option>
                    <option value="CUSTOMER_EMAIL">CUSTOMER_EMAIL</option>
                    <option value="CERTIFICATION">CERTIFICATION</option>
                    <option value="DOCUMENT">DOCUMENT</option>
                  </select>
                  <input
                    type="url"
                    placeholder="https://github.com/... or URL"
                    value={evidenceUrl}
                    onChange={(e) => setEvidenceUrl(e.target.value)}
                    className="col-span-2 h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-indigo-500 focus:outline-none"
                  />
                </div>
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
                  Submit Check-in
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
