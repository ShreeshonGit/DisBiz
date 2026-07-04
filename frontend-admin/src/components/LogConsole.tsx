import React, { useState, useEffect, useRef } from "react";
import { Search, Download, Play, Pause, AlertTriangle, List, FileText } from "lucide-react";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

interface LogRecord {
  timestamp: string;
  level: string;
  logger: string;
  message: string;
  traceback?: string;
}

interface ErrorGroup {
  message: string;
  count: number;
  last_occurrence: string;
  examples: LogRecord[];
}

export default function LogConsole() {
  const [activeSubTab, setActiveSubTab] = useState<"all" | "errors">("all");
  const [logs, setLogs] = useState<LogRecord[]>([]);
  const [errorGroups, setErrorGroups] = useState<ErrorGroup[]>([]);
  const [level, setLevel] = useState<string>("");
  const [search, setSearch] = useState<string>("");
  const [isStreaming, setIsStreaming] = useState<boolean>(true);
  const eventSourceRef = useRef<EventSource | null>(null);

  const fetchLogs = async () => {
    try {
      const qParams = new URLSearchParams();
      if (level) qParams.append("level", level);
      if (search) qParams.append("query", search);
      qParams.append("limit", "150");
      const res = await fetch(`${BACKEND_URL}/api/v1/logs?${qParams.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setLogs(data);
      }
    } catch (e) {
      console.error("Failed to fetch logs", e);
    }
  };

  const fetchErrorGroups = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/logs/errors`);
      if (res.ok) {
        const data = await res.json();
        setErrorGroups(data);
      }
    } catch (e) {
      console.error("Failed to fetch error groups", e);
    }
  };

  // SSE Log Streaming
  useEffect(() => {
    if (isStreaming && activeSubTab === "all") {
      const source = new EventSource(`${BACKEND_URL}/api/v1/logs/stream`);
      eventSourceRef.current = source;

      source.onmessage = (event) => {
        try {
          const newLog = JSON.parse(event.data);
          setLogs((prev) => {
            const updated = [...prev, newLog];
            return updated.slice(-150); // limit to last 150 items
          });
        } catch (e) {
          console.error("Error parsing stream message", e);
        }
      };

      source.onerror = () => {
        console.error("SSE stream connection error");
        source.close();
      };

      return () => {
        source.close();
      };
    } else {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    }
  }, [isStreaming, activeSubTab]);

  useEffect(() => {
    if (activeSubTab === "all") {
      fetchLogs();
    } else {
      fetchErrorGroups();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [level, search, activeSubTab]);

  const handleDownload = () => {
    const qParams = new URLSearchParams();
    if (level) qParams.append("level", level);
    if (search) qParams.append("query", search);
    window.open(`${BACKEND_URL}/api/v1/logs/download?${qParams.toString()}`);
  };

  const handleExportCSV = () => {
    const qParams = new URLSearchParams();
    if (level) qParams.append("level", level);
    if (search) qParams.append("query", search);
    window.open(`${BACKEND_URL}/api/v1/logs/export?${qParams.toString()}`);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-zinc-800 pb-5">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-zinc-50 mb-1">
            Execution logs
          </h1>
          <p className="text-sm text-slate-500 dark:text-zinc-400">
            Real-time execution log parser and exception clustering console.
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveSubTab("all")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold ${
              activeSubTab === "all"
                ? "bg-slate-900 text-white dark:bg-zinc-100 dark:text-zinc-950"
                : "border border-slate-250 dark:border-zinc-800 text-slate-700 dark:text-zinc-300"
            }`}
          >
            <List className="h-3.5 w-3.5" />
            All Logs
          </button>
          <button
            onClick={() => setActiveSubTab("errors")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold ${
              activeSubTab === "errors"
                ? "bg-slate-900 text-white dark:bg-zinc-100 dark:text-zinc-950"
                : "border border-slate-250 dark:border-zinc-800 text-slate-700 dark:text-zinc-300"
            }`}
          >
            <AlertTriangle className="h-3.5 w-3.5" />
            Grouped Errors
          </button>
        </div>
      </div>

      {activeSubTab === "all" ? (
        <div className="space-y-4">
          {/* Controls Bar */}
          <div className="flex flex-wrap items-center justify-between gap-4 bg-white dark:bg-zinc-900 p-4 border border-slate-200 dark:border-zinc-800 rounded-xl shadow-xs">
            <div className="flex flex-wrap items-center gap-3">
              {/* Search */}
              <div className="relative w-64">
                <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400 dark:text-zinc-500" />
                <input
                  type="text"
                  placeholder="Filter logs by keywords..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-9 pr-4 py-2 w-full bg-slate-50 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 rounded-lg text-sm"
                />
              </div>

              {/* Level Filter */}
              <select
                value={level}
                onChange={(e) => setLevel(e.target.value)}
                className="bg-slate-50 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 rounded-lg py-2 px-3 text-sm"
              >
                <option value="">All Levels</option>
                <option value="INFO">INFO</option>
                <option value="WARNING">WARNING</option>
                <option value="ERROR">ERROR</option>
                <option value="CRITICAL">CRITICAL</option>
              </select>

              {/* Streaming Toggle */}
              <button
                onClick={() => setIsStreaming(!isStreaming)}
                className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold border ${
                  isStreaming
                    ? "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/20"
                    : "bg-slate-50 text-slate-700 border-slate-200 dark:bg-zinc-800 dark:text-zinc-400 dark:border-zinc-700"
                }`}
              >
                {isStreaming ? (
                  <>
                    <Pause className="h-3 w-3 fill-current" />
                    Streaming
                  </>
                ) : (
                  <>
                    <Play className="h-3 w-3 fill-current" />
                    Paused
                  </>
                )}
              </button>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleDownload}
                className="flex items-center gap-1.5 px-3 py-2 bg-slate-50 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 rounded-lg text-xs font-semibold hover:bg-slate-100 dark:hover:bg-zinc-700"
              >
                <Download className="h-3.5 w-3.5" />
                Raw Log
              </button>
              <button
                onClick={handleExportCSV}
                className="flex items-center gap-1.5 px-3 py-2 bg-slate-50 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 rounded-lg text-xs font-semibold hover:bg-slate-100 dark:hover:bg-zinc-700"
              >
                <FileText className="h-3.5 w-3.5" />
                Export CSV
              </button>
            </div>
          </div>

          {/* Console Area */}
          <div className="bg-slate-900 border border-slate-800 dark:bg-black rounded-xl p-5 font-mono text-xs text-slate-350 dark:text-zinc-450 leading-relaxed shadow-inner max-h-[500px] overflow-y-auto space-y-2">
            {logs.length === 0 ? (
              <p className="text-slate-500 text-center py-8 select-none">No matching log records found in memory cache.</p>
            ) : (
              logs.map((log, idx) => {
                let lvlColor = "text-slate-400";
                if (log.level === "WARNING") lvlColor = "text-amber-500";
                if (log.level === "ERROR" || log.level === "CRITICAL") lvlColor = "text-red-500";
                if (log.level === "INFO") lvlColor = "text-sky-400";
                
                return (
                  <div key={idx} className="border-b border-slate-850 dark:border-zinc-900/50 pb-1.5 last:border-0">
                    <span className="text-slate-500 mr-2 select-none">[{log.timestamp.split("T")[1]?.slice(0, 8)}]</span>
                    <span className={`font-semibold uppercase mr-2 select-none ${lvlColor}`}>{log.level}</span>
                    <span className="text-slate-450 dark:text-zinc-500 mr-2 select-none">[{log.logger}]</span>
                    <span className="text-zinc-200 dark:text-zinc-300">{log.message}</span>
                    {log.traceback && (
                      <pre className="bg-red-950/20 text-red-400/90 border-l border-red-500/30 p-3 mt-2 rounded overflow-x-auto leading-normal">
                        {log.traceback}
                      </pre>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      ) : (
        /* Error Groups view */
        <div className="space-y-4">
          {errorGroups.length === 0 ? (
            <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-16 text-center max-w-xl mx-auto shadow-sm">
              <AlertTriangle className="h-10 w-10 text-emerald-500 mx-auto mb-3" />
              <h3 className="font-semibold text-slate-800 dark:text-zinc-200 mb-1">Zero Errors Found</h3>
              <p className="text-sm text-slate-500 dark:text-zinc-500">The application is running cleanly without logged exceptions.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {errorGroups.map((g, idx) => (
                <div key={idx} className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-5 hover:shadow-xs transition-shadow">
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div className="space-y-1">
                      <p className="font-mono text-sm font-semibold text-red-650 dark:text-red-400 break-all">{g.message}</p>
                      <p className="text-xs text-slate-400 dark:text-zinc-500">Last occurrence: {new Date(g.last_occurrence).toLocaleString()}</p>
                    </div>
                    <span className="bg-red-50 text-red-600 dark:bg-red-500/10 dark:text-red-400 border border-red-100 dark:border-red-500/20 px-2.5 py-1 rounded-full text-xs font-bold whitespace-nowrap">
                      {g.count} occurrences
                    </span>
                  </div>

                  <div className="mt-4">
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Example Traceback Snippet:</p>
                    {g.examples[0]?.traceback ? (
                      <pre className="bg-slate-900 dark:bg-black text-red-400/90 border-l-2 border-red-500 p-4 rounded-lg font-mono text-[10px] leading-relaxed overflow-x-auto">
                        {g.examples[0].traceback}
                      </pre>
                    ) : (
                      <div className="bg-slate-900 dark:bg-black text-slate-300 p-3 rounded-lg font-mono text-[11px] border border-slate-800">
                        {g.examples[0]?.message}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
