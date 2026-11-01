'use client';

import React, { useState } from 'react';
import { History, Shield, ChevronDown, ChevronRight, FileJson } from 'lucide-react';
import { AuditEvent } from '../../types';

interface AuditLogsViewProps {
  auditEvents: AuditEvent[];
}

export const AuditLogsView: React.FC<AuditLogsViewProps> = ({ auditEvents }) => {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">Immutable Security & Audit Ledger</h1>
        <p className="text-xs text-slate-400">
          Append-only cryptographic event trail documenting every administrative override and state transition.
        </p>
      </div>

      <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/60 shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-800 bg-slate-950/60 text-slate-400">
              <tr>
                <th className="py-3 px-4 font-semibold">Event ID</th>
                <th className="py-3 px-4 font-semibold">Timestamp</th>
                <th className="py-3 px-4 font-semibold">Actor ID</th>
                <th className="py-3 px-4 font-semibold">Operation</th>
                <th className="py-3 px-4 font-semibold">Target Entity</th>
                <th className="py-3 px-4 font-semibold">Audit Justification</th>
                <th className="py-3 px-4 font-semibold text-center">Payload</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {auditEvents.map((ev) => {
                const isExpanded = expandedId === ev.event_id;
                return (
                  <React.Fragment key={ev.event_id}>
                    <tr className="hover:bg-slate-800/40 transition">
                      <td className="py-3 px-4 font-mono font-medium text-indigo-400">{ev.event_id}</td>
                      <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">{ev.timestamp}</td>
                      <td className="py-3 px-4 font-mono text-slate-300">{ev.actor_id || 'SYSTEM'}</td>
                      <td className="py-3 px-4">
                        <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold border ${
                          ev.operation_type === 'CORRECTION' ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' :
                          ev.operation_type === 'CREATE' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' :
                          'bg-indigo-500/10 text-indigo-400 border-indigo-500/30'
                        }`}>
                          {ev.operation_type}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono text-slate-300">
                        {ev.entity_name}:{ev.entity_id}
                      </td>
                      <td className="py-3 px-4 text-slate-300 max-w-xs truncate" title={ev.reason || ''}>
                        {ev.reason || '—'}
                      </td>
                      <td className="py-3 px-4 text-center">
                        {(ev.old_values || ev.new_values) && (
                          <button
                            onClick={() => setExpandedId(isExpanded ? null : ev.event_id)}
                            className="inline-flex items-center gap-1 rounded bg-slate-800 px-2 py-1 text-[10px] text-slate-300 hover:text-white hover:bg-slate-700 transition"
                          >
                            <FileJson className="h-3 w-3 text-indigo-400" />
                            <span>{isExpanded ? 'Hide' : 'Inspect'}</span>
                          </button>
                        )}
                      </td>
                    </tr>
                    {isExpanded && (
                      <tr className="bg-slate-950/80">
                        <td colSpan={7} className="p-4">
                          <div className="rounded-lg border border-slate-800 bg-slate-950 p-3 text-[11px] font-mono space-y-2">
                            {ev.old_values && (
                              <div>
                                <span className="text-rose-400 font-semibold block mb-1">Previous Values:</span>
                                <pre className="text-slate-400 whitespace-pre-wrap">{JSON.stringify(ev.old_values, null, 2)}</pre>
                              </div>
                            )}
                            {ev.new_values && (
                              <div>
                                <span className="text-emerald-400 font-semibold block mb-1">New Values:</span>
                                <pre className="text-slate-300 whitespace-pre-wrap">{JSON.stringify(ev.new_values, null, 2)}</pre>
                              </div>
                            )}
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
