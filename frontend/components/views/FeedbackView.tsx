'use client';

import React, { useState } from 'react';
import { MessageSquareQuote, Plus, Star, ShieldCheck, AlertCircle, User, Compass } from 'lucide-react';
import { Feedback, Employee, Competency, ReviewCycle } from '../../types';
import { api } from '../../services/api';

interface FeedbackViewProps {
  feedbacks: Feedback[];
  employees: Employee[];
  competencies: Competency[];
  cycles: ReviewCycle[];
  onRefresh: () => void;
}

export const FeedbackView: React.FC<FeedbackViewProps> = ({
  feedbacks,
  employees,
  competencies,
  cycles,
  onRefresh
}) => {
  const [showModal, setShowModal] = useState(false);
  const [subjectId, setSubjectId] = useState('');
  const [cycleId, setCycleId] = useState('CYCLE-2026-H1');
  const [feedbackType, setFeedbackType] = useState('SELF');
  const [competencyId, setCompetencyId] = useState('COMP-TECH-01');
  const [rating, setRating] = useState<number>(4.0);
  const [comments, setComments] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    try {
      const fbId = `FB-${Math.floor(100000 + Math.random() * 900000)}`;
      await api.submitFeedback({
        feedback_id: fbId,
        subject_employee_id: subjectId,
        review_cycle_id: cycleId,
        feedback_type: feedbackType,
        competency_id: competencyId,
        rating: Number(rating),
        comments: comments
      });
      setShowModal(false);
      onRefresh();
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to submit feedback');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">360° Multi-Source Feedback</h1>
          <p className="text-xs text-slate-400">
            Validated relationship feedback: Self, Direct Manager, and Peer perspectives.
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
          <span>Submit Feedback</span>
        </button>
      </div>

      {/* Feedbacks Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {feedbacks.slice(0, 36).map((fb) => (
          <div
            key={fb.feedback_id}
            className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 space-y-3 hover:border-slate-700 transition"
          >
            <div className="flex items-center justify-between">
              <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold border ${
                fb.feedback_type === 'SELF' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                fb.feedback_type === 'MANAGER' ? 'bg-purple-500/10 text-purple-400 border-purple-500/20' :
                'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
              }`}>
                {fb.feedback_type}
              </span>
              <div className="flex items-center gap-1 text-amber-400 font-bold text-xs">
                <Star className="h-3.5 w-3.5 fill-amber-400" />
                <span>{Number(fb.rating).toFixed(1)} / 5.0</span>
              </div>
            </div>

            <div>
              <p className="text-xs font-semibold text-white">Subject: <span className="font-mono text-indigo-400">{fb.subject_employee_id}</span></p>
              <p className="text-[11px] text-slate-400">Reviewer: <span className="font-mono text-slate-300">{fb.reviewer_employee_id}</span> • {fb.submission_date}</p>
            </div>

            <div className="rounded-lg bg-slate-950/60 p-3 border border-slate-800/60 text-xs text-slate-300">
              <span className="font-mono text-[10px] text-indigo-400 block mb-1">
                Competency: {fb.competency_id}
              </span>
              <p className="italic leading-relaxed text-slate-300">"{fb.comments}"</p>
            </div>
          </div>
        ))}
      </div>

      {/* Submit Feedback Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white">Submit 360° Competency Feedback</h3>
            <p className="text-xs text-slate-400 mt-1">
              Validates reviewer eligibility before recording feedback.
            </p>

            {errorMsg && (
              <div className="mt-3 rounded-lg border border-rose-500/30 bg-rose-950/40 p-2.5 text-xs text-rose-300">
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleSubmit} className="mt-4 space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Subject Employee</label>
                <select
                  required
                  value={subjectId}
                  onChange={(e) => setSubjectId(e.target.value)}
                  className="w-full h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-indigo-500 focus:outline-none"
                >
                  <option value="">Select Employee...</option>
                  {employees.map(e => (
                    <option key={e.employee_id} value={e.employee_id}>
                      {e.full_name} ({e.employee_id} - {e.department})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Feedback Type</label>
                  <select
                    value={feedbackType}
                    onChange={(e) => setFeedbackType(e.target.value)}
                    className="w-full h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-indigo-500 focus:outline-none"
                  >
                    <option value="SELF">SELF</option>
                    <option value="MANAGER">MANAGER</option>
                    <option value="PEER">PEER</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Rating (1.0 to 5.0)</label>
                  <input
                    type="number"
                    step="0.1"
                    min="1.0"
                    max="5.0"
                    value={rating}
                    onChange={(e) => setRating(Number(e.target.value))}
                    className="w-full h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-indigo-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Competency Rubric</label>
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

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Detailed Qualitative Evaluation</label>
                <textarea
                  required
                  rows={3}
                  placeholder="Provide concrete behavioral observations and delivery impact..."
                  value={comments}
                  onChange={(e) => setComments(e.target.value)}
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
                  Submit Evaluation
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
