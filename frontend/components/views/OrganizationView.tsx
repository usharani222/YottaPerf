'use client';

import React, { useState } from 'react';
import { Network, User, ChevronDown, ChevronRight, UserCheck, ArrowRight, AlertTriangle } from 'lucide-react';
import { HierarchyNode, Employee } from '../../types';
import { api } from '../../services/api';

interface OrganizationViewProps {
  hierarchy: HierarchyNode[];
  employees: Employee[];
  onRefresh: () => void;
}

export const OrganizationView: React.FC<OrganizationViewProps> = ({
  hierarchy,
  employees,
  onRefresh
}) => {
  const [selectedNode, setSelectedNode] = useState<HierarchyNode | null>(null);
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [targetEmpId, setTargetEmpId] = useState('');
  const [newMgrId, setNewMgrId] = useState('');
  const [transferReason, setTransferReason] = useState('');
  const [transferError, setTransferError] = useState('');
  const [transferSuccess, setTransferSuccess] = useState('');

  const handleTransfer = async (e: React.FormEvent) => {
    e.preventDefault();
    setTransferError('');
    setTransferSuccess('');
    try {
      await api.transferManager(targetEmpId, newMgrId || null, transferReason);
      setTransferSuccess(`Successfully transferred ${targetEmpId} to new manager ${newMgrId || 'None'}`);
      onRefresh();
      setTimeout(() => setShowTransferModal(false), 1500);
    } catch (err: any) {
      setTransferError(err.message || 'Transfer failed');
    }
  };

  const renderNode = (node: HierarchyNode, depth: number = 0) => {
    const hasChildren = node.children && node.children.length > 0;
    return (
      <div key={node.id} className="ml-4 border-l border-slate-800 pl-4 py-1.5">
        <div
          onClick={() => setSelectedNode(node)}
          className={`flex items-center justify-between rounded-lg border p-2.5 transition cursor-pointer ${
            selectedNode?.id === node.id
              ? 'border-indigo-500 bg-indigo-950/30'
              : 'border-slate-800/80 bg-slate-900/40 hover:bg-slate-900 hover:border-slate-700'
          }`}
        >
          <div className="flex items-center gap-3">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 text-xs font-bold">
              {node.level}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-white">{node.name}</span>
                <span className="text-[10px] font-mono text-slate-500">{node.id}</span>
              </div>
              <p className="text-[11px] text-slate-400">{node.title} • {node.department}</p>
            </div>
          </div>
          {hasChildren && (
            <span className="rounded-full bg-slate-800 px-2 py-0.5 text-[10px] font-semibold text-slate-400">
              {node.children.length} direct reports
            </span>
          )}
        </div>

        {hasChildren && (
          <div className="mt-1 space-y-1">
            {node.children.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Reporting Hierarchy & Span of Control</h1>
          <p className="text-xs text-slate-400">Deterministic acyclic organizational structure.</p>
        </div>
        <button
          onClick={() => {
            setShowTransferModal(true);
            setTransferError('');
            setTransferSuccess('');
          }}
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-500 transition shadow-md shadow-indigo-600/30"
        >
          <UserCheck className="h-4 w-4" />
          <span>Transfer / Reassign Manager</span>
        </button>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm">
        <div className="flex items-center gap-2 mb-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
          <Network className="h-4 w-4 text-indigo-400" />
          <span>Organizational DAG Tree</span>
        </div>
        <div className="space-y-2">
          {hierarchy.map(rootNode => renderNode(rootNode))}
        </div>
      </div>

      {/* Manager Transfer Modal */}
      {showTransferModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white">Manager Reassignment & Transfer</h3>
            <p className="text-xs text-slate-400 mt-1">
              Validates effective dates, updates history, and rejects circular reporting loops.
            </p>

            {transferError && (
              <div className="mt-4 flex items-center gap-2 rounded-lg border border-rose-500/30 bg-rose-950/40 p-3 text-xs text-rose-300">
                <AlertTriangle className="h-4 w-4 shrink-0" />
                <span>{transferError}</span>
              </div>
            )}

            {transferSuccess && (
              <div className="mt-4 rounded-lg border border-emerald-500/30 bg-emerald-950/40 p-3 text-xs text-emerald-300">
                {transferSuccess}
              </div>
            )}

            <form onSubmit={handleTransfer} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Target Employee</label>
                <select
                  required
                  value={targetEmpId}
                  onChange={(e) => setTargetEmpId(e.target.value)}
                  className="w-full h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-indigo-500 focus:outline-none"
                >
                  <option value="">Select Employee...</option>
                  {employees.map(e => (
                    <option key={e.employee_id} value={e.employee_id}>
                      {e.full_name} ({e.employee_id} - {e.job_title})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">New Manager</label>
                <select
                  required
                  value={newMgrId}
                  onChange={(e) => setNewMgrId(e.target.value)}
                  className="w-full h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-indigo-500 focus:outline-none"
                >
                  <option value="">Select Manager...</option>
                  {employees.map(e => (
                    <option key={e.employee_id} value={e.employee_id}>
                      {e.full_name} ({e.employee_id} - {e.department})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Transfer Justification Reason</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Department reorganization Q3"
                  value={transferReason}
                  onChange={(e) => setTransferReason(e.target.value)}
                  className="w-full h-9 rounded-lg border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowTransferModal(false)}
                  className="rounded-lg px-4 py-2 text-xs font-medium text-slate-400 hover:text-white transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-500 transition shadow-md shadow-indigo-600/30"
                >
                  Commit Transfer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
