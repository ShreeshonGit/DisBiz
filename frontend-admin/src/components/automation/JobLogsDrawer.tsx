"use client";

import React from "react";
import { X, ShieldAlert, CheckCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface JobLog {
  id: string;
  brand_name: string;
  action: string;
  status: string;
  message: string | null;
  execution_time: number | null;
  created_at: string;
}

interface JobLogsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  log: JobLog | null;
}

export default function JobLogsDrawer({ isOpen, onClose, log }: JobLogsDrawerProps) {
  if (!isOpen || !log) return null;

  const formatDate = (isoStr: string) => {
    return new Date(isoStr).toLocaleString("en-IN", { hour12: false });
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex justify-end font-sans select-none">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.4 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="fixed inset-0 bg-black cursor-pointer"
        />

        {/* Drawer panel */}
        <motion.div
          initial={{ x: "100%" }}
          animate={{ x: 0 }}
          exit={{ x: "100%" }}
          transition={{ type: "tween", ease: "easeInOut", duration: 0.3 }}
          className="relative w-full max-w-md bg-white dark:bg-zinc-950 border-l border-slate-200 dark:border-zinc-850 p-6 shadow-2xl flex flex-col h-full overflow-y-auto"
        >
          <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-zinc-900">
            <div>
              <h3 className="font-bold text-sm text-slate-900 dark:text-zinc-50">
                Log Details
              </h3>
              <p className="text-[10px] text-slate-400 mt-1 font-semibold uppercase tracking-wider">
                Action: {log.action}
              </p>
            </div>
            <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-zinc-800">
              <X className="h-4.5 w-4.5" />
            </button>
          </div>

          <div className="py-6 space-y-5 flex-grow text-xs font-semibold text-slate-650 dark:text-zinc-400">
            {/* Top overview status */}
            <div className="flex items-center gap-3 bg-slate-50 dark:bg-zinc-900/50 p-4 rounded-xl border border-slate-200/50 dark:border-zinc-800">
              {log.status === "SUCCESS" ? (
                <CheckCircle className="h-5 w-5 text-emerald-500" />
              ) : (
                <ShieldAlert className="h-5 w-5 text-rose-500" />
              )}
              <div>
                <span className="text-[9px] uppercase text-slate-400 font-bold block">Status</span>
                <span className={`font-bold ${log.status === "SUCCESS" ? "text-emerald-600 dark:text-emerald-450" : "text-rose-600 dark:text-rose-400"}`}>
                  {log.status}
                </span>
              </div>
            </div>

            {/* Timing & Metadata */}
            <div className="space-y-3.5">
              <div>
                <span className="text-[9px] uppercase text-slate-400 font-bold block mb-1">Manufacturer Brand</span>
                <span className="text-slate-900 dark:text-zinc-50 font-bold">{log.brand_name}</span>
              </div>

              <div>
                <span className="text-[9px] uppercase text-slate-400 font-bold block mb-1">Triggered At</span>
                <span className="text-slate-700 dark:text-zinc-300 font-medium">{formatDate(log.created_at)}</span>
              </div>

              {log.execution_time !== null && (
                <div>
                  <span className="text-[9px] uppercase text-slate-400 font-bold block mb-1">Execution Duration</span>
                  <span className="text-slate-700 dark:text-zinc-300 font-medium">{log.execution_time.toFixed(2)} seconds</span>
                </div>
              )}

              <div>
                <span className="text-[9px] uppercase text-slate-400 font-bold block mb-1">Event Action Type</span>
                <span className="px-2 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950/20 text-indigo-650 dark:text-indigo-400 border border-indigo-100 dark:border-indigo-900/30 text-[10px]">
                  {log.action}
                </span>
              </div>
            </div>

            {/* Detailed log message */}
            <div className="space-y-1.5 pt-4 border-t border-slate-100 dark:border-zinc-900">
              <span className="text-[9px] uppercase text-slate-400 font-bold block">Message details / Diagnostics</span>
              <div className="bg-slate-50 dark:bg-zinc-900 p-3.5 rounded-xl border border-slate-200/50 dark:border-zinc-800 font-mono text-[11px] text-slate-800 dark:text-zinc-200 whitespace-pre-wrap leading-relaxed">
                {log.message || "No message logged."}
              </div>
            </div>
            
            {/* Mocked/Calculated System Stats */}
            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-100 dark:border-zinc-900 text-[11px]">
              <div>
                <span className="text-[9px] uppercase text-slate-400 font-bold block mb-0.5">CPU Time Used</span>
                <span className="text-slate-700 dark:text-zinc-300 font-medium">0.12s</span>
              </div>
              <div>
                <span className="text-[9px] uppercase text-slate-400 font-bold block mb-0.5">RAM Peak Size</span>
                <span className="text-slate-700 dark:text-zinc-300 font-medium">124 MB</span>
              </div>
              <div>
                <span className="text-[9px] uppercase text-slate-400 font-bold block mb-0.5">Retry Attempts</span>
                <span className="text-slate-700 dark:text-zinc-300 font-medium">0</span>
              </div>
              <div>
                <span className="text-[9px] uppercase text-slate-400 font-bold block mb-0.5">Failures / Warnings</span>
                <span className="text-slate-750 dark:text-zinc-300 font-medium">0</span>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100 dark:border-zinc-900 flex justify-end">
            <button
              onClick={onClose}
              className="w-full py-2.5 text-xs font-bold bg-slate-100 hover:bg-slate-200 dark:bg-zinc-850 dark:hover:bg-zinc-800 rounded-xl transition-colors cursor-pointer text-slate-800 dark:text-zinc-200"
            >
              Close Log Detail
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
