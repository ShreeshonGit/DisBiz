"use client";

import React, { useState, useEffect } from "react";
import { X } from "lucide-react";

interface Brand {
  id: string;
  name: string;
}

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

interface ScheduleModalProps {
  isOpen: boolean;
  onClose: () => void;
  brands: Brand[];
  scheduleToEdit: Schedule | null;
  onSave: (data: Partial<Schedule>) => void;
}

export default function ScheduleModal({
  isOpen,
  onClose,
  brands,
  scheduleToEdit,
  onSave
}: ScheduleModalProps) {
  const [brandId, setBrandId] = useState("");
  const [scheduleName, setScheduleName] = useState("");
  const [cronExpression, setCronExpression] = useState("0 * * * *");
  const [timezone, setTimezone] = useState("UTC");
  const [priority, setPriority] = useState("MEDIUM");
  const [maxRetries, setMaxRetries] = useState(3);
  const [retryDelayMinutes, setRetryDelayMinutes] = useState(5);
  const [retryPolicy, setRetryPolicy] = useState("EXPONENTIAL");

  useEffect(() => {
    if (scheduleToEdit) {
      setBrandId(scheduleToEdit.brand_id);
      setScheduleName(scheduleToEdit.schedule_name);
      setCronExpression(scheduleToEdit.cron_expression);
      setTimezone(scheduleToEdit.timezone || "UTC");
      setPriority(scheduleToEdit.priority || "MEDIUM");
      setMaxRetries(scheduleToEdit.max_retries || 3);
      setRetryDelayMinutes(scheduleToEdit.retry_delay_minutes || 5);
      setRetryPolicy(scheduleToEdit.retry_policy || "EXPONENTIAL");
    } else {
      setBrandId(brands[0]?.id || "");
      setScheduleName("");
      setCronExpression("0 2 * * *");
      setTimezone("UTC");
      setPriority("MEDIUM");
      setMaxRetries(3);
      setRetryDelayMinutes(5);
      setRetryPolicy("EXPONENTIAL");
    }
  }, [scheduleToEdit, isOpen, brands]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave({
      id: scheduleToEdit?.id,
      brand_id: brandId,
      schedule_name: scheduleName,
      cron_expression: cronExpression,
      timezone,
      priority,
      max_retries: maxRetries,
      retry_delay_minutes: retryDelayMinutes,
      retry_policy: retryPolicy
    });
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 font-sans select-none">
      <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl">
        <div className="px-6 py-4 border-b border-slate-100 dark:border-zinc-850 flex items-center justify-between">
          <h3 className="font-bold text-sm text-slate-900 dark:text-zinc-55">
            {scheduleToEdit ? "Modify Schedule" : "New Automation Schedule"}
          </h3>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-zinc-800">
            <X className="h-4.5 w-4.5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4 text-xs font-semibold text-slate-650 dark:text-zinc-400">
          {/* Brand select */}
          <div className="space-y-1.5">
            <label className="block text-[10px] uppercase font-bold text-slate-400 tracking-wider">Manufacturer Brand</label>
            <select
              value={brandId}
              onChange={(e) => setBrandId(e.target.value)}
              disabled={!!scheduleToEdit}
              className="w-full px-3 py-2.5 rounded-xl border border-slate-200 dark:border-zinc-800 bg-slate-50 dark:bg-zinc-950 focus:outline-none"
            >
              {brands.map((b) => (
                <option key={b.id} value={b.id}>{b.name}</option>
              ))}
            </select>
          </div>

          {/* Schedule Name */}
          <div className="space-y-1.5">
            <label className="block text-[10px] uppercase font-bold text-slate-400 tracking-wider">Schedule Name</label>
            <input
              type="text"
              required
              value={scheduleName}
              onChange={(e) => setScheduleName(e.target.value)}
              placeholder="e.g. Daily Outlets Crawl"
              className="w-full px-3 py-2.5 rounded-xl border border-slate-200 dark:border-zinc-800 bg-slate-50 dark:bg-zinc-950 focus:outline-none font-medium text-slate-900 dark:text-zinc-50"
            />
          </div>

          {/* Cron & Priority Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="block text-[10px] uppercase font-bold text-slate-400 tracking-wider">Cron Schedule</label>
              <input
                type="text"
                required
                value={cronExpression}
                onChange={(e) => setCronExpression(e.target.value)}
                placeholder="e.g. 0 2 * * *"
                className="w-full px-3 py-2.5 rounded-xl border border-slate-200 dark:border-zinc-800 bg-slate-50 dark:bg-zinc-950 focus:outline-none font-mono font-medium text-slate-900 dark:text-zinc-50"
              />
            </div>
            <div className="space-y-1.5">
              <label className="block text-[10px] uppercase font-bold text-slate-400 tracking-wider">Execution Priority</label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="w-full px-3 py-2.5 rounded-xl border border-slate-200 dark:border-zinc-800 bg-slate-50 dark:bg-zinc-950 focus:outline-none"
              >
                <option value="HIGH">HIGH (Runs First)</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="LOW">LOW</option>
              </select>
            </div>
          </div>

          {/* Retries config */}
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-1.5">
              <label className="block text-[10px] uppercase font-bold text-slate-400 tracking-wider">Max Retries</label>
              <input
                type="number"
                min="0"
                max="10"
                value={maxRetries}
                onChange={(e) => setMaxRetries(parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2.5 rounded-xl border border-slate-200 dark:border-zinc-800 bg-slate-50 dark:bg-zinc-950 focus:outline-none font-medium text-slate-900 dark:text-zinc-50"
              />
            </div>
            <div className="space-y-1.5">
              <label className="block text-[10px] uppercase font-bold text-slate-400 tracking-wider">Delay (min)</label>
              <input
                type="number"
                min="1"
                max="60"
                value={retryDelayMinutes}
                onChange={(e) => setRetryDelayMinutes(parseInt(e.target.value) || 1)}
                className="w-full px-3 py-2.5 rounded-xl border border-slate-200 dark:border-zinc-800 bg-slate-50 dark:bg-zinc-950 focus:outline-none font-medium text-slate-900 dark:text-zinc-50"
              />
            </div>
            <div className="space-y-1.5">
              <label className="block text-[10px] uppercase font-bold text-slate-400 tracking-wider">Retry Policy</label>
              <select
                value={retryPolicy}
                onChange={(e) => setRetryPolicy(e.target.value)}
                className="w-full px-3 py-2.5 rounded-xl border border-slate-200 dark:border-zinc-800 bg-slate-50 dark:bg-zinc-950 focus:outline-none"
              >
                <option value="EXPONENTIAL">Exponential</option>
                <option value="LINEAR">Linear</option>
                <option value="IMMEDIATE">Immediate</option>
              </select>
            </div>
          </div>

          {/* Action row */}
          <div className="pt-4 border-t border-slate-100 dark:border-zinc-850 flex gap-2 justify-end">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-bold border border-slate-200 dark:border-zinc-800 rounded-xl hover:bg-slate-50 dark:hover:bg-zinc-850 text-slate-700 dark:text-zinc-350 cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 text-xs font-bold bg-zinc-900 text-zinc-50 dark:bg-zinc-100 dark:text-zinc-900 rounded-xl cursor-pointer"
            >
              Save Configuration
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
