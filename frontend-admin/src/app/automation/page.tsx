"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ArrowLeft, RefreshCw, CheckCircle, ShieldAlert } from "lucide-react";
import MonitorCards from "@/components/automation/MonitorCards";
import ScheduleTable from "@/components/automation/ScheduleTable";
import ScheduleModal from "@/components/automation/ScheduleModal";
import JobLogsDrawer from "@/components/automation/JobLogsDrawer";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

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

interface JobLog {
  id: string;
  brand_name: string;
  action: string;
  status: string;
  message: string | null;
  execution_time: number | null;
  created_at: string;
}

export default function AutomationDashboard() {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [logs, setLogs] = useState<JobLog[]>([]);
  const [metrics, setMetrics] = useState({
    uptime_seconds: 0,
    total_runs: 0,
    successes: 0,
    failures: 0,
    retries: 0,
    success_rate: 100,
    failure_rate: 0,
    avg_runtime_seconds: 0,
    longest_runtime_seconds: 0,
    queue_size: 0,
    active_workers: 0,
    worker_utilization: 0
  });

  // Modal & Drawer State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [scheduleToEdit, setScheduleToEdit] = useState<Schedule | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [selectedLog, setSelectedLog] = useState<JobLog | null>(null);
  
  // Loading & SSE logs feed
  const [loading, setLoading] = useState(false);
  const [sseStatus, setSseStatus] = useState("Connecting...");

  useEffect(() => {
    // Dark mode check
    const storedTheme = localStorage.getItem("theme");
    const systemPrefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    if (storedTheme === "dark" || (!storedTheme && systemPrefersDark)) {
      document.documentElement.classList.add("dark");
    }

    fetchBrands();
    loadAllData(); // eslint-disable-line react-hooks/exhaustive-deps

    // Setup SSE live stream listener
    const eventSource = new EventSource(`${BACKEND_URL}/api/v1/scheduler/stream`);
    
    eventSource.onopen = () => setSseStatus("Live Broadcast Active");
    eventSource.onerror = () => setSseStatus("Reconnecting...");
    
    eventSource.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        console.log("SSE Event Received:", payload);
        // Refresh statuses, logs on new runs
        loadAllData();
      } catch (err) {
        console.error("Error parsing SSE data:", err);
      }
    };

    return () => eventSource.close();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchSchedules(),
        fetchMetrics(),
        fetchLogs()
      ]);
    } catch (e) {
      console.error("Error fetching automation data:", e);
    } finally {
      setLoading(false);
    }
  };

  const fetchBrands = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/brands`);
      const data = await res.json();
      if (res.ok && data.success) setBrands(data.data || []);
    } catch (err) {
      console.error("Failed to load brands:", err);
    }
  };

  const fetchSchedules = async () => {
    const res = await fetch(`${BACKEND_URL}/api/v1/schedules`);
    const data = await res.json();
    if (res.ok && data.success) setSchedules(data.data || []);
  };

  const fetchMetrics = async () => {
    const res = await fetch(`${BACKEND_URL}/api/v1/scheduler/status`);
    const data = await res.json();
    if (res.ok && data.success) setMetrics(data.data);
  };

  const fetchLogs = async () => {
    const res = await fetch(`${BACKEND_URL}/api/v1/scheduler/logs`);
    const data = await res.json();
    if (res.ok && data.success) setLogs(data.data || []);
  };

  const handleRunNow = async (id: string) => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/schedules/${id}/run`, { method: "POST" });
      const data = await res.json();
      if (res.ok && data.success) loadAllData();
    } catch (e) {
      console.error("Failed to trigger run now:", e);
    }
  };

  const handleToggleStatus = async (id: string, currentlyEnabled: boolean) => {
    const endpoint = currentlyEnabled ? "pause" : "resume";
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/schedules/${id}/${endpoint}`, { method: "POST" });
      const data = await res.json();
      if (res.ok && data.success) loadAllData();
    } catch (e) {
      console.error("Failed to toggle schedule status:", e);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this automated schedule?")) return;
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/schedules/${id}`, { method: "DELETE" });
      const data = await res.json();
      if (res.ok && data.success) loadAllData();
    } catch (e) {
      console.error("Failed to delete schedule:", e);
    }
  };

  const handleSaveSchedule = async (payload: Partial<Schedule>) => {
    try {
      const isEdit = !!payload.id;
      const url = isEdit ? `${BACKEND_URL}/api/v1/schedules/${payload.id}` : `${BACKEND_URL}/api/v1/schedules`;
      const method = isEdit ? "PUT" : "POST";
      
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setIsModalOpen(false);
        loadAllData();
      } else {
        let errMsg = "Failed to save schedule.";
        if (data.details && data.details.errors && Array.isArray(data.details.errors)) {
          errMsg = data.details.errors.join("\n");
        } else if (data.details && data.details.error) {
          errMsg = data.details.error;
        } else if (data.message) {
          errMsg = data.message;
        } else if (data.detail) {
          errMsg = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
        }
        alert(errMsg);
      }
    } catch (e) {
      console.error("Failed to save schedule:", e);
      alert("A network or connection error occurred while saving the schedule.");
    }
  };

  const handleDuplicate = (schedule: Schedule) => {
    const dupe = {
      ...schedule,
      id: "",
      schedule_name: `${schedule.schedule_name} - Copy`
    };
    setScheduleToEdit(dupe);
    setIsModalOpen(true);
  };

  const openLogDetails = (log: JobLog) => {
    setSelectedLog(log);
    setIsDrawerOpen(true);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-zinc-950 dark:text-zinc-50 transition-colors duration-300 flex flex-col font-sans relative">
      {/* Background Decorative Grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:14px_24px] pointer-events-none" />

      {/* Navigation Header */}
      <header className="sticky top-0 z-40 border-b border-slate-200/80 dark:border-zinc-800/80 bg-white/70 dark:bg-zinc-950/70 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="p-2 rounded-lg border border-slate-200 dark:border-zinc-800 hover:bg-slate-100 dark:hover:bg-zinc-900 transition-colors">
              <ArrowLeft className="h-4 w-4" />
            </Link>
            <span className="font-bold text-base tracking-tight select-none">Automation Engine</span>
          </div>

          <div className="flex items-center gap-4.5 text-xs font-semibold">
            <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full border ${
              sseStatus.includes("Active") 
                ? "bg-emerald-50 dark:bg-emerald-950/10 text-emerald-600 dark:text-emerald-450 border-emerald-100 dark:border-emerald-900/20" 
                : "bg-amber-50 dark:bg-amber-950/10 text-amber-600 dark:text-amber-450 border-amber-100 dark:border-amber-900/20"
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full ${sseStatus.includes("Active") ? "bg-emerald-500 animate-pulse" : "bg-amber-500"}`} />
              {sseStatus}
            </span>
            <button
              onClick={loadAllData}
              disabled={loading}
              className="inline-flex items-center gap-1.5 px-4 py-2 border border-slate-200 dark:border-zinc-800 hover:bg-slate-100 dark:hover:bg-zinc-900 rounded-lg cursor-pointer transition-colors"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
              Sync Dashboard
            </button>
          </div>
        </div>
      </header>

      {/* Main dashboard content */}
      <main className="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 relative z-10 space-y-10">
        <MonitorCards metrics={metrics} />

        {/* Schedule grid header */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-extrabold text-slate-900 dark:text-zinc-55">Active Crawler Schedules</h2>
              <p className="text-[11px] text-slate-500 dark:text-zinc-400 font-medium">Manage automated background jobs, concurrency groups, and cron execution patterns.</p>
            </div>
            <button
              onClick={() => { setScheduleToEdit(null); setIsModalOpen(true); }}
              className="inline-flex items-center justify-center text-xs font-bold bg-zinc-900 hover:bg-zinc-800 text-zinc-50 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200 px-4 py-2.5 rounded-xl shadow-md transition-colors cursor-pointer"
            >
              Create Schedule
            </button>
          </div>

          <ScheduleTable
            schedules={schedules}
            onRunNow={handleRunNow}
            onToggleStatus={handleToggleStatus}
            onEdit={(s) => { setScheduleToEdit(s); setIsModalOpen(true); }}
            onDelete={handleDelete}
            onDuplicate={handleDuplicate}
          />
        </div>

        {/* History Action Logs feed */}
        <div className="space-y-5">
          <h2 className="text-lg font-extrabold text-slate-900 dark:text-zinc-55">Recent Automation Activity Logs</h2>
          <div className="bg-white dark:bg-zinc-900 border border-slate-200/80 dark:border-zinc-800/80 rounded-2xl p-5 shadow-sm space-y-3 max-h-[300px] overflow-y-auto">
            {logs.length === 0 ? (
              <p className="text-xs text-slate-400 dark:text-zinc-500 text-center py-6">No event actions logged yet.</p>
            ) : (
              logs.map((log: JobLog) => (
                <div 
                  key={log.id} 
                  onClick={() => openLogDetails(log)}
                  className="flex items-center justify-between p-3 border border-slate-100 dark:border-zinc-850 hover:bg-slate-50/50 dark:hover:bg-zinc-950/40 rounded-xl transition-colors cursor-pointer text-xs font-semibold"
                >
                  <div className="flex items-center gap-3">
                    {log.status === "SUCCESS" ? (
                      <CheckCircle className="h-4.5 w-4.5 text-emerald-500" />
                    ) : (
                      <ShieldAlert className="h-4.5 w-4.5 text-rose-500" />
                    )}
                    <div>
                      <span className="font-bold text-slate-900 dark:text-zinc-50">{log.brand_name}</span>
                      <span className="text-[10px] text-slate-400 dark:text-zinc-500 ml-2 font-medium">({log.action})</span>
                      <p className="text-[10px] text-slate-400 dark:text-zinc-550 mt-0.5 font-medium">{log.message}</p>
                    </div>
                  </div>
                  <div className="text-[10px] text-slate-400 dark:text-zinc-500 font-medium">
                    {new Date(log.created_at).toLocaleString("en-IN", { hour12: false })}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </main>

      <ScheduleModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        brands={brands}
        scheduleToEdit={scheduleToEdit}
        onSave={handleSaveSchedule}
      />

      <JobLogsDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        log={selectedLog}
      />
    </div>
  );
}
