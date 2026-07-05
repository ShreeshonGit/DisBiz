"use client";

import React from "react";
import { motion } from "framer-motion";
import { ShieldCheck } from "lucide-react";

interface HeroProps {
  children?: React.ReactNode;
}

export default function Hero({ children }: HeroProps) {
  return (
    <section className="relative overflow-hidden bg-[#F8FAFC] dark:bg-[#09090B] pt-14 pb-12 text-center select-none border-b border-[#E5E7EB] dark:border-white/5">
      {/* High-end ultra-light radial glow */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(37,99,235,0.04)_0%,transparent_70%)] pointer-events-none" />

      <div className="relative max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="space-y-4">
          {/* Top Badge */}
          <motion.div
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white dark:bg-[#111113] border border-[#E5E7EB] dark:border-white/10 text-[10px] font-bold text-[#2563EB] dark:text-zinc-300 tracking-wider uppercase shadow-xs"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-[#2563EB]" />
            <span>Verified Brand Directory</span>
          </motion.div>

          {/* Headline - Max 2 lines */}
          <motion.h1
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.05 }}
            className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-[#0F172A] dark:text-white leading-tight font-serif max-w-3xl mx-auto"
          >
            Find Authorized Dealers Across India
          </motion.h1>

          {/* Subheading - Single sentence */}
          <motion.p
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
            className="text-xs sm:text-sm text-slate-500 dark:text-[#A1A1AA] max-w-[650px] mx-auto leading-relaxed font-medium"
          >
            Discover verified dealers, distributors and service centres from trusted manufacturers across India.
          </motion.p>
        </div>

        {/* Premium search card slot */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.15 }}
          className="max-w-4xl mx-auto pt-2"
        >
          {children}
        </motion.div>
      </div>
    </section>
  );
}
