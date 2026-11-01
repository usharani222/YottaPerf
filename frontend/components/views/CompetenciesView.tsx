'use client';

import React from 'react';
import { Compass, BookOpen, Layers } from 'lucide-react';
import { Competency } from '../../types';

interface CompetenciesViewProps {
  competencies: Competency[];
}

export const CompetenciesView: React.FC<CompetenciesViewProps> = ({ competencies }) => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">Competency & Capability Framework</h1>
        <p className="text-xs text-slate-400">
          Standard organizational behavioral rubrics and technical capability benchmarks.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {competencies.map((comp) => (
          <div
            key={comp.competency_id}
            className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 space-y-3 hover:border-indigo-500/40 transition"
          >
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-bold text-indigo-400">{comp.competency_id}</span>
              <span className="rounded-full bg-slate-800 px-2 py-0.5 text-[10px] font-semibold text-slate-300">
                {comp.category}
              </span>
            </div>

            <div>
              <h3 className="text-sm font-bold text-white">{comp.name}</h3>
              <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">{comp.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
