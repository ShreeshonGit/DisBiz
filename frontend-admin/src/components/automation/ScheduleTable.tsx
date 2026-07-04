"use client";

import React from "react";
import { Play, Pause, RefreshCw, Edit, Trash2, Copy } from "lucide-react";

interface Schedule {
  id: string;
  brand_id: string;
  brand_name: string;
  schedule_name: string;
  cron_expression: string;
  timezone: string;
  enabled: boolean;
  last_run: string | null;
  next_run: string | null;
  priority: string;
  max_retries: number;
  retry_delay_minutes: number;
  retry_policy: string;
  status: string;
}

interface ScheduleTableProps {
  schedules: Schedule[];
  onRunNow: (id: string) => void;
  onToggleStatus: (id: string, currentlyEnabled: boolean) => void;
  onEdit: (schedule: Schedule) => void;
  onDelete: (id: string) => void;
  onDuplicate: (schedule: Schedule) => void;
}

export default function ScheduleTable({
  schedules,
  onRunNow,
  onToggleStatus,
  onEdit,
  onDelete,
  onDuplicate
}: ScheduleTableProps) {
  const formatDate = (isoStr: string | null) => {
    if (!isoStr) return "--";
    const date = new Date(isoStr);
    return date.toLocaleString("en-IN", { hour12: false });
  };

  const getPriorityColor = (priority: string) => {
    switch (priority?.toUpperCase()) {
      case "HIGH":
        return "bg-rose-50 dark:bg-rose-950/20 text-rose-600 dark:text-rose-450 border-rose-100 dark:border-rose-900/30";
      case "LOW":
        return "bg-slate-50 dark:bg-zinc-800/40 text-slate-500 dark:text-zinc-400 border-slate-200/50 dark:border-zinc-800";
      default:
        return "bg-blue-50 dark:bg-blue-950/20 text-blue-600 dark:text-blue-450 border-blue-100 dark:border-blue-900/30";
    }
  };

  const getStatusBadge = (sched: Schedule) => {
    if (!sched.enabled || sched.status === "PAUSED") {
      return "bg-slate-100 dark:bg-zinc-850 text-slate-500 dark:text-zinc-450 border-slate-200 dark:border-zinc-800";
    }
    if (sched.status === "FAILED") {
      return "bg-red-50 dark:bg-red-950/20 text-red-650 dark:text-red-400 border-red-100 dark:border-red-900/30";
    }
    return "bg-emerald-50 dark:bg-emerald-950/20 text-emerald-650 dark:text-emerald-450 border-emerald-100 dark:border-emerald-900/30";
  };

  return (
    <div className="bg-white dark:bg-zinc-900 border border-slate-200/80 dark:border-zinc-800/80 rounded-2xl overflow-hidden shadow-sm select-none font-sans">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-slate-50 dark:bg-zinc-950 border-b border-slate-200/60 dark:border-zinc-800/60 text-slate-500 dark:text-zinc-400 font-bold uppercase tracking-wider text-[10px]">
              <th className="px-6 py-4">Brand</th>
              <th className="px-6 py-4">Schedule</th>
              <th className="px-6 py-4">Cron Expression</th>
              <th className="px-6 py-4 text-center">Priority</th>
              <th className="px-6 py-4">Last Run</th>
              <th className="px-6 py-4">Next Run</th>
              <th className="px-6 py-4 text-center">Status</th>
              <th className="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-150 dark:divide-zinc-800/80 text-slate-700 dark:text-zinc-200 font-medium">
            {schedules.length === 0 ? (
              <tr>
                <td colSpan={8} className="text-center py-12 text-slate-400 dark:text-zinc-500 font-medium">
                  No automated scraper schedules configured. Click &quot;Create Schedule&quot; to define triggers.
                </td>
              </tr>
            ) : (
              schedules.map((sched) => (
                <tr key={sched.id} className="hover:bg-slate-50/50 dark:hover:bg-zinc-900/40 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="h-7 w-7 rounded-lg bg-slate-100 dark:bg-zinc-950 border border-slate-200/50 dark:border-zinc-850 flex items-center justify-center font-bold text-[10px]">
                        {sched.brand_name.slice(0, 2).toUpperCase()}
                      </div>
                      <span className="font-bold">{sched.brand_name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 font-semibold text-slate-900 dark:text-zinc-50">
                    {sched.schedule_name}
                  </td>
                  <td className="px-6 py-4 font-mono text-[11px] text-indigo-650 dark:text-indigo-400">
                    {sched.cron_expression}
                  </td>
                  <td className="px-6 py-4 text-center">
                    <span className={`inline-flex px-2 py-0.5 rounded-md border text-[10px] font-bold ${getPriorityColor(sched.priority)}`}>
                      {sched.priority}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-500 dark:text-zinc-400">
                    {formatDate(sched.last_run)}
                  </td>
                  <td className="px-6 py-4 text-slate-500 dark:text-zinc-400">
                    {formatDate(sched.next_run)}
                  </td>
                  <td className="px-6 py-4 text-center">
                    <span className={`inline-flex px-2 py-0.5 rounded-md border text-[10px] font-bold ${getStatusBadge(sched)}`}>
                      {sched.enabled && sched.status === "ACTIVE" ? "ACTIVE" : sched.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      <button
                        onClick={() => onRunNow(sched.id)}
                        title="Run scraper now"
                        className="p-1.5 rounded-lg border border-slate-200 dark:border-zinc-800 text-slate-650 dark:text-zinc-350 hover:bg-emerald-50 dark:hover:bg-emerald-950/20 hover:text-emerald-600 transition-colors cursor-pointer"
                      >
                        <Play className="h-3.5 w-3.5" />
                      </button>
                      
                      <button
                        onClick={() => onToggleStatus(sched.id, sched.enabled)}
                        title={sched.enabled ? "Pause Schedule" : "Resume Schedule"}
                        className="p-1.5 rounded-lg border border-slate-200 dark:border-zinc-800 text-slate-650 dark:text-zinc-350 hover:bg-amber-50 dark:hover:bg-amber-950/20 hover:text-amber-600 transition-colors cursor-pointer"
                      >
                        {sched.enabled ? <Pause className="h-3.5 w-3.5" /> : <RefreshCw className="h-3.5 w-3.5" />}
                      </button>

                      <button
                        onClick={() => onDuplicate(sched)}
                        title="Duplicate Schedule"
                        className="p-1.5 rounded-lg border border-slate-200 dark:border-zinc-800 text-slate-650 dark:text-zinc-350 hover:bg-indigo-50 dark:hover:bg-indigo-950/20 hover:text-indigo-600 transition-colors cursor-pointer"
                      >
                        <Copy className="h-3.5 w-3.5" />
                      </button>

                      <button
                        onClick={() => onEdit(sched)}
                        title="Edit Configuration"
                        className="p-1.5 rounded-lg border border-slate-200 dark:border-zinc-800 text-slate-650 dark:text-zinc-350 hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer"
                      >
                        <Edit className="h-3.5 w-3.5" />
                      </button>

                      <button
                        onClick={() => onDelete(sched.id)}
                        title="Delete Schedule"
                        className="p-1.5 rounded-lg border border-slate-200 dark:border-zinc-800 text-slate-650 dark:text-zinc-350 hover:bg-rose-50 dark:hover:bg-rose-950/20 hover:text-rose-600 transition-colors cursor-pointer"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
