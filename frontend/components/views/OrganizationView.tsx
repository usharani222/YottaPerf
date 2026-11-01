'use client';

import React, { useState, useMemo, useEffect } from 'react';
import {
  Network, User, ChevronDown, ChevronRight, UserCheck, ArrowRight,
  AlertTriangle, ShieldCheck, Building, Layers, Search, RefreshCw,
  FolderTree, Minimize2, Maximize2, UserPlus, Info, CheckCircle2
} from 'lucide-react';
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
  // Collect all node IDs for Expand/Collapse All
  const allNodeIds = useMemo(() => {
    const ids = new Set<string>();
    const traverse = (node: HierarchyNode) => {
      ids.add(node.id);
      if (node.children) {
        node.children.forEach(traverse);
      }
    };
    hierarchy.forEach(traverse);
    return ids;
  }, [hierarchy]);

  // Initial expanded state: expand top 2 levels
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(() => {
    const initial = new Set<string>();
    hierarchy.forEach(root => {
      initial.add(root.id);
      if (root.children) {
        root.children.forEach(c => initial.add(c.id));
      }
    });
    return initial;
  });

  // Ensure expandedNodes is populated when hierarchy asynchronously resolves
  useEffect(() => {
    if (hierarchy.length > 0) {
      setExpandedNodes(prev => {
        if (prev.size > 0) return prev;
        const initial = new Set<string>();
        hierarchy.forEach(root => {
          initial.add(root.id);
          if (root.children) {
            root.children.forEach(c => initial.add(c.id));
          }
        });
        return initial;
      });
    }
  }, [hierarchy]);

  const [selectedNode, setSelectedNode] = useState<HierarchyNode | null>(null);
  const [selectedEmpProfile, setSelectedEmpProfile] = useState<any>(null);
  const [profileLoading, setProfileLoading] = useState(false);

  const [showTransferModal, setShowTransferModal] = useState(false);
  const [targetEmpId, setTargetEmpId] = useState('');
  const [newMgrId, setNewMgrId] = useState('');
  const [transferReason, setTransferReason] = useState('');
  const [transferError, setTransferError] = useState('');
  const [transferSuccess, setTransferSuccess] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const toggleNode = (nodeId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setExpandedNodes(prev => {
      const next = new Set(prev);
      if (next.has(nodeId)) {
        next.delete(nodeId);
      } else {
        next.add(nodeId);
      }
      return next;
    });
  };

  const handleExpandAll = () => {
    setExpandedNodes(new Set(allNodeIds));
  };

  const handleCollapseAll = () => {
    setExpandedNodes(new Set());
  };

  const handleSelectNode = async (node: HierarchyNode) => {
    setSelectedNode(node);
    setProfileLoading(true);
    setSelectedEmpProfile(null);
    try {
      const p = await api.getEmployeePerformanceProfile(node.id);
      setSelectedEmpProfile(p);
    } catch (err) {
      console.error('Failed to fetch profile for hierarchy node:', err);
    } finally {
      setProfileLoading(false);
    }
  };

  const handleTransfer = async (e: React.FormEvent) => {
    e.preventDefault();
    setTransferError('');
    setTransferSuccess('');
    setIsSubmitting(true);
    try {
      await api.transferManager(targetEmpId, newMgrId || null, transferReason);
      setTransferSuccess(`Successfully transferred ${targetEmpId} to new manager ${newMgrId || 'None (Root Node)'}.`);
      onRefresh();
      setTimeout(() => setShowTransferModal(false), 1500);
    } catch (err: any) {
      setTransferError(err.message || 'Transfer failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderNode = (node: HierarchyNode, depth: number = 0) => {
    const hasChildren = node.children && node.children.length > 0;
    const isExpanded = expandedNodes.has(node.id);
    const isSelected = selectedNode?.id === node.id;

    return (
      <div key={node.id} className="relative">
        <div
          onClick={() => handleSelectNode(node)}
          style={{ marginLeft: `${depth * 20}px` }}
          className={`group flex items-center justify-between rounded-xl border p-3 my-1.5 transition-all cursor-pointer ${
            isSelected
              ? 'border-emerald-500/60 bg-emerald-950/20 shadow-md shadow-emerald-500/5'
              : 'border-white/[0.08] bg-slate-900/50 hover:bg-slate-900 hover:border-white/[0.15]'
          }`}
        >
          <div className="flex items-center gap-3">
            {/* Expand / Collapse Toggle */}
            {hasChildren ? (
              <button
                onClick={(e) => toggleNode(node.id, e)}
                className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition"
              >
                {isExpanded ? (
                  <ChevronDown className="h-4 w-4 text-emerald-400" />
                ) : (
                  <ChevronRight className="h-4 w-4 text-slate-400" />
                )}
              </button>
            ) : (
              <div className="w-6 h-6 flex items-center justify-center">
                <span className="h-1.5 w-1.5 rounded-full bg-slate-600" />
              </div>
            )}

            {/* Level Badge */}
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[11px] font-bold font-mono">
              {node.level}
            </div>

            {/* Employee Details */}
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-white group-hover:text-emerald-300 transition-colors">
                  {node.name}
                </span>
                <span className="text-[10px] font-mono text-emerald-400/80 bg-emerald-500/5 px-1.5 py-0.2 rounded border border-emerald-500/10">
                  {node.id}
                </span>
                <span className="text-[10px] text-slate-400">
                  • {node.department}
                </span>
              </div>
              <p className="text-[11px] text-slate-400">{node.title}</p>
            </div>
          </div>

          {/* Right Metrics & Badges */}
          <div className="flex items-center gap-2">
            {hasChildren && (
              <span className="rounded-full bg-slate-800/80 px-2.5 py-0.5 text-[10px] font-semibold text-slate-300 border border-white/[0.05]">
                {node.children.length} direct reports
              </span>
            )}
          </div>
        </div>

        {/* Children Subtree */}
        {hasChildren && isExpanded && (
          <div className="space-y-0.5">
            {node.children.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Network className="h-6 w-6 text-emerald-400" />
            Organizational DAG & Span of Control
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Deterministic acyclic reporting hierarchy with cycle detection and historical manager transfer logs.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={handleExpandAll}
            className="flex items-center gap-1.5 rounded-xl border border-white/[0.08] bg-slate-900 px-3 py-1.5 text-xs font-semibold text-slate-300 hover:text-white transition"
          >
            <Maximize2 className="h-3.5 w-3.5" />
            <span>Expand All</span>
          </button>
          <button
            onClick={handleCollapseAll}
            className="flex items-center gap-1.5 rounded-xl border border-white/[0.08] bg-slate-900 px-3 py-1.5 text-xs font-semibold text-slate-300 hover:text-white transition"
          >
            <Minimize2 className="h-3.5 w-3.5" />
            <span>Collapse All</span>
          </button>
          <button
            onClick={() => {
              setShowTransferModal(true);
              setTransferError('');
              setTransferSuccess('');
            }}
            className="flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 px-3.5 py-1.5 text-xs font-semibold text-white shadow-lg shadow-emerald-500/20 hover:from-emerald-400 hover:to-teal-500 transition"
          >
            <UserCheck className="h-4 w-4" />
            <span>Transfer / Reassign</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Tree (left 3 cols) and Inspector (right 2 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Tree Container */}
        <div className="lg:col-span-3 rounded-2xl border border-white/[0.08] bg-slate-900/40 p-5 backdrop-blur-2xl shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-white/[0.06]">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-300">
              <FolderTree className="h-4 w-4 text-emerald-400" />
              <span>Hierarchical DAG Structure ({employees.length} Personnel)</span>
            </div>
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
              Non-Circular DAG
            </span>
          </div>

          <div className="max-h-[650px] overflow-y-auto pr-1">
            {hierarchy.map(rootNode => renderNode(rootNode))}
          </div>
        </div>

        {/* Selected Node Inspector Panel */}
        <div className="lg:col-span-2 rounded-2xl border border-white/[0.08] bg-slate-900/40 p-5 backdrop-blur-2xl shadow-xl flex flex-col justify-between space-y-4">
          {selectedNode ? (
            <div className="space-y-4">
              <div className="pb-3 border-b border-white/[0.06]">
                <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400">
                  Node Inspector
                </span>
                <div className="flex items-center gap-2 mt-1">
                  <h3 className="text-base font-bold text-white">{selectedNode.name}</h3>
                  <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                    {selectedNode.id}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  {selectedNode.title} • {selectedNode.department} ({selectedNode.level})
                </p>
              </div>

              {/* Manager & Direct Reports Cards */}
              <div className="space-y-2.5">
                <div className="rounded-xl bg-slate-950/70 p-3 border border-white/[0.05] text-xs">
                  <span className="text-[10px] uppercase font-bold text-slate-500 block">Reporting Manager</span>
                  <div className="flex items-center justify-between mt-1">
                    <span className="font-semibold text-slate-200">
                      {selectedEmpProfile?.manager
                        ? `${selectedEmpProfile.manager.full_name} (${selectedEmpProfile.manager.job_title})`
                        : (selectedNode.manager_id ? selectedNode.manager_id : 'Chief Executive Officer (Root Node)')}
                    </span>
                    <span className="font-mono text-xs text-slate-400">
                      {selectedNode.manager_id || 'ROOT'}
                    </span>
                  </div>
                </div>

                <div className="rounded-xl bg-slate-950/70 p-3 border border-white/[0.05] text-xs">
                  <span className="text-[10px] uppercase font-bold text-slate-500 block">Span of Control</span>
                  <div className="flex items-center justify-between mt-1">
                    <span className="font-semibold text-slate-200">
                      {selectedNode.children?.length ?? 0} Direct Subordinates
                    </span>
                    <span className="text-[10px] text-emerald-400 font-mono">Active</span>
                  </div>
                </div>
              </div>

              {/* Manager Transfer History */}
              <div className="space-y-2 pt-2 border-t border-white/[0.06]">
                <span className="text-xs font-bold text-white flex items-center gap-1.5">
                  <Building className="h-3.5 w-3.5 text-cyan-400" />
                  Manager Reassignment History
                </span>

                {profileLoading ? (
                  <div className="py-4 text-center text-xs text-slate-500">Loading audit history...</div>
                ) : (!selectedEmpProfile?.manager_history || selectedEmpProfile.manager_history.length === 0) ? (
                  <p className="text-xs text-slate-500 italic">No historical reassignments on record.</p>
                ) : (
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {selectedEmpProfile.manager_history.map((h: any) => (
                      <div key={h.history_id} className="p-2.5 rounded-lg bg-slate-950/80 border border-white/[0.05] text-xs space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="font-mono font-semibold text-cyan-300">Manager: {h.manager_id}</span>
                          <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded ${h.is_current ? 'bg-emerald-500/10 text-emerald-400' : 'text-slate-500'}`}>
                            {h.is_current ? 'Current' : 'Past'}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400">
                          {h.start_date} → {h.end_date || 'Present'}
                        </p>
                        <p className="text-[11px] text-slate-300">
                          Reason: {h.transfer_reason || 'Initial seed assignment'}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Circular Protection Guard */}
              <div className="rounded-xl border border-emerald-500/20 bg-emerald-950/15 p-3 text-xs space-y-1">
                <div className="flex items-center gap-1.5 text-emerald-400 font-semibold text-[11px]">
                  <ShieldCheck className="h-4 w-4" />
                  <span>Cycle Prevention Guard Active</span>
                </div>
                <p className="text-slate-300 text-[11px] leading-relaxed">
                  PostgreSQL recursive CTE validates that assigning a new manager does not create an inverted cyclical loop (A → B → C → A).
                </p>
              </div>
            </div>
          ) : (
            <div className="h-72 flex flex-col items-center justify-center text-center p-6 text-slate-500 text-xs">
              <Network className="h-10 w-10 text-slate-700 mb-2" />
              <p className="font-semibold text-slate-400">Select any node in the hierarchy</p>
              <p className="mt-1">Inspect manager assignment, direct subordinate list, and transfer audit history.</p>
            </div>
          )}
        </div>
      </div>

      {/* Manager Transfer Modal */}
      {showTransferModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl border border-white/[0.08] bg-slate-950 p-6 shadow-2xl animate-in zoom-in-95 duration-200">
            <h3 className="text-lg font-bold text-white">Manager Reassignment & Transfer</h3>
            <p className="text-xs text-slate-400 mt-1">
              Validates effective dates, records history, and prevents circular reporting loops.
            </p>

            {transferError && (
              <div className="mt-4 flex items-center gap-2 rounded-xl border border-rose-500/30 bg-rose-950/40 p-3 text-xs text-rose-300">
                <AlertTriangle className="h-4 w-4 shrink-0" />
                <span>{transferError}</span>
              </div>
            )}

            {transferSuccess && (
              <div className="mt-4 rounded-xl border border-emerald-500/30 bg-emerald-950/40 p-3 text-xs text-emerald-300">
                {transferSuccess}
              </div>
            )}

            <form onSubmit={handleTransfer} className="mt-4 space-y-3.5">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Target Employee</label>
                <select
                  required
                  value={targetEmpId}
                  onChange={(e) => setTargetEmpId(e.target.value)}
                  className="w-full h-9 rounded-xl border border-white/[0.08] bg-slate-900 px-3 text-xs text-white focus:border-emerald-500 focus:outline-none"
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
                <label className="block text-xs font-semibold text-slate-300 mb-1">New Reporting Manager</label>
                <select
                  required
                  value={newMgrId}
                  onChange={(e) => setNewMgrId(e.target.value)}
                  className="w-full h-9 rounded-xl border border-white/[0.08] bg-slate-900 px-3 text-xs text-white focus:border-emerald-500 focus:outline-none"
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
                <label className="block text-xs font-semibold text-slate-300 mb-1">Transfer Justification Reason</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Department reorganization Q3"
                  value={transferReason}
                  onChange={(e) => setTransferReason(e.target.value)}
                  className="w-full h-9 rounded-xl border border-white/[0.08] bg-slate-900 px-3 text-xs text-white focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-white/[0.08]">
                <button
                  type="button"
                  onClick={() => setShowTransferModal(false)}
                  className="rounded-xl px-4 py-2 text-xs font-medium text-slate-400 hover:text-white transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 px-4 py-2 text-xs font-semibold text-white hover:from-emerald-400 hover:to-teal-500 transition shadow-md shadow-emerald-500/20"
                >
                  {isSubmitting ? 'Committing...' : 'Commit Transfer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
