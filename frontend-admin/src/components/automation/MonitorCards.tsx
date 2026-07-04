"use client";

import React from "react";
import { motion } from "framer-motion";
import { Clock, Layers, Cpu, CheckCircle } from "lucide-react";

interface Metrics {
  uptime_seconds: number;
  total_runs: number;
  successes: number;
  failures: number;
  retries: number;
  success_rate: number;
  failure_rate: number;
  avg_runtime_seconds: number;
  longest_runtime_seconds: number;
  queue_size: number;
  active_workers: number;
  worker_utilization: number;
}

interface MonitorCardsProps {
  metrics: Metrics;
}

export default function MonitorCards({ metrics }: MonitorCardsProps) {
  const formatUptime = (sec: number) => {
    const hrs = Math.floor(sec / 3600);
    const mins = Math.floor((sec % 3600) / 60);
    const secs = Math.floor(sec % 60);
    return `${hrs}h ${mins}m ${secs}s`;
  };

  const cards = [
    {
      title: "Scheduler Uptime",
      value: formatUptime(metrics.uptime_seconds || 0),
      icon: Clock,
      color: "text-blue-500 bg-blue-500/10",
      desc: "Engine status: Running"
    },
    {
      title: "Job Queue Depth",
      value: `${metrics.queue_size || 0} Pending`,
      icon: Layers,
      color: "text-indigo-500 bg-indigo-500/10",
      desc: "Priority ordered execution"
    },
    {
      title: "Worker Utilization",
      value: `${metrics.worker_utilization || 0}%`,
      icon: Cpu,
      color: "text-amber-500 bg-amber-500/10",
      desc: `${metrics.active_workers || 0} / 3 concurrent workers active`
    },
    {
      title: "Task Success Rate",
      value: `${metrics.success_rate || 100}%`,
      icon: CheckCircle,
      color: "text-emerald-500 bg-emerald-500/10",
      desc: `Total runs: ${metrics.total_runs || 0}`
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 select-none">
      {cards.map((card, i) => {
        const IconComponent = card.icon;
        return (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: i * 0.05 }}
            className="bg-white dark:bg-zinc-900 border border-slate-200/80 dark:border-zinc-800/85 rounded-2xl p-5 hover:shadow-lg dark:hover:shadow-black/25 transition-all duration-300"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-500 dark:text-zinc-400">{card.title}</span>
              <div className={`p-2 rounded-xl ${card.color}`}>
                <IconComponent className="h-4.5 w-4.5" />
              </div>
            </div>
            <div className="mt-4 space-y-1">
              <h3 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-zinc-50 font-sans tracking-tight">
                {card.value}
              </h3>
              <p className="text-[10px] text-slate-400 dark:text-zinc-500 font-semibold uppercase tracking-wide">
                {card.desc}
              </p>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
