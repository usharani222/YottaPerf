'use client';

import React, { useState } from 'react';
import { Search, Filter, User, Mail, Briefcase, Calendar, ChevronRight } from 'lucide-react';
import { Employee } from '../../types';

interface EmployeesViewProps {
  employees: Employee[];
  loading: boolean;
  onSelectEmployee?: (emp: Employee) => void;
}

export const EmployeesView: React.FC<EmployeesViewProps> = ({ employees, loading, onSelectEmployee }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDept, setSelectedDept] = useState('ALL');
  const [selectedEmp, setSelectedEmp] = useState<Employee | null>(null);

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

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Employee Directory</h1>
          <p className="text-xs text-slate-400">Total profiles: {employees.length}</p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Search Input */}
          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
            <input
              type="text"
              placeholder="Search name, ID, title..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="h-9 w-64 rounded-lg border border-slate-800 bg-slate-900/80 pl-9 pr-3 text-xs text-white placeholder-slate-500 focus:border-indigo-500 focus:outline-none"
            />
          </div>

          {/* Department Filter */}
          <select
            value={selectedDept}
            onChange={(e) => setSelectedDept(e.target.value)}
            className="h-9 rounded-lg border border-slate-800 bg-slate-900/80 px-3 text-xs text-slate-300 focus:border-indigo-500 focus:outline-none"
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
      <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/60 shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-800 bg-slate-950/60 text-slate-400">
              <tr>
                <th className="py-3 px-4 font-semibold">Employee ID</th>
                <th className="py-3 px-4 font-semibold">Full Name</th>
                <th className="py-3 px-4 font-semibold">Department</th>
                <th className="py-3 px-4 font-semibold">Title & Level</th>
                <th className="py-3 px-4 font-semibold">Reporting Manager</th>
                <th className="py-3 px-4 font-semibold">Hire Date</th>
                <th className="py-3 px-4 font-semibold text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.slice(0, 50).map((emp) => (
                <tr
                  key={emp.employee_id}
                  onClick={() => setSelectedEmp(emp)}
                  className="hover:bg-slate-800/40 cursor-pointer transition"
                >
                  <td className="py-3 px-4 font-mono font-medium text-indigo-400">{emp.employee_id}</td>
                  <td className="py-3 px-4 font-medium text-white">{emp.full_name}</td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center rounded-md bg-slate-800 px-2 py-0.5 text-[11px] font-medium text-slate-300">
                      {emp.department}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      <span>{emp.job_title}</span>
                      <span className="rounded bg-indigo-500/10 px-1.5 py-0.5 text-[10px] font-semibold text-indigo-400 border border-indigo-500/20">
                        {emp.job_level}
                      </span>
                    </div>
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-400">
                    {emp.manager_id || <span className="text-emerald-400 font-sans font-medium">Chief Executive</span>}
                  </td>
                  <td className="py-3 px-4 text-slate-400">{emp.hire_date}</td>
                  <td className="py-3 px-4 text-center">
                    <span className="inline-flex items-center rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold text-emerald-400 border border-emerald-500/20">
                      Active
                    </span>
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
