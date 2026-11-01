'use client';

import React, { useState } from 'react';
import {
  Search, Filter, User, Mail, Briefcase, Calendar, ChevronRight,
  X, Target, Award, Compass, GraduationCap, Clock, CheckCircle2,
  AlertTriangle, ExternalLink, ShieldCheck, ChevronDown, Sparkles,
  Building, Layers, UserCheck, FileText, CheckCircle
} from 'lucide-react';
import { Employee, EmployeePerformanceProfile } from '../../types';
import { api } from '../../services/api';

interface EmployeesViewProps {
  employees: Employee[];
  loading: boolean;
  onSelectEmployee?: (emp: Employee) => void;
}

export const EmployeesView: React.FC<EmployeesViewProps> = ({ employees, loading, onSelectEmployee }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDept, setSelectedDept] = useState('ALL');
  const [selectedEmp, setSelectedEmp] = useState<Employee | null>(null);
  const [profileData, setProfileData] = useState<EmployeePerformanceProfile | null>(null);
  const [profileLoading, setProfileLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'goals' | 'checkins' | 'feedback' | 'reviews' | 'development' | 'history'>('goals');

  const departments = ['ALL', ...Array.from(new Set(employees.map(e => e.department)))];

  const filtered = employees.filter(e => {
    const matchesSearch =
      e.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.employee_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.job_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.email.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesDept = selectedDept === 'ALL' || e.department === selectedDept;
    return matchesSearch && matchesDept;
  });

  const handleOpenProfile = async (emp: Employee) => {
    setSelectedEmp(emp);
    setProfileLoading(true);
    setProfileData(null);
    setActiveTab('goals');
    try {
      const data = await api.getEmployeePerformanceProfile(emp.employee_id);
      setProfileData(data);
    } catch (err: any) {
      console.error('Error fetching employee profile:', err);
    } finally {
      setProfileLoading(false);
    }
  };

  const handleCloseProfile = () => {
    setSelectedEmp(null);
    setProfileData(null);
  };

  return (
    <div className="space-y-6">
      {/* Title & Search Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <User className="h-6 w-6 text-emerald-400" />
            Organizational Employee Directory
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Browse personnel profiles, verify reporting managers, and inspect real-time 360° performance dossiers.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Search Input */}
          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
            <input
              type="text"
              placeholder="Search name, ID, title, email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="h-9 w-64 rounded-xl border border-white/[0.08] bg-slate-900/80 pl-9 pr-3 text-xs text-white placeholder-slate-500 focus:border-emerald-500/50 focus:outline-none"
            />
          </div>

          {/* Department Filter */}
          <select
            value={selectedDept}
            onChange={(e) => setSelectedDept(e.target.value)}
            className="h-9 rounded-xl border border-white/[0.08] bg-slate-900/80 px-3 text-xs text-slate-300 focus:border-emerald-500/50 focus:outline-none"
          >
            {departments.map((d) => (
              <option key={d} value={d}>
                {d === 'ALL' ? 'All Departments' : d}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Employee List Table */}
      <div className="overflow-hidden rounded-2xl border border-white/[0.08] bg-slate-900/40 backdrop-blur-2xl shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-white/[0.08] bg-slate-950/80 text-slate-400">
              <tr>
                <th className="py-3.5 px-4 font-semibold">Employee ID</th>
                <th className="py-3.5 px-4 font-semibold">Full Name</th>
                <th className="py-3.5 px-4 font-semibold">Department</th>
                <th className="py-3.5 px-4 font-semibold">Title & Level</th>
                <th className="py-3.5 px-4 font-semibold">Reporting Manager</th>
                <th className="py-3.5 px-4 font-semibold">Hire Date</th>
                <th className="py-3.5 px-4 font-semibold text-center">Status</th>
                <th className="py-3.5 px-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.05] text-slate-300">
              {filtered.map((emp) => (
                <tr
                  key={emp.employee_id}
                  onClick={() => handleOpenProfile(emp)}
                  className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                >
                  <td className="py-3.5 px-4 font-mono font-medium text-emerald-400">{emp.employee_id}</td>
                  <td className="py-3.5 px-4 font-semibold text-white flex items-center gap-2">
                    <div className="h-6 w-6 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center text-[10px] font-bold">
                      {emp.first_name[0]}{emp.last_name[0]}
                    </div>
                    <span>{emp.full_name}</span>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="inline-flex items-center rounded-md bg-slate-800/80 px-2 py-0.5 text-[11px] font-medium text-slate-300 border border-white/[0.05]">
                      {emp.department}
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-2">
                      <span className="text-slate-200">{emp.job_title}</span>
                      <span className="rounded bg-indigo-500/10 px-1.5 py-0.2 text-[10px] font-semibold text-indigo-400 border border-indigo-500/20 font-mono">
                        {emp.job_level}
                      </span>
                    </div>
                  </td>
                  <td className="py-3.5 px-4 font-mono text-slate-400">
                    {emp.manager_id || <span className="text-emerald-400 font-sans font-semibold">Chief Executive</span>}
                  </td>
                  <td className="py-3.5 px-4 text-slate-400">{emp.hire_date}</td>
                  <td className="py-3.5 px-4 text-center">
                    <span className="inline-flex items-center rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-[10px] font-semibold text-emerald-400 border border-emerald-500/20">
                      Active
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleOpenProfile(emp);
                      }}
                      className="inline-flex items-center gap-1 rounded-lg border border-white/[0.08] bg-slate-800/80 px-2.5 py-1 text-[11px] font-medium text-slate-200 hover:text-white hover:border-emerald-500/40 hover:bg-slate-800 transition"
                    >
                      <span>360° Profile</span>
                      <ChevronRight className="h-3 w-3 text-slate-400" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Dedicated Employee 360 Performance Profile Drawer/Modal */}
      {selectedEmp && (
        <div className="fixed inset-0 z-50 flex items-center justify-end bg-black/70 backdrop-blur-sm p-0 sm:p-4">
          <div className="w-full sm:max-w-4xl h-full sm:h-[94vh] rounded-none sm:rounded-2xl border-l sm:border border-white/[0.08] bg-slate-950 flex flex-col shadow-2xl overflow-hidden animate-in slide-in-from-right duration-300">
            {/* Drawer Header */}
            <div className="p-5 border-b border-white/[0.08] bg-slate-900/60 backdrop-blur-xl flex items-start justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className="h-14 w-14 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-teal-500/10 border border-emerald-500/30 flex items-center justify-center text-lg font-bold text-emerald-400 font-mono shadow-lg shadow-emerald-500/10">
                  {selectedEmp.first_name[0]}{selectedEmp.last_name[0]}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-lg font-bold text-white">{selectedEmp.full_name}</h2>
                    <span className="font-mono text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                      {selectedEmp.employee_id}
                    </span>
                    <span className="rounded bg-indigo-500/10 px-1.5 py-0.5 text-[10px] font-semibold text-indigo-400 border border-indigo-500/20 font-mono">
                      {selectedEmp.job_level}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {selectedEmp.job_title} • <span className="text-slate-300 font-medium">{selectedEmp.department}</span> • Joined {selectedEmp.hire_date}
                  </p>
                  <p className="text-[11px] text-slate-500 font-mono mt-0.5">
                    {selectedEmp.email}
                  </p>
                </div>
              </div>

              <button
                onClick={handleCloseProfile}
                className="rounded-xl p-2 text-slate-400 hover:bg-slate-800 hover:text-white transition"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Reporting Relationship Card Bar */}
            <div className="px-5 py-3 border-b border-white/[0.06] bg-slate-900/30 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div className="flex items-center gap-3">
                <UserCheck className="h-4 w-4 text-teal-400 shrink-0" />
                <div>
                  <span className="text-[10px] uppercase text-slate-500 font-bold tracking-wider">Reporting Manager:</span>
                  <p className="font-semibold text-slate-200">
                    {profileData?.manager
                      ? `${profileData.manager.full_name} (${profileData.manager.job_title})`
                      : (selectedEmp.manager_id ? selectedEmp.manager_id : 'Chief Executive Officer (Root Node)')}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3 sm:justify-end">
                <Layers className="h-4 w-4 text-cyan-400 shrink-0" />
                <div>
                  <span className="text-[10px] uppercase text-slate-500 font-bold tracking-wider">Span of Control:</span>
                  <p className="font-semibold text-slate-200">
                    {profileData?.direct_reports_count ?? 0} Direct Reports
                  </p>
                </div>
              </div>
            </div>

            {/* Tab Navigation */}
            <div className="flex items-center gap-1 px-5 border-b border-white/[0.08] bg-slate-900/20 text-xs overflow-x-auto">
              {[
                { id: 'goals', label: `Active Goals (${profileData?.goals?.length ?? 0})`, icon: Target },
                { id: 'checkins', label: `Check-in Timeline (${profileData?.check_ins?.length ?? 0})`, icon: Clock },
                { id: 'feedback', label: `360° Feedback (${profileData?.feedbacks?.length ?? 0})`, icon: Compass },
                { id: 'reviews', label: `Reviews (${profileData?.reviews?.length ?? 0})`, icon: Award },
                { id: 'development', label: `IDPs (${profileData?.development_plans?.length ?? 0})`, icon: GraduationCap },
                { id: 'history', label: `Reporting History (${profileData?.manager_history?.length ?? 0})`, icon: Building },
              ].map(tab => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`flex items-center gap-1.5 py-3 px-3.5 font-semibold transition border-b-2 whitespace-nowrap ${
                      isActive
                        ? 'border-emerald-400 text-emerald-400'
                        : 'border-transparent text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <Icon className="h-3.5 w-3.5" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </div>

            {/* Tab Content Body */}
            <div className="flex-1 overflow-y-auto p-5 space-y-4">
              {profileLoading ? (
                <div className="h-64 flex flex-col items-center justify-center text-slate-400 text-xs gap-2">
                  <div className="h-6 w-6 rounded-full border-2 border-emerald-500 border-t-transparent animate-spin" />
                  <span>Loading complete 360° performance profile...</span>
                </div>
              ) : (
                <>
                  {/* TAB 1: GOALS & KEY RESULTS */}
                  {activeTab === 'goals' && (
                    <div className="space-y-4">
                      {(!profileData?.goals || profileData.goals.length === 0) ? (
                        <div className="p-8 text-center text-xs text-slate-500">No active goals registered for this cycle.</div>
                      ) : (
                        profileData.goals.map(goal => (
                          <div key={goal.goal_id} className="rounded-xl border border-white/[0.08] bg-slate-900/50 p-4 space-y-3">
                            <div className="flex items-start justify-between gap-2">
                              <div>
                                <div className="flex items-center gap-2">
                                  <span className="font-mono text-xs font-semibold text-emerald-400">{goal.goal_id}</span>
                                  <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                                    goal.priority === 'CRITICAL' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                                    goal.priority === 'HIGH' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                                    'bg-slate-800 text-slate-300'
                                  }`}>
                                    {goal.priority}
                                  </span>
                                  <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] font-medium text-slate-400">
                                    {goal.category}
                                  </span>
                                </div>
                                <h4 className="text-sm font-semibold text-white mt-1">{goal.title}</h4>
                                <p className="text-[11px] text-slate-400 mt-0.5">Due: {goal.due_date} • Weight: {goal.weight}</p>
                              </div>

                              <div className="text-right">
                                <span className="font-mono text-sm font-extrabold text-emerald-400">
                                  {goal.calculated_progress}%
                                </span>
                                <div className="text-[10px] text-slate-500 uppercase font-semibold">Progress</div>
                              </div>
                            </div>

                            {/* Progress bar */}
                            <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-300"
                                style={{ width: `${Math.min(100, goal.calculated_progress || 0)}%` }}
                              />
                            </div>

                            {/* Child Key Results */}
                            {goal.key_results && goal.key_results.length > 0 && (
                              <div className="pt-2 border-t border-white/[0.06] space-y-2">
                                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                                  Key Results ({goal.key_results.length})
                                </span>
                                <div className="space-y-1.5">
                                  {goal.key_results.map(kr => (
                                    <div key={kr.key_result_id} className="flex items-center justify-between rounded-lg bg-slate-950/70 p-2.5 border border-white/[0.05] text-xs">
                                      <div>
                                        <p className="font-medium text-slate-200">{kr.metric_name}</p>
                                        <p className="text-[10px] text-slate-400">
                                          Baseline: {kr.baseline_value} → Target: {kr.target_value} {kr.unit} | Direction: {kr.metric_direction}
                                        </p>
                                      </div>
                                      <div className="text-right">
                                        <span className="font-mono font-bold text-cyan-400">{kr.progress_percentage}%</span>
                                        <div className="text-[10px] text-slate-500 font-mono">Current: {kr.current_value}</div>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        ))
                      )}
                    </div>
                  )}

                  {/* TAB 2: CHECK-IN TIMELINE & EVIDENCE */}
                  {activeTab === 'checkins' && (
                    <div className="space-y-3">
                      {(!profileData?.check_ins || profileData.check_ins.length === 0) ? (
                        <div className="p-8 text-center text-xs text-slate-500">No check-in logs submitted yet.</div>
                      ) : (
                        profileData.check_ins.map(ci => (
                          <div key={ci.check_in_id} className="rounded-xl border border-white/[0.08] bg-slate-900/50 p-4 space-y-2.5">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <span className="font-mono text-xs font-semibold text-emerald-400">{ci.check_in_id}</span>
                                <span className="text-[10px] text-slate-400 font-mono">Goal: {ci.goal_id}</span>
                              </div>
                              <span className="text-[11px] text-slate-400 flex items-center gap-1 font-mono">
                                <Clock className="h-3 w-3 text-slate-500" />
                                {ci.check_in_date}
                              </span>
                            </div>

                            <p className="text-xs text-slate-200">
                              <strong className="text-slate-400 font-medium">Comments: </strong>
                              {ci.employee_comments}
                            </p>

                            {ci.manager_comments && (
                              <p className="text-xs text-teal-300/90 bg-teal-950/20 p-2 rounded-lg border border-teal-500/20">
                                <strong className="text-teal-400 font-medium">Manager Feedback: </strong>
                                {ci.manager_comments}
                              </p>
                            )}

                            {/* Attached Evidence */}
                            {ci.evidences && ci.evidences.length > 0 && (
                              <div className="pt-2 border-t border-white/[0.06] space-y-1.5">
                                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                                  Attached Evidence Artifacts ({ci.evidences.length})
                                </span>
                                {ci.evidences.map(ev => (
                                  <div key={ev.evidence_id} className="flex items-center justify-between rounded-lg bg-slate-950/80 p-2 border border-white/[0.05] text-xs">
                                    <div className="flex items-center gap-2">
                                      <FileText className="h-3.5 w-3.5 text-cyan-400" />
                                      <span className="font-medium text-slate-300">{ev.description || ev.evidence_type}</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <span className="rounded bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold text-emerald-400 border border-emerald-500/20">
                                        {ev.verification_status}
                                      </span>
                                      {ev.reference_url && (
                                        <a
                                          href={ev.reference_url}
                                          target="_blank"
                                          rel="noreferrer"
                                          className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 text-[11px]"
                                        >
                                          <ExternalLink className="h-3 w-3" />
                                          <span>Link</span>
                                        </a>
                                      )}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        ))
                      )}
                    </div>
                  )}

                  {/* TAB 3: 360° FEEDBACK */}
                  {activeTab === 'feedback' && (
                    <div className="space-y-3">
                      {(!profileData?.feedbacks || profileData.feedbacks.length === 0) ? (
                        <div className="p-8 text-center text-xs text-slate-500">No 360° feedback records found.</div>
                      ) : (
                        profileData.feedbacks.map(fb => (
                          <div key={fb.feedback_id} className="rounded-xl border border-white/[0.08] bg-slate-900/50 p-4 space-y-2">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold border ${
                                  fb.feedback_type === 'MANAGER' ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20' :
                                  fb.feedback_type === 'PEER' ? 'bg-purple-500/10 text-purple-400 border-purple-500/20' :
                                  'bg-slate-800 text-slate-300 border-white/[0.05]'
                                }`}>
                                  {fb.feedback_type}
                                </span>
                                <span className="text-xs font-semibold text-white">
                                  {fb.competency_name || fb.competency_id}
                                </span>
                                <span className="text-[10px] text-slate-400">({fb.competency_category})</span>
                              </div>
                              <div className="flex items-center gap-1 text-emerald-400 font-bold font-mono text-xs">
                                <span>{fb.rating} / 5.0</span>
                              </div>
                            </div>
                            <p className="text-xs text-slate-300 italic">"{fb.comments}"</p>
                            <p className="text-[10px] text-slate-500 font-mono text-right">
                              Reviewer: {fb.reviewer_employee_id} • Date: {fb.submission_date}
                            </p>
                          </div>
                        ))
                      )}
                    </div>
                  )}

                  {/* TAB 4: REVIEWS */}
                  {activeTab === 'reviews' && (
                    <div className="space-y-3">
                      {(!profileData?.reviews || profileData.reviews.length === 0) ? (
                        <div className="p-8 text-center text-xs text-slate-500">No finalized reviews recorded.</div>
                      ) : (
                        profileData.reviews.map(rev => (
                          <div key={rev.review_id} className="rounded-xl border border-white/[0.08] bg-slate-900/50 p-4 space-y-3">
                            <div className="flex items-center justify-between">
                              <span className="font-mono text-xs font-semibold text-emerald-400">{rev.review_cycle_id}</span>
                              <span className="rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-[10px] font-bold text-emerald-400 border border-emerald-500/20">
                                {rev.stage}
                              </span>
                            </div>
                            <div className="grid grid-cols-4 gap-2 text-center text-xs bg-slate-950/70 p-3 rounded-xl border border-white/[0.05]">
                              <div>
                                <span className="text-[10px] text-slate-500 uppercase font-semibold">Goal Score</span>
                                <p className="font-mono font-bold text-slate-200 mt-0.5">{rev.goal_score}</p>
                              </div>
                              <div>
                                <span className="text-[10px] text-slate-500 uppercase font-semibold">Competency</span>
                                <p className="font-mono font-bold text-slate-200 mt-0.5">{rev.competency_score}</p>
                              </div>
                              <div>
                                <span className="text-[10px] text-slate-500 uppercase font-semibold">Feedback</span>
                                <p className="font-mono font-bold text-slate-200 mt-0.5">{rev.feedback_score}</p>
                              </div>
                              <div>
                                <span className="text-[10px] text-slate-500 uppercase font-semibold">Final Calibrated</span>
                                <p className="font-mono font-extrabold text-emerald-400 mt-0.5">{rev.final_score} ({rev.rating_category})</p>
                              </div>
                            </div>
                            {rev.manager_comments && (
                              <p className="text-xs text-slate-300">
                                <strong className="text-slate-400">Manager Summary: </strong> {rev.manager_comments}
                              </p>
                            )}
                          </div>
                        ))
                      )}
                    </div>
                  )}

                  {/* TAB 5: DEVELOPMENT PLANS */}
                  {activeTab === 'development' && (
                    <div className="space-y-3">
                      {(!profileData?.development_plans || profileData.development_plans.length === 0) ? (
                        <div className="p-8 text-center text-xs text-slate-500">No active development plans registered.</div>
                      ) : (
                        profileData.development_plans.map(dp => (
                          <div key={dp.plan_id} className="rounded-xl border border-white/[0.08] bg-slate-900/50 p-4 space-y-2.5">
                            <div className="flex items-center justify-between">
                              <span className="font-mono text-xs font-semibold text-blue-400">{dp.plan_id}</span>
                              <div className="flex items-center gap-2">
                                <span className="rounded bg-blue-500/10 px-2 py-0.5 text-[10px] font-semibold text-blue-400 border border-blue-500/20">
                                  {dp.approval_status}
                                </span>
                                <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] font-semibold text-slate-300">
                                  {dp.status}
                                </span>
                              </div>
                            </div>
                            <h4 className="text-xs font-semibold text-white">Target Competency: {dp.competency_name || dp.competency_id}</h4>
                            <p className="text-xs text-slate-300">{dp.recommended_action}</p>
                            <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-white/[0.06]">
                              <span>Baseline: {dp.current_level} → Target: {dp.target_level}</span>
                              <span>Target Completion: {dp.target_completion_date}</span>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  )}

                  {/* TAB 6: REPORTING HISTORY */}
                  {activeTab === 'history' && (
                    <div className="space-y-3">
                      {(!profileData?.manager_history || profileData.manager_history.length === 0) ? (
                        <div className="p-8 text-center text-xs text-slate-500">No historical manager transfers on record.</div>
                      ) : (
                        profileData.manager_history.map(mh => (
                          <div key={mh.history_id} className="rounded-xl border border-white/[0.08] bg-slate-900/50 p-4 space-y-1.5 text-xs">
                            <div className="flex items-center justify-between">
                              <span className="font-mono font-semibold text-emerald-400">Manager: {mh.manager_id}</span>
                              <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                                mh.is_current ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-slate-800 text-slate-400'
                              }`}>
                                {mh.is_current ? 'Current Active Assignment' : 'Historical'}
                              </span>
                            </div>
                            <p className="text-slate-300">
                              Duration: <span className="font-mono text-slate-400">{mh.start_date}</span> to <span className="font-mono text-slate-400">{mh.end_date || 'Present'}</span>
                            </p>
                            <p className="text-[11px] text-slate-400">
                              Reason: {mh.transfer_reason || 'Initial seed assignment'}
                            </p>
                          </div>
                        ))
                      )}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
