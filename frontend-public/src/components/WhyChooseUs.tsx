"use client";

import React from "react";
import { motion } from "framer-motion";
import { ShieldCheck, Database, Search, MapPin, RefreshCw } from "lucide-react";

const features = [
  {
    title: "Verified Dealers",
    desc: "Every listing is checked against official manufacturer directories to eliminate duplicates.",
    icon: ShieldCheck
  },
  {
    title: "Live Database Sync",
    desc: "Real-time updates directly query official brand data endpoints to ensure active listings.",
    icon: Database
  },
  {
    title: "Fast Adaptive Search",
    desc: "Iterative filters and keyword search index thousands of retail partners in milliseconds.",
    icon: Search
  },
  {
    title: "Accurate Coordinates",
    desc: "Direct mapping integrations with latitude and longitude data ensure flawless directions.",
    icon: MapPin
  },
  {
    title: "Updated Daily",
    desc: "Automated background scrapers run daily validation syncs, maintaining quality scores.",
    icon: RefreshCw
  }
];

export default function WhyChooseUs() {
  return (
    <section className="space-y-8 select-none font-sans py-6">
      <div className="text-center max-w-xl mx-auto space-y-2">
        <h2 className="text-xl sm:text-2xl font-bold text-[#0F172A] dark:text-white font-serif">
          Why Choose Dealer Discovery?
        </h2>
        <p className="text-xs text-slate-500 dark:text-[#A1A1AA]">
          A robust, secure, and authenticated approach to mapping brand retail distribution networks.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5">
        {features.map((feat, i) => {
          const IconComponent = feat.icon;
          return (
            <motion.div
              key={feat.title}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.05 }}
              className="bg-white dark:bg-[#111113] border border-[#E5E7EB] dark:border-white/10 rounded-[16px] p-5 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 flex flex-col items-center text-center space-y-3"
            >
              <div className="p-3 rounded-[12px] bg-[#F8FAFC] dark:bg-[#09090B] border border-[#E5E7EB] dark:border-white/10 text-[#2563EB]">
                <IconComponent className="h-5 w-5" />
              </div>
              <h3 className="text-xs font-bold text-[#0F172A] dark:text-white">
                {feat.title}
              </h3>
              <p className="text-[11px] text-slate-500 dark:text-[#A1A1AA] leading-relaxed font-medium">
                {feat.desc}
              </p>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}
