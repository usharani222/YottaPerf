'use client';

import React, { useState } from 'react';
import { api } from '@/services/api';
import { 
  Database, 
  Cpu, 
  CheckCircle2, 
  AlertTriangle, 
  Play, 
  RefreshCw, 
  ShieldCheck, 
  Layers, 
  Activity, 
  FileCheck,
  Server
} from 'lucide-react';

export default function AdminView() {
  const [genMode, setGenMode] = useState<'starter' | 'full'>('starter');
  const [genSeed, setGenSeed] = useState<number>(20261022);
  const [isGenerating, setIsGenerating] = useState(false);
  const [genResult, setGenResult] = useState<any>(null);
  const [genError, setGenError] = useState<string | null>(null);

  const [valDataset, setValDataset] = useState<string>('generated_data/starter');
  const [isValidating, setIsValidating] = useState(false);
  const [valResult, setValResult] = useState<any>(null);
  const [valError, setValError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setGenError(null);
    setGenResult(null);
    try {
      const res = await api.generateData(genMode, genSeed);
      setGenResult(res);
    } catch (err: any) {
      setGenError(err.message || 'Data generation failed');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleValidate = async () => {
    setIsValidating(true);
    setValError(null);
    setValResult(null);
    try {
      const res = await api.validateData(valDataset);
      setValResult(res);
    } catch (err: any) {
      setValError(err.message || 'Validation execution failed');
    } finally {
      setIsValidating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
          <Server className="w-6 h-6 text-indigo-400" />
          System Administration & Operations
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Execute deterministic data generation pipelines, trigger the 15-point automated validation engine, and monitor system health.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Synthetic Data Generation Engine Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  <Database className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-base font-semibold text-slate-100">Deterministic Synthetic Generator</h2>
                  <p className="text-xs text-slate-400">Generate referentially-sound synthetic datasets</p>
                </div>
              </div>
              <span className="text-xs px-2.5 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full font-mono">
                SEED: 20261022
              </span>
            </div>

            <div className="mt-5 space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Generation Mode</label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setGenMode('starter')}
                    className={`px-4 py-2.5 rounded-lg text-sm font-medium border text-left transition-all ${
                      genMode === 'starter'
                        ? 'bg-indigo-600/20 border-indigo-500 text-indigo-300 shadow-sm'
                        : 'bg-slate-800/50 border-slate-700 text-slate-400 hover:border-slate-600'
                    }`}
                  >
                    <div className="font-semibold text-slate-200">Starter Mode</div>
                    <div className="text-xs text-slate-400">50 Emps, 10 Mgrs, 150 Goals</div>
                  </button>
                  <button
                    type="button"
                    onClick={() => setGenMode('full')}
                    className={`px-4 py-2.5 rounded-lg text-sm font-medium border text-left transition-all ${
                      genMode === 'full'
                        ? 'bg-indigo-600/20 border-indigo-500 text-indigo-300 shadow-sm'
                        : 'bg-slate-800/50 border-slate-700 text-slate-400 hover:border-slate-600'
                    }`}
                  >
                    <div className="font-semibold text-slate-200">Full Mode</div>
                    <div className="text-xs text-slate-400">3,000 Emps, 500 Mgrs, 10,000 Goals</div>
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Deterministic Random Seed</label>
                <input
                  type="number"
                  value={genSeed}
                  onChange={(e) => setGenSeed(parseInt(e.target.value) || 20261022)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 font-mono focus:outline-none focus:border-indigo-500"
                />
                <p className="text-[11px] text-slate-400 mt-1">Guarantees bit-for-bit reproducible output files and SHA-256 manifest verification.</p>
              </div>

              {genError && (
                <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-400 text-xs flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 shrink-0" />
                  <span>{genError}</span>
                </div>
              )}

              {genResult && (
                <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-lg space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-emerald-400 flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4" /> Generation Succeeded
                    </span>
                    <span className="text-xs text-slate-400 font-mono">Mode: {genResult.mode}</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs font-mono text-slate-300 pt-2 border-t border-slate-800">
                    <div>Employees: {genResult.row_counts?.employees || 0}</div>
                    <div>Managers: {genResult.row_counts?.managers || 0}</div>
                    <div>Goals: {genResult.row_counts?.goals || 0}</div>
                    <div>Key Results: {genResult.row_counts?.key_results || 0}</div>
                    <div>Check-ins: {genResult.row_counts?.check_ins || 0}</div>
                    <div>Reviews: {genResult.row_counts?.reviews || 0}</div>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800">
            <button
              onClick={handleGenerate}
              disabled={isGenerating}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors shadow-md"
            >
              {isGenerating ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Generating & Ingesting Dataset...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Run Synthetic Data Pipeline
                </>
              )}
            </button>
          </div>
        </div>

        {/* 15-Point Automated Validation Engine Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-base font-semibold text-slate-100">Automated Validation Engine</h2>
                  <p className="text-xs text-slate-400">15-Point multi-dimensional relational integrity test</p>
                </div>
              </div>
              <span className="text-xs px-2.5 py-1 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-full font-mono">
                15 CHECKS (A-O)
              </span>
            </div>

            <div className="mt-5 space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Target Dataset Path</label>
                <input
                  type="text"
                  value={valDataset}
                  onChange={(e) => setValDataset(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 font-mono focus:outline-none focus:border-emerald-500"
                  placeholder="generated_data/starter"
                />
                <p className="text-[11px] text-slate-400 mt-1">
                  JSON dataset folder containing relational entity tables and ground_truth.json.
                </p>
              </div>

              {valError && (
                <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-400 text-xs flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 shrink-0" />
                  <span>{valError}</span>
                </div>
              )}

              {valResult && (
                <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-lg space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-400">Validation Status</span>
                    <span
                      className={`text-xs px-2.5 py-0.5 rounded-full font-semibold ${
                        valResult.validation_status === 'PASSED'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      }`}
                    >
                      {valResult.validation_status || 'UNKNOWN'}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs font-mono text-slate-300 pt-2 border-t border-slate-800">
                    <div>Records Scanned: {valResult.total_records_validated || 0}</div>
                    <div>PK Violations: {valResult.primary_key_violations || 0}</div>
                    <div>FK Violations: {valResult.foreign_key_violations || 0}</div>
                    <div>Date Sequence Errors: {valResult.invalid_date_sequences || 0}</div>
                    <div>Detected Anomalies: {valResult.detected_anomalies || 0}</div>
                    <div>Ground-Truth Matches: {valResult.ground_truth_matches || 0}</div>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800">
            <button
              onClick={handleValidate}
              disabled={isValidating}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors shadow-md"
            >
              {isValidating ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Executing 15 Integrity Checks...
                </>
              ) : (
                <>
                  <FileCheck className="w-4 h-4" />
                  Run Validation Audit
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* System Infrastructure Details */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h3 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
          <Activity className="w-4 h-4 text-indigo-400" />
          Environment & Infrastructure Status
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-4 rounded-lg bg-slate-950/60 border border-slate-800">
            <div className="text-xs text-slate-400 mb-1">Backend API</div>
            <div className="text-sm font-mono text-emerald-400 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              FastAPI 0.110+ (Port 8001)
            </div>
          </div>

          <div className="p-4 rounded-lg bg-slate-950/60 border border-slate-800">
            <div className="text-xs text-slate-400 mb-1">PostgreSQL Database</div>
            <div className="text-sm font-mono text-emerald-400 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              PostgreSQL 16 (Port 5434)
            </div>
          </div>

          <div className="p-4 rounded-lg bg-slate-950/60 border border-slate-800">
            <div className="text-xs text-slate-400 mb-1">ORM & Migrations</div>
            <div className="text-sm font-mono text-slate-300">SQLAlchemy 2.0 / Alembic</div>
          </div>

          <div className="p-4 rounded-lg bg-slate-950/60 border border-slate-800">
            <div className="text-xs text-slate-400 mb-1">Frontend Stack</div>
            <div className="text-sm font-mono text-slate-300">Next.js 14 App Router (3002)</div>
          </div>
        </div>
      </div>
    </div>
  );
}
