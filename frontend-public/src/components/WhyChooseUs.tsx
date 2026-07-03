"use client";

import React from "react";
import { motion } from "framer-motion";
import { ShieldCheck, Database, Search, MapPin, RefreshCw } from "lucide-react";

const features = [
  {
    title: "Verified Dealers Only",
    desc: "Every listing is checked against official manufacturer locator indexes to eliminate duplicates or fraudulent listings.",
    icon: ShieldCheck,
    color: "text-emerald-500 bg-emerald-500/10"
  },
  {
    title: "Live Database Sync",
    desc: "Real-time updates directly query official brand data endpoints to ensure store operating hours and contacts are active.",
    icon: Database,
    color: "text-blue-500 bg-blue-500/10"
  },
  {
    title: "Fast Adaptive Search",
    desc: "Iterative filters and keyword search index thousands of retail partners and service outlets in milliseconds.",
    icon: Search,
    color: "text-indigo-500 bg-indigo-500/10"
  },
  {
    title: "Accurate Coordinates",
    desc: "Direct mapping integrations with latitude and longitude data ensure flawless directions with Google Maps view.",
    icon: MapPin,
    color: "text-rose-500 bg-rose-500/10"
  },
  {
    title: "Updated Daily",
    desc: "Our automated background scrapers run daily validation syncs, maintaining listing freshness and scoring quality.",
    icon: RefreshCw,
    color: "text-purple-500 bg-purple-500/10"
  }
];

export default function WhyChooseUs() {
  return (
    <section className="space-y-8 select-none font-sans py-6">
      <div className="text-center max-w-xl mx-auto space-y-2">
        <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-zinc-50">
          Why Choose Dealer Discovery?
        </h2>
        <p className="text-xs text-slate-500 dark:text-zinc-400 font-medium">
          A robust, secure, and authenticated approach to mapping brand retail distribution network locations.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5">
        {features.map((feat, i) => {
          const IconComponent = feat.icon;
          return (
            <motion.div
              key={feat.title}
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.05 }}
              className="bg-white dark:bg-zinc-900 border border-slate-200/80 dark:border-zinc-800/80 rounded-2xl p-5 hover:shadow-md transition-shadow duration-300 flex flex-col items-center text-center space-y-3.5"
            >
              <div className={`p-3 rounded-xl ${feat.color} shadow-sm`}>
                <IconComponent className="h-5 w-5" />
              </div>
              <h3 className="text-xs font-bold text-slate-800 dark:text-zinc-200">
                {feat.title}
              </h3>
              <p className="text-[11px] text-slate-500 dark:text-zinc-400 leading-relaxed font-medium">
                {feat.desc}
              </p>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}
