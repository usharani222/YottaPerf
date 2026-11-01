'use client';

import React, { useState } from 'react';
import {
  ShieldAlert, AlertTriangle, CheckCircle, Search, Filter, Wrench,
  ExternalLink, Lock, ShieldCheck, Clock, FileText, CheckCircle2,
  AlertOctagon, Info
} from 'lucide-react';
import { Anomaly } from '../../types';
import { api } from '../../services/api';

interface AnomalyCenterViewProps {
  anomalies: Anomaly[];
  onRefresh: () => void;
}

export const AnomalyCenterView: React.FC<AnomalyCenterViewProps> = ({ anomalies, onRefresh }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('ALL');
  const [selectedSeverity, setSelectedSeverity] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [activeAnomaly, setActiveAnomaly] = useState<Anomaly | null>(null);
  const [resolveNotes, setResolveNotes] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const issueTypes = ['ALL', ...Array.from(new Set(anomalies.map(a => a.issue_type)))];

  const filtered = anomalies.filter(a => {
    const matchSearch =
      a.anomaly_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      a.affected_record_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      a.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      a.issue_type.toLowerCase().includes(searchTerm.toLowerCase());

    const matchType = selectedType === 'ALL' || a.issue_type === selectedType;
    const matchSev = selectedSeverity === 'ALL' || a.severity === selectedSeverity;
    const matchStatus = selectedStatus === 'ALL' || a.detection_status === selectedStatus;

    return matchSearch && matchType && matchSev && matchStatus;
  });

  const handleResolve = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeAnomaly) return;
    setIsSubmitting(true);
    try {
      await api.resolveAnomaly(activeAnomaly.anomaly_id, resolveNotes);
      setShowModal(false);
      setResolveNotes('');
      onRefresh();
    } catch (e: any) {
      alert('Error resolving anomaly: ' + e.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const openCount = anomalies.filter(a => a.detection_status === 'OPEN').length;
  const criticalCount = anomalies.filter(a => a.severity === 'CRITICAL' && a.detection_status === 'OPEN').length;
  const resolvedCount = anomalies.filter(a => a.detection_status === 'RESOLVED').length;

  return (
    <div className="space-y-6">
      {/* Header and Telemetry Stats Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <ShieldAlert className="h-6 w-6 text-rose-400" />
            Exception & Anomaly Resolution Center
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time heuristic integrity scanner: Detects structural discrepancies, duplicate calculations, orphan nodes, and isolated test anomalies.
          </p>
        </div>

        {/* Metric Badges */}
        <div className="flex items-center gap-2.5">
          <div className="flex items-center gap-1.5 rounded-xl border border-rose-500/30 bg-rose-500/10 px-3 py-1.5 text-xs font-semibold text-rose-400">
            <AlertOctagon className="h-4 w-4" />
            <span>{criticalCount} Critical Open</span>
          </div>
          <div className="flex items-center gap-1.5 rounded-xl border border-amber-500/30 bg-amber-500/10 px-3 py-1.5 text-xs font-semibold text-amber-400">
            <AlertTriangle className="h-4 w-4" />
            <span>{openCount} Total Open</span>
          </div>
          <div className="flex items-center gap-1.5 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-3 py-1.5 text-xs font-semibold text-emerald-400">
            <CheckCircle2 className="h-4 w-4" />
            <span>{resolvedCount} Remediated</span>
          </div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="rounded-2xl border border-white/[0.08] bg-slate-900/40 p-4 backdrop-blur-xl flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3">
          {/* Search Box */}
          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search anomaly, ID, record..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="h-8.5 w-60 rounded-xl border border-white/[0.08] bg-slate-950/80 pl-8 pr-3 text-xs text-white placeholder-slate-500 focus:border-rose-500/50 focus:outline-none"
            />
          </div>

          {/* Status Filter */}
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="h-8.5 rounded-xl border border-white/[0.08] bg-slate-950 px-3 text-xs text-slate-200 focus:border-rose-500 focus:outline-none"
          >
            <option value="ALL">All Statuses</option>
            <option value="OPEN">OPEN Only</option>
            <option value="RESOLVED">RESOLVED Only</option>
          </select>

          {/* Severity Filter */}
          <select
            value={selectedSeverity}
            onChange={(e) => setSelectedSeverity(e.target.value)}
            className="h-8.5 rounded-xl border border-white/[0.08] bg-slate-950 px-3 text-xs text-slate-200 focus:border-rose-500 focus:outline-none"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">CRITICAL Tier</option>
            <option value="HIGH">HIGH Tier</option>
            <option value="MEDIUM">MEDIUM Tier</option>
            <option value="LOW">LOW Tier</option>
          </select>

          {/* Issue Type Filter */}
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="h-8.5 rounded-xl border border-white/[0.08] bg-slate-950 px-3 text-xs text-slate-200 focus:border-rose-500 focus:outline-none max-w-xs truncate"
          >
            {issueTypes.map(t => (
              <option key={t} value={t}>
                {t === 'ALL' ? 'All Issue Types' : t}
              </option>
            ))}
          </select>
        </div>

        <span className="text-xs text-slate-400 font-mono">
          Showing {filtered.length} of {anomalies.length} items
        </span>
      </div>

      {/* Anomalies Table */}
      <div className="overflow-hidden rounded-2xl border border-white/[0.08] bg-slate-900/40 backdrop-blur-2xl shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-white/[0.08] bg-slate-950/80 text-slate-400">
              <tr>
                <th className="py-3.5 px-4 font-semibold">Anomaly ID</th>
                <th className="py-3.5 px-4 font-semibold">Severity</th>
                <th className="py-3.5 px-4 font-semibold">Classification & Target</th>
                <th className="py-3.5 px-4 font-semibold">Diagnostic Explanation</th>
                <th className="py-3.5 px-4 font-semibold">Ground-Truth Label</th>
                <th className="py-3.5 px-4 font-semibold">Expected Resolution</th>
                <th className="py-3.5 px-4 font-semibold text-center">Status</th>
                <th className="py-3.5 px-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.05] text-slate-300">
              {filtered.map((a) => {
                const isRestricted = a.ground_truth_label === 'RESTRICTED_SECURITY_ROLE';
                return (
                  <tr key={a.anomaly_id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-medium text-rose-400 whitespace-nowrap">
                      {a.anomaly_id}
                    </td>

                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-[10px] font-bold border ${
                        a.severity === 'CRITICAL' ? 'bg-red-500/10 text-red-400 border-red-500/30' :
                        a.severity === 'HIGH' ? 'bg-orange-500/10 text-orange-400 border-orange-500/30' :
                        a.severity === 'MEDIUM' ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' :
                        'bg-slate-800 text-slate-300 border border-white/[0.05]'
                      }`}>
                        {a.severity}
                      </span>
                    </td>

                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-white">{a.issue_type}</div>
                      <div className="mt-0.5">
                        <span className="rounded bg-slate-950/90 px-1.5 py-0.5 border border-white/[0.08] text-[10px] font-mono text-cyan-300">
                          {a.affected_entity}:{a.affected_record_id}
                        </span>
                      </div>
                    </td>

                    <td className="py-3.5 px-4 max-w-xs text-slate-300" title={a.description}>
                      <p className="line-clamp-2 leading-relaxed">{a.description}</p>
                    </td>

                    {/* Ground-Truth Isolation Protection */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      {isRestricted ? (
                        <span
                          title="Ground truth diagnostic label is restricted to ADMIN roles to protect evaluation isolation"
                          className="inline-flex items-center gap-1 rounded-full bg-slate-800/80 px-2 py-0.5 text-[10px] font-semibold text-slate-400 border border-white/[0.05]"
                        >
                          <Lock className="h-3 w-3 text-slate-500" />
                          <span>Restricted Role</span>
                        </span>
                      ) : (
                        <span
                          title="Verified injection ground truth"
                          className="inline-flex items-center gap-1 rounded-full bg-purple-500/10 px-2 py-0.5 text-[10px] font-semibold text-purple-300 border border-purple-500/20 font-mono"
                        >
                          <ShieldCheck className="h-3 w-3 text-purple-400" />
                          <span>{a.ground_truth_label}</span>
                        </span>
                      )}
                    </td>

                    <td className="py-3.5 px-4 max-w-xs text-slate-400" title={a.expected_resolution}>
                      <p className="line-clamp-2 text-[11px] leading-relaxed">{a.expected_resolution}</p>
                    </td>

                    <td className="py-3.5 px-4 text-center whitespace-nowrap">
                      <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-[10px] font-bold border ${
                        a.detection_status === 'RESOLVED'
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                          : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                      }`}>
                        {a.detection_status}
                      </span>
                    </td>

                    <td className="py-3.5 px-4 text-right whitespace-nowrap">
                      {a.detection_status !== 'RESOLVED' ? (
                        <button
                          onClick={() => {
                            setActiveAnomaly(a);
                            setResolveNotes(a.expected_resolution || 'Remediated as per organizational governance policy.');
                            setShowModal(true);
                          }}
                          className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-2.5 py-1 text-[11px] font-semibold text-white hover:bg-emerald-500 transition shadow-sm"
                        >
                          <Wrench className="h-3 w-3" />
                          <span>Remediate</span>
                        </button>
                      ) : (
                        <span className="text-[11px] text-emerald-400 flex items-center justify-end gap-1 font-medium">
                          <CheckCircle className="h-3.5 w-3.5" />
                          <span>Resolved</span>
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Remediate Anomaly Exception Modal */}
      {showModal && activeAnomaly && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg rounded-2xl border border-white/[0.08] bg-slate-950 p-6 shadow-2xl animate-in zoom-in-95 duration-200">
            <div className="flex items-start justify-between pb-3 border-b border-white/[0.08]">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-semibold text-rose-400">{activeAnomaly.anomaly_id}</span>
                  <span className="text-xs font-bold text-white">• {activeAnomaly.issue_type}</span>
                </div>
                <h3 className="text-base font-bold text-white mt-1">Remediate Structural Anomaly</h3>
                <p className="text-xs text-slate-400">Updates backend state and creates an immutable audit trail entry.</p>
              </div>

              <button
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="mt-4 p-3.5 rounded-xl border border-white/[0.06] bg-slate-900/80 text-xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Affected Entity:</span>
                <span className="font-mono text-cyan-300 font-semibold">{activeAnomaly.affected_entity}:{activeAnomaly.affected_record_id}</span>
              </div>
              <div>
                <span className="text-slate-400 block mb-0.5">Diagnostic Signature:</span>
                <p className="text-slate-200 leading-relaxed">{activeAnomaly.description}</p>
              </div>
              <div>
                <span className="text-slate-400 block mb-0.5">Recommended Resolution:</span>
                <p className="text-emerald-300/90 leading-relaxed">{activeAnomaly.expected_resolution}</p>
              </div>
            </div>

            <form onSubmit={handleResolve} className="mt-4 space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Remediation Audit Notes & Justification
                </label>
                <textarea
                  required
                  rows={3}
                  value={resolveNotes}
                  onChange={(e) => setResolveNotes(e.target.value)}
                  placeholder="Describe resolution steps taken..."
                  className="w-full rounded-xl border border-white/[0.08] bg-slate-900 p-2.5 text-xs text-white focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-white/[0.08]">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 px-4 py-2 text-xs font-semibold text-white hover:from-emerald-400 hover:to-teal-500 shadow-md shadow-emerald-500/20 transition flex items-center gap-1.5"
                >
                  <CheckCircle2 className="h-4 w-4" />
                  <span>{isSubmitting ? 'Recording...' : 'Commit Remediation'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
