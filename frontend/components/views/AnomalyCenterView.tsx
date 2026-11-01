'use client';

import React, { useState } from 'react';
import { ShieldAlert, AlertTriangle, CheckCircle, Search, Filter, Wrench, ExternalLink } from 'lucide-react';
import { Anomaly } from '../../types';
import { api } from '../../services/api';

interface AnomalyCenterViewProps {
  anomalies: Anomaly[];
  onRefresh: () => void;
}

export const AnomalyCenterView: React.FC<AnomalyCenterViewProps> = ({ anomalies, onRefresh }) => {
  const [selectedType, setSelectedType] = useState('ALL');
  const [selectedSeverity, setSelectedSeverity] = useState('ALL');
  const [activeAnomaly, setActiveAnomaly] = useState<Anomaly | null>(null);
  const [resolveNotes, setResolveNotes] = useState('');
  const [showModal, setShowModal] = useState(false);

  const issueTypes = ['ALL', ...Array.from(new Set(anomalies.map(a => a.issue_type)))];

  const filtered = anomalies.filter(a => {
    const matchType = selectedType === 'ALL' || a.issue_type === selectedType;
    const matchSev = selectedSeverity === 'ALL' || a.severity === selectedSeverity;
    return matchType && matchSev;
  });

  const handleResolve = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeAnomaly) return;
    try {
      await api.resolveAnomaly(activeAnomaly.anomaly_id, resolveNotes);
      setShowModal(false);
      setResolveNotes('');
      onRefresh();
    } catch (e: any) {
      alert('Error resolving anomaly: ' + e.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Exception & Anomaly Center</h1>
          <p className="text-xs text-slate-400">
            Real-time heuristic integrity scanner: Injected anomalies, structural mismatches, and ground truth mapping.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="h-9 rounded-lg border border-slate-800 bg-slate-900 px-3 text-xs text-slate-300 focus:border-indigo-500 focus:outline-none"
          >
            {issueTypes.map(t => (
              <option key={t} value={t}>
                {t === 'ALL' ? 'All Issue Types' : t}
              </option>
            ))}
          </select>

          <select
            value={selectedSeverity}
            onChange={(e) => setSelectedSeverity(e.target.value)}
            className="h-9 rounded-lg border border-slate-800 bg-slate-900 px-3 text-xs text-slate-300 focus:border-indigo-500 focus:outline-none"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>
        </div>
      </div>

      {/* Anomalies Table */}
      <div className="overflow-hidden rounded-2xl border border-white/[0.08] bg-slate-900/40 backdrop-blur-2xl shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-white/[0.08] bg-slate-950/80 text-slate-400">
              <tr>
                <th className="py-3.5 px-4 font-semibold">Anomaly ID</th>
                <th className="py-3.5 px-4 font-semibold">Severity</th>
                <th className="py-3.5 px-4 font-semibold">Issue Classification</th>
                <th className="py-3.5 px-4 font-semibold">Affected Record</th>
                <th className="py-3.5 px-4 font-semibold">Diagnostic Signature</th>
                <th className="py-3.5 px-4 font-semibold">Expected Resolution</th>
                <th className="py-3.5 px-4 font-semibold text-center">Status</th>
                <th className="py-3.5 px-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.05] text-slate-300">
              {filtered.map((a) => (
                <tr key={a.anomaly_id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-3.5 px-4 font-mono font-medium text-rose-400">{a.anomaly_id}</td>
                  <td className="py-3.5 px-4">
                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-[10px] font-bold border ${
                      a.severity === 'CRITICAL' ? 'bg-red-500/10 text-red-400 border-red-500/30' :
                      a.severity === 'HIGH' ? 'bg-orange-500/10 text-orange-400 border-orange-500/30' :
                      a.severity === 'MEDIUM' ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' :
                      'bg-slate-800 text-slate-300 border border-white/[0.05]'
                    }`}>
                      {a.severity}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 font-semibold text-white">{a.issue_type}</td>
                  <td className="py-3.5 px-4 font-mono text-slate-400">
                    <span className="rounded-lg bg-slate-950/90 px-2 py-1 border border-white/[0.08] text-[11px] text-cyan-300">
                      {a.affected_entity}:{a.affected_record_id}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 max-w-xs truncate text-slate-300" title={a.description}>
                    {a.description}
                  </td>
                  <td className="py-3 px-4 max-w-xs truncate text-slate-400" title={a.expected_resolution}>
                    {a.expected_resolution}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold border ${
                      a.detection_status === 'RESOLVED' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                      'bg-rose-500/10 text-rose-400 border-rose-500/20'
                    }`}>
                      {a.detection_status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    {a.detection_status !== 'RESOLVED' ? (
                      <button
                        onClick={() => {
                          setActiveAnomaly(a);
                          setResolveNotes(a.expected_resolution);
                          setShowModal(true);
                        }}
                        className="inline-flex items-center gap-1 rounded bg-indigo-600 px-2.5 py-1 text-[11px] font-medium text-white hover:bg-indigo-500 transition shadow-sm"
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
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Resolve Anomaly Modal */}
      {showModal && activeAnomaly && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white">Remediate Anomaly Exception</h3>
            <p className="text-xs text-slate-400 mt-1">
              Apply administrative resolution for {activeAnomaly.anomaly_id} ({activeAnomaly.issue_type})
            </p>

            <div className="mt-3 p-3 rounded-lg border border-slate-800 bg-slate-950 text-xs space-y-1">
              <p className="text-slate-400">Affected: <span className="font-mono text-indigo-400">{activeAnomaly.affected_entity}:{activeAnomaly.affected_record_id}</span></p>
              <p className="text-slate-300">{activeAnomaly.description}</p>
            </div>

            <form onSubmit={handleResolve} className="mt-4 space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Remediation Audit Notes</label>
                <textarea
                  required
                  rows={3}
                  value={resolveNotes}
                  onChange={(e) => setResolveNotes(e.target.value)}
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
                  className="rounded-lg bg-emerald-600 px-4 py-2 text-xs font-semibold text-white hover:bg-emerald-500 shadow-md shadow-emerald-600/30"
                >
                  Mark Remediated
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
