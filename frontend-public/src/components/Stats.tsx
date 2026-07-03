"use client";

import React from "react";
import { motion } from "framer-motion";
import { ShieldCheck, MapPin, Award, Layers } from "lucide-react";

const statsData = [
  {
    value: "10,000+",
    label: "Authorized Dealers",
    icon: Award,
    color: "text-blue-600 dark:text-blue-400"
  },
  {
    value: "250+",
    label: "Brands",
    icon: Layers,
    color: "text-indigo-600 dark:text-indigo-400"
  },
  {
    value: "700+",
    label: "Cities",
    icon: MapPin,
    color: "text-emerald-600 dark:text-emerald-400"
  },
  {
    value: "99.9%",
    label: "Verified Listings",
    icon: ShieldCheck,
    color: "text-purple-600 dark:text-purple-400"
  }
];

export default function Stats() {
  return (
    <section className="py-12 border-y border-slate-200/80 dark:border-zinc-800/80 bg-slate-50/50 dark:bg-zinc-950/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-8">
          {statsData.map((stat, i) => {
            const IconComponent = stat.icon;
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 15 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className="text-center space-y-2 group"
              >
                <div className="mx-auto h-9 w-9 rounded-xl bg-white dark:bg-zinc-900 border border-slate-250/60 dark:border-zinc-800 flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform duration-300">
                  <IconComponent className={`h-4.5 w-4.5 ${stat.color}`} />
                </div>
                <div className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-zinc-50 font-sans tracking-tight">
                  {stat.value}
                </div>
                <div className="text-xs font-semibold text-slate-500 dark:text-zinc-400">
                  {stat.label}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
