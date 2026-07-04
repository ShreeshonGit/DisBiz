import React, { useState, useEffect } from "react";
import { Award, Users, Cpu, Clock, BarChart2, ShieldAlert, Sparkles, Network } from "lucide-react";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

interface SummaryData {
  total_brands: number;
  active_brands: number;
  total_dealers: number;
  dealers_added_today: number;
  successful_scrapes: number;
  failed_scrapes: number;
  success_rate: number;
  avg_scrape_duration: number;
  jobs_today: number;
  jobs_this_week: number;
  jobs_this_month: number;
  scheduler_uptime: number;
  worker_uptime: number;
}

interface PerformanceData {
  database_latency_ms: number;
  queue_delay_seconds: number;
  avg_scraper_runtime_seconds: number;
  avg_api_latency_ms: number;
  p95_api_latency_ms: number;
}

interface ChartData {
  scrapes_per_day: { date: string; successful: number; failed: number }[];
  dealers_over_time: { date: string; count: number }[];
  failure_trend: { error: string; count: number }[];
  brand_wise_dealers: { brand_name: string; dealer_count: number }[];
  scheduler_activity: { hour: string; job_count: number }[];
}

export default function DashboardAnalytics() {
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [performance, setPerformance] = useState<PerformanceData | null>(null);
  const [charts, setCharts] = useState<ChartData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchAllData = async () => {
    try {
      const [sumRes, perfRes, chartRes] = await Promise.all([
        fetch(`${BACKEND_URL}/api/v1/analytics/summary`),
        fetch(`${BACKEND_URL}/api/v1/performance/metrics`),
        fetch(`${BACKEND_URL}/api/v1/analytics/charts`)
      ]);
      
      if (sumRes.ok) setSummary(await sumRes.json());
      if (perfRes.ok) setPerformance(await perfRes.json());
      if (chartRes.ok) setCharts(await chartRes.json());
    } catch (e) {
      console.error("Failed to load analytics metrics", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 15000);
    return () => clearInterval(interval);
  }, []);

  if (loading || !summary) {
    return <div className="text-center py-12 text-slate-400 dark:text-zinc-600 font-sans">Compiling data engine...</div>;
  }

  // Format uptime to readable string
  const formatUptime = (seconds: number) => {
    const d = Math.floor(seconds / (3600 * 24));
    const h = Math.floor((seconds % (3600 * 24)) / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    if (d > 0) return `${d}d ${h}h ${m}m`;
    if (h > 0) return `${h}h ${m}m`;
    return `${m}m`;
  };

  // Find max values for CSS relative charts scaling
  const maxDealerCount = charts?.brand_wise_dealers?.length 
    ? Math.max(...charts.brand_wise_dealers.map(b => b.dealer_count), 1) 
    : 1;

  const maxScrapesCount = charts?.scrapes_per_day?.length
    ? Math.max(...charts.scrapes_per_day.map(s => s.successful + s.failed), 1)
    : 1;

  return (
    <div className="space-y-8 animate-fade-in font-sans">
      {/* Header */}
      <div className="border-b border-slate-200 dark:border-zinc-800 pb-5">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-zinc-50 mb-1">
          Analytics Dashboard
        </h1>
        <p className="text-sm text-slate-500 dark:text-zinc-400">
          Telemetric summaries, scraped locations count, failure trends, and system latencies.
        </p>
      </div>

      {/* Summary Matrix Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-5 hover:shadow-xs transition-shadow">
          <div className="flex justify-between items-start mb-4">
            <span className="text-xs font-semibold text-slate-550 dark:text-zinc-500 uppercase tracking-wider">
              Total Monitored Brands
            </span>
            <Award className="h-5 w-5 text-indigo-500" />
          </div>
          <div className="flex items-baseline gap-2.5">
            <span className="text-3xl font-bold text-slate-900 dark:text-zinc-50">{summary.total_brands}</span>
            <span className="text-xs text-slate-400 dark:text-zinc-550">({summary.active_brands} active)</span>
          </div>
        </div>

        <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-5 hover:shadow-xs transition-shadow">
          <div className="flex justify-between items-start mb-4">
            <span className="text-xs font-semibold text-slate-550 dark:text-zinc-500 uppercase tracking-wider">
              Total Dealer Locations
            </span>
            <Users className="h-5 w-5 text-sky-500" />
          </div>
          <div className="flex items-baseline gap-2.5">
            <span className="text-3xl font-bold text-slate-900 dark:text-zinc-50">{summary.total_dealers}</span>
            <span className="text-xs text-emerald-600 dark:text-emerald-500 font-semibold flex items-center gap-0.5">
              +{summary.dealers_added_today} today
            </span>
          </div>
        </div>

        <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-5 hover:shadow-xs transition-shadow">
          <div className="flex justify-between items-start mb-4">
            <span className="text-xs font-semibold text-slate-550 dark:text-zinc-500 uppercase tracking-wider">
              Scraper Success Rate
            </span>
            <Cpu className="h-5 w-5 text-emerald-500" />
          </div>
          <div className="flex items-baseline gap-2.5">
            <span className="text-3xl font-bold text-slate-900 dark:text-zinc-50">{summary.success_rate}%</span>
            <span className="text-xs text-slate-400 dark:text-zinc-550">({summary.successful_scrapes}/{summary.successful_scrapes + summary.failed_scrapes} runs)</span>
          </div>
        </div>

        <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-5 hover:shadow-xs transition-shadow">
          <div className="flex justify-between items-start mb-4">
            <span className="text-xs font-semibold text-slate-550 dark:text-zinc-500 uppercase tracking-wider">
              Scheduler Uptime
            </span>
            <Clock className="h-5 w-5 text-amber-500" />
          </div>
          <div className="flex items-baseline gap-2.5">
            <span className="text-3xl font-bold text-slate-900 dark:text-zinc-50">{formatUptime(summary.scheduler_uptime)}</span>
            <span className="text-xs text-emerald-600 dark:text-emerald-500 font-semibold">Active</span>
          </div>
        </div>
      </div>

      {/* Latency / Performance Metrics (Phase 6) */}
      <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-2xl p-6 shadow-xs">
        <h3 className="text-md font-semibold text-slate-900 dark:text-zinc-50 mb-4 flex items-center gap-2">
          <Network className="h-4.5 w-4.5 text-indigo-500" />
          Performance Latency Metrics
        </h3>
        
        {performance ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            <div className="bg-slate-50 dark:bg-zinc-950 p-4 rounded-xl border border-slate-150 dark:border-zinc-850">
              <p className="text-xs text-slate-450 dark:text-zinc-500 uppercase tracking-wider font-semibold mb-1">API Avg Response</p>
              <p className="text-2xl font-bold text-slate-850 dark:text-zinc-150">{performance.avg_api_latency_ms} ms</p>
              <p className="text-[10px] text-slate-400 dark:text-zinc-550 mt-1">p95: {performance.p95_api_latency_ms} ms</p>
            </div>
            
            <div className="bg-slate-50 dark:bg-zinc-950 p-4 rounded-xl border border-slate-150 dark:border-zinc-850">
              <p className="text-xs text-slate-450 dark:text-zinc-500 uppercase tracking-wider font-semibold mb-1">Database Queries</p>
              <p className="text-2xl font-bold text-slate-850 dark:text-zinc-150">{performance.database_latency_ms} ms</p>
              <p className="text-[10px] text-slate-400 dark:text-zinc-550 mt-1">Supabase API latency</p>
            </div>
            
            <div className="bg-slate-50 dark:bg-zinc-950 p-4 rounded-xl border border-slate-150 dark:border-zinc-850">
              <p className="text-xs text-slate-450 dark:text-zinc-500 uppercase tracking-wider font-semibold mb-1">Queue Dispatch Delay</p>
              <p className="text-2xl font-bold text-slate-850 dark:text-zinc-150">{performance.queue_delay_seconds} s</p>
              <p className="text-[10px] text-slate-400 dark:text-zinc-550 mt-1">Time enqueued in worker</p>
            </div>
            
            <div className="bg-slate-50 dark:bg-zinc-950 p-4 rounded-xl border border-slate-150 dark:border-zinc-850">
              <p className="text-xs text-slate-450 dark:text-zinc-500 uppercase tracking-wider font-semibold mb-1">Avg Scraper Duration</p>
              <p className="text-2xl font-bold text-slate-850 dark:text-zinc-150">{performance.avg_scraper_runtime_seconds} s</p>
              <p className="text-[10px] text-slate-400 dark:text-zinc-550 mt-1">Completed scrapers run</p>
            </div>
          </div>
        ) : (
          <p className="text-sm text-slate-500">Latency timings not yet populated.</p>
        )}
      </div>

      {/* Visual Aggregates / CSS Charts Display */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Brand wise distribution */}
        <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-2xl p-6 shadow-xs">
          <h3 className="text-md font-semibold text-slate-900 dark:text-zinc-50 mb-5 flex items-center gap-2">
            <BarChart2 className="h-4.5 w-4.5 text-indigo-500" />
            Dealers Discovered by Brand
          </h3>
          
          <div className="space-y-4">
            {charts?.brand_wise_dealers?.length === 0 ? (
              <p className="text-sm text-slate-500 py-8 text-center">No brand dealer mappings recorded.</p>
            ) : (
              charts?.brand_wise_dealers?.map((b, idx) => {
                const widthPercent = Math.max(10, Math.min(100, (b.dealer_count / maxDealerCount) * 100));
                return (
                  <div key={idx} className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs font-semibold text-slate-700 dark:text-zinc-350">
                      <span>{b.brand_name}</span>
                      <span>{b.dealer_count} locations</span>
                    </div>
                    <div className="h-3 w-full bg-slate-100 dark:bg-zinc-950 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-indigo-500 to-sky-500 rounded-full transition-all duration-500"
                        style={{ width: `${widthPercent}%` }}
                      />
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Daily Scrapes status bar chart */}
        <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-2xl p-6 shadow-xs">
          <h3 className="text-md font-semibold text-slate-900 dark:text-zinc-50 mb-5 flex items-center gap-2">
            <Sparkles className="h-4.5 w-4.5 text-emerald-500" />
            Scraper Run History (Last 7 Days)
          </h3>
          
          <div className="h-48 flex items-end justify-between gap-2 border-b border-slate-150 dark:border-zinc-800 pb-3">
            {charts?.scrapes_per_day?.length === 0 ? (
              <p className="text-sm text-slate-550 w-full text-center py-16">No recent scraping executions.</p>
            ) : (
              charts?.scrapes_per_day?.map((s, idx) => {
                const total = s.successful + s.failed;
                const totalHeight = Math.max(8, Math.min(100, (total / maxScrapesCount) * 100));
                const succPct = total > 0 ? (s.successful / total) * 100 : 0;
                
                return (
                  <div key={idx} className="flex-1 flex flex-col items-center group relative">
                    {/* Tooltip */}
                    <div className="absolute bottom-full mb-2 bg-slate-900 text-white text-[10px] px-2 py-1 rounded hidden group-hover:block whitespace-nowrap shadow-md z-30">
                      <span>Succ: {s.successful} / Fail: {s.failed}</span>
                    </div>
                    
                    <div
                      className="w-8 rounded-t-sm overflow-hidden flex flex-col justify-end"
                      style={{ height: `${totalHeight}%`, minHeight: "4px" }}
                    >
                      <div className="bg-red-500 w-full" style={{ height: `${100 - succPct}%` }} />
                      <div className="bg-emerald-500 w-full" style={{ height: `${succPct}%` }} />
                    </div>
                    <span className="text-[9px] text-slate-400 dark:text-zinc-550 mt-1.5 leading-none">
                      {s.date.slice(5)}
                    </span>
                  </div>
                );
              })
            )}
          </div>
          
          <div className="flex items-center gap-4 justify-center mt-4 text-xs font-semibold text-slate-500">
            <span className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 bg-emerald-500 rounded-full" />
              Completed Runs
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 bg-red-500 rounded-full" />
              Failed / Blocked Runs
            </span>
          </div>
        </div>
      </div>

      {/* Failure clustering details */}
      {charts?.failure_trend && charts.failure_trend.length > 0 && (
        <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-2xl p-6 shadow-xs">
          <h3 className="text-md font-semibold text-slate-900 dark:text-zinc-50 mb-4 flex items-center gap-2">
            <ShieldAlert className="h-4.5 w-4.5 text-red-500" />
            Top Error Categories
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {charts.failure_trend.map((err, idx) => (
              <div key={idx} className="bg-slate-50 dark:bg-zinc-950 px-4 py-3 rounded-lg border border-slate-150 dark:border-zinc-850 flex justify-between items-center text-xs">
                <span className="font-mono text-slate-700 dark:text-zinc-350 break-all">{err.error}</span>
                <span className="bg-red-100 text-red-750 dark:bg-red-500/10 dark:text-red-400 font-bold px-2 py-0.5 rounded ml-2 shrink-0">
                  {err.count} times
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
