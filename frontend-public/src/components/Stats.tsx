"use client";

import React from "react";
import { motion } from "framer-motion";
import { ShieldCheck, MapPin, Award, Layers } from "lucide-react";

const statsData = [
  {
    value: "10,000+",
    label: "Verified Dealers",
    icon: Award
  },
  {
    value: "250+",
    label: "Brands",
    icon: Layers
  },
  {
    value: "700+",
    label: "Cities",
    icon: MapPin
  },
  {
    value: "99.9%",
    label: "Verified Listings",
    icon: ShieldCheck
  }
];

export default function Stats() {
  return (
    <section className="py-12 bg-[#F8FAFC] dark:bg-[#09090B] font-sans select-none border-b border-[#E5E7EB] dark:border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {statsData.map((stat, i) => {
            const IconComponent = stat.icon;
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.05 }}
                className="bg-white dark:bg-[#111113] border border-[#E5E7EB] dark:border-white/10 rounded-[20px] p-6 flex items-start gap-4 shadow-xs hover:shadow-md hover:-translate-y-1 transition-all duration-250 h-full"
              >
                {/* Icon wrapper */}
                <div className="h-11 w-11 shrink-0 rounded-[12px] bg-[#F8FAFC] dark:bg-[#09090B] border border-[#E5E7EB] dark:border-white/10 flex items-center justify-center">
                  <IconComponent className="h-5 w-5 text-[#2563EB]" />
                </div>
                
                {/* Numbers */}
                <div className="space-y-1">
                  <div className="text-3xl sm:text-4xl font-extrabold text-[#0F172A] dark:text-white font-serif leading-none tracking-tight">
                    {stat.value}
                  </div>
                  <div className="text-xs font-bold text-slate-400 dark:text-[#A1A1AA] uppercase tracking-wider">
                    {stat.label}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
