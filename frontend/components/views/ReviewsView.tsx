'use client';

import React, { useState } from 'react';
import { Award, CheckCircle2, RotateCcw, XCircle, ChevronRight, Calculator, FileText } from 'lucide-react';
import { Review, ReviewCycle } from '../../types';
import { api } from '../../services/api';

interface ReviewsViewProps {
  reviews: Review[];
  cycles: ReviewCycle[];
  onRefresh: () => void;
}

export const ReviewsView: React.FC<ReviewsViewProps> = ({ reviews, cycles, onRefresh }) => {
  const [selectedCycle, setSelectedCycle] = useState('ALL');
  const [transitioningId, setTransitioningId] = useState<string | null>(null);

  const handleTransition = async (reviewId: string, targetStage: string) => {
    setTransitioningId(reviewId);
    try {
      await api.transitionReview(reviewId, targetStage, `Transitioned stage to ${targetStage}`);
      onRefresh();
    } catch (e: any) {
      alert('Error updating review stage: ' + e.message);
    } finally {
      setTransitioningId(null);
    }
  };

  const filtered = reviews.filter(r => selectedCycle === 'ALL' || r.review_cycle_id === selectedCycle);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Performance Review Appraisals</h1>
          <p className="text-xs text-slate-400">
            Transparent scoring model: Goal Achievement (50%) + Competency (30%) + Feedback (20%).
          </p>
        </div>

        <select
          value={selectedCycle}
          onChange={(e) => setSelectedCycle(e.target.value)}
          className="h-9 rounded-lg border border-slate-800 bg-slate-900 px-3 text-xs text-slate-300 focus:border-indigo-500 focus:outline-none"
        >
          <option value="ALL">All Review Cycles</option>
          {cycles.map(c => (
            <option key={c.cycle_id} value={c.cycle_id}>
              {c.cycle_name} ({c.stage})
            </option>
          ))}
        </select>
      </div>

      {/* Reviews Table */}
      <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/60 shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-800 bg-slate-950/60 text-slate-400">
              <tr>
                <th className="py-3 px-4 font-semibold">Review ID</th>
                <th className="py-3 px-4 font-semibold">Employee ID</th>
                <th className="py-3 px-4 font-semibold">Cycle</th>
                <th className="py-3 px-4 font-semibold text-center">Goal Score (50%)</th>
                <th className="py-3 px-4 font-semibold text-center">Comp Score (30%)</th>
                <th className="py-3 px-4 font-semibold text-center">Feedback (20%)</th>
                <th className="py-3 px-4 font-semibold text-center">Final Score</th>
                <th className="py-3 px-4 font-semibold">Rating Category</th>
                <th className="py-3 px-4 font-semibold">Stage</th>
                <th className="py-3 px-4 font-semibold text-right">Workflow Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.slice(0, 40).map((r) => (
                <tr key={r.review_id} className="hover:bg-slate-800/40 transition">
                  <td className="py-3 px-4 font-mono font-medium text-indigo-400">{r.review_id}</td>
                  <td className="py-3 px-4 font-mono font-medium text-white">{r.employee_id}</td>
                  <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">{r.review_cycle_id}</td>
                  <td className="py-3 px-4 text-center font-semibold text-cyan-400">{r.goal_score}%</td>
                  <td className="py-3 px-4 text-center font-semibold text-purple-400">{r.competency_score}%</td>
                  <td className="py-3 px-4 text-center font-semibold text-emerald-400">{r.feedback_score}%</td>
                  <td className="py-3 px-4 text-center">
                    <span className="font-bold text-sm text-white bg-slate-800 px-2 py-0.5 rounded">
                      {r.final_score}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-bold border ${
                      r.rating_category === 'OUTSTANDING' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                      r.rating_category === 'EXCEEDS_EXPECTATIONS' ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20' :
                      r.rating_category === 'MEETS_EXPECTATIONS' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                      'bg-rose-500/10 text-rose-400 border-rose-500/20'
                    }`}>
                      {r.rating_category}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="rounded bg-slate-800 px-2 py-0.5 text-[11px] font-medium text-slate-300">
                      {r.stage}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      {r.stage === 'DRAFT' && (
                        <button
                          disabled={transitioningId === r.review_id}
                          onClick={() => handleTransition(r.review_id, 'SELF_REVIEW_PENDING')}
                          className="rounded bg-indigo-600 px-2.5 py-1 text-[11px] font-medium text-white hover:bg-indigo-500 transition"
                        >
                          Initiate Self
                        </button>
                      )}
                      {r.stage === 'SELF_REVIEW_PENDING' && (
                        <button
                          disabled={transitioningId === r.review_id}
                          onClick={() => handleTransition(r.review_id, 'MANAGER_REVIEW_PENDING')}
                          className="rounded bg-purple-600 px-2.5 py-1 text-[11px] font-medium text-white hover:bg-purple-500 transition"
                        >
                          Submit to Mgr
                        </button>
                      )}
                      {r.stage === 'MANAGER_REVIEW_PENDING' && (
                        <>
                          <button
                            disabled={transitioningId === r.review_id}
                            onClick={() => handleTransition(r.review_id, 'HR_REVIEW_PENDING')}
                            className="rounded bg-emerald-600 px-2.5 py-1 text-[11px] font-medium text-white hover:bg-emerald-500 transition"
                          >
                            Mgr Approve
                          </button>
                          <button
                            disabled={transitioningId === r.review_id}
                            onClick={() => handleTransition(r.review_id, 'RETURNED_FOR_REVISION')}
                            className="rounded bg-slate-800 px-2 py-1 text-[11px] text-slate-400 hover:text-white"
                          >
                            Return
                          </button>
                        </>
                      )}
                      {r.stage === 'HR_REVIEW_PENDING' && (
                        <button
                          disabled={transitioningId === r.review_id}
                          onClick={() => handleTransition(r.review_id, 'APPROVED')}
                          className="rounded bg-emerald-600 px-2.5 py-1 text-[11px] font-semibold text-white hover:bg-emerald-500 transition"
                        >
                          HR Calibrate & Approve
                        </button>
                      )}
                      {r.stage === 'APPROVED' && (
                        <button
                          disabled={transitioningId === r.review_id}
                          onClick={() => handleTransition(r.review_id, 'COMPLETED')}
                          className="rounded bg-blue-600 px-2.5 py-1 text-[11px] font-semibold text-white hover:bg-blue-500 transition"
                        >
                          Finalize
                        </button>
                      )}
                      {r.stage === 'COMPLETED' && (
                        <span className="text-emerald-400 font-semibold text-[11px] flex items-center gap-1">
                          <CheckCircle2 className="h-3.5 w-3.5" />
                          <span>Finalized</span>
                        </span>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
