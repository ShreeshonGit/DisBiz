import React, { useState, useEffect } from "react";
import { Cpu, HardDrive, Play, ListOrdered, Activity } from "lucide-react";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

interface MonitoringData {
  live_workers: string[];
  active_workers_count: number;
  queue_size: number;
  running_jobs: number;
  waiting_jobs: number;
  failed_jobs: number;
  retry_count: number;
  api_stats: {
    avg_latency_ms: number;
    p95_latency_ms: number;
    total_requests: number;
  };
  system_stats: {
    cpu_usage_percent: number;
    memory_usage_percent: number;
    memory_used_mb: number;
    memory_total_mb: number;
  };
}

interface HealthStatus {
  status: string;
  components?: {
    database_health?: string;
    supabase_health?: string;
    scheduler_health?: string;
    worker_health?: string;
  };
}

export default function SystemMonitoring() {
  const [data, setData] = useState<MonitoringData | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchStats = async () => {
    try {
      const [statsRes, healthRes] = await Promise.all([
        fetch(`${BACKEND_URL}/api/v1/monitoring/status`),
        fetch(`${BACKEND_URL}/api/v1/health`)
      ]);
      if (statsRes.ok) setData(await statsRes.json());
      if (healthRes.ok) setHealth(await healthRes.json());
    } catch (e) {
      console.error("Failed to load monitoring stats", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    // Poll monitoring data every 5 seconds for real-time dashboard monitoring
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading || !data) {
    return <div className="text-center py-12 text-slate-400 dark:text-zinc-600 font-sans">Querying hardware diagnostics...</div>;
  }

  return (
    <div className="space-y-6 font-sans">
      {/* Header */}
      <div className="border-b border-slate-200 dark:border-zinc-800 pb-5">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-zinc-50 mb-1">
          System Monitoring
        </h1>
        <p className="text-sm text-slate-500 dark:text-zinc-400">
          Hardware metrics, system liveness checks, and active queue telemetry.
        </p>
      </div>

      {/* Health Checks Indicators (Phase 5) */}
      <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-5 shadow-xs">
        <h3 className="text-sm font-semibold text-slate-800 dark:text-zinc-200 mb-4 flex items-center gap-1.5">
          <Activity className="h-4 w-4 text-emerald-500" />
          Component Liveness & Readiness Checks
        </h3>
        
        {health ? (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-slate-50 dark:bg-zinc-950 px-4 py-3 rounded-lg border border-slate-150 dark:border-zinc-850 flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500">Platform Status</span>
              <span className={`text-xs font-bold uppercase ${health.status === "healthy" ? "text-emerald-500" : "text-rose-500"}`}>
                {health.status}
              </span>
            </div>
            <div className="bg-slate-50 dark:bg-zinc-950 px-4 py-3 rounded-lg border border-slate-150 dark:border-zinc-850 flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500">Database</span>
              <span className={`text-xs font-bold uppercase ${health.components?.database_health === "ok" ? "text-emerald-500" : "text-rose-500"}`}>
                {health.components?.database_health === "ok" ? "CONNECTED" : "DISCONNECTED"}
              </span>
            </div>
            <div className="bg-slate-50 dark:bg-zinc-950 px-4 py-3 rounded-lg border border-slate-150 dark:border-zinc-850 flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500">Scheduler</span>
              <span className={`text-xs font-bold uppercase ${health.components?.scheduler_health === "ok" ? "text-emerald-500" : "text-rose-500"}`}>
                {health.components?.scheduler_health === "ok" ? "ACTIVE" : "INACTIVE"}
              </span>
            </div>
            <div className="bg-slate-50 dark:bg-zinc-950 px-4 py-3 rounded-lg border border-slate-150 dark:border-zinc-850 flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500">Workers Pool</span>
              <span className={`text-xs font-bold uppercase ${health.components?.worker_health === "ok" ? "text-emerald-500" : "text-rose-500"}`}>
                {health.components?.worker_health === "ok" ? "READY" : "OFFLINE"}
              </span>
            </div>
          </div>
        ) : (
          <p className="text-xs text-slate-500">Subsystem status unavailable.</p>
        )}
      </div>

      {/* Hardware Utilization row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* CPU Util */}
        <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-5 shadow-xs">
          <div className="flex justify-between items-start mb-4">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">CPU Utilization</span>
            <Cpu className="h-4.5 w-4.5 text-indigo-500" />
          </div>
          <div className="space-y-3">
            <div className="flex items-baseline justify-between">
              <span className="text-3xl font-bold text-slate-800 dark:text-zinc-150">{data.system_stats.cpu_usage_percent}%</span>
              <span className="text-xs text-slate-400 dark:text-zinc-550">Processing Load</span>
            </div>
            <div className="h-2.5 w-full bg-slate-100 dark:bg-zinc-950 rounded-full overflow-hidden">
              <div
                className="h-full bg-indigo-500 transition-all duration-300"
                style={{ width: `${data.system_stats.cpu_usage_percent}%` }}
              />
            </div>
          </div>
        </div>

        {/* RAM Util */}
        <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-5 shadow-xs">
          <div className="flex justify-between items-start mb-4">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Memory Allocation</span>
            <HardDrive className="h-4.5 w-4.5 text-sky-500" />
          </div>
          <div className="space-y-3">
            <div className="flex items-baseline justify-between">
              <span className="text-3xl font-bold text-slate-800 dark:text-zinc-150">{data.system_stats.memory_usage_percent}%</span>
              <span className="text-xs text-slate-400 dark:text-zinc-550">
                {Math.round(data.system_stats.memory_used_mb)} MB / {Math.round(data.system_stats.memory_total_mb)} MB
              </span>
            </div>
            <div className="h-2.5 w-full bg-slate-100 dark:bg-zinc-950 rounded-full overflow-hidden">
              <div
                className="h-full bg-sky-500 transition-all duration-300"
                style={{ width: `${data.system_stats.memory_usage_percent}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Queue Monitoring & Workers list */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Queue depths */}
        <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-5 shadow-xs md:col-span-2 space-y-4">
          <h3 className="text-sm font-semibold text-slate-800 dark:text-zinc-200 flex items-center gap-1.5">
            <ListOrdered className="h-4.5 w-4.5 text-indigo-500" />
            Queue Depth Telemetry
          </h3>
          
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="bg-slate-50 dark:bg-zinc-950 p-3 rounded-lg border border-slate-150 dark:border-zinc-850">
              <p className="text-[10px] text-slate-450 dark:text-zinc-500 uppercase font-semibold mb-0.5">Enqueued / Waiting</p>
              <p className="text-xl font-bold text-slate-750 dark:text-zinc-200">{data.queue_size}</p>
            </div>
            
            <div className="bg-slate-50 dark:bg-zinc-950 p-3 rounded-lg border border-slate-150 dark:border-zinc-850">
              <p className="text-[10px] text-slate-450 dark:text-zinc-500 uppercase font-semibold mb-0.5">Active / Running</p>
              <p className="text-xl font-bold text-indigo-600 dark:text-indigo-400">{data.running_jobs}</p>
            </div>
            
            <div className="bg-slate-50 dark:bg-zinc-950 p-3 rounded-lg border border-slate-150 dark:border-zinc-850">
              <p className="text-[10px] text-slate-450 dark:text-zinc-500 uppercase font-semibold mb-0.5">Failed / Retrying</p>
              <p className="text-xl font-bold text-rose-650 dark:text-rose-400">{data.failed_jobs}</p>
            </div>
          </div>
          
          <div className="flex justify-between items-center text-xs text-slate-500 border-t border-slate-100 dark:border-zinc-800 pt-3">
            <span>Cumulative job retry frequencies:</span>
            <span className="font-bold text-slate-700 dark:text-zinc-350">{data.retry_count} total retries</span>
          </div>
        </div>

        {/* Live Workers list */}
        <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-5 shadow-xs space-y-4">
          <h3 className="text-sm font-semibold text-slate-800 dark:text-zinc-200 flex items-center gap-1.5">
            <Play className="h-4.5 w-4.5 text-sky-500 fill-current" />
            Active Thread Workers
          </h3>
          
          <div className="space-y-2 max-h-[140px] overflow-y-auto">
            {data.live_workers.length === 0 ? (
              <p className="text-xs text-slate-500 text-center py-6">No scraper jobs currently running in background thread pool.</p>
            ) : (
              data.live_workers.map((worker, idx) => (
                <div key={idx} className="flex items-center gap-2 bg-slate-50 dark:bg-zinc-950 p-2 border border-slate-100 dark:border-zinc-850 rounded text-[11px] font-mono text-slate-700 dark:text-zinc-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-ping shrink-0" />
                  <span className="truncate">{worker}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
