"use client";

import React from "react";
import { motion } from "framer-motion";
import { 
  Smartphone, Bed, Car, Stethoscope, 
  Hammer, Sprout, Wrench, Sparkles, ArrowRight 
} from "lucide-react";

interface PopularCategoriesProps {
  onSelectCategory: (category: string) => void;
}

const categories = [
  { 
    name: "Electronics", 
    icon: Smartphone, 
    desc: "Verify authorized retail shops, repair labs, and electronics outlets." 
  },
  { 
    name: "Furniture", 
    icon: Bed, 
    desc: "Locate authorized showrooms, sleep centers, and wooden furniture dealers." 
  },
  { 
    name: "Automotive", 
    icon: Car, 
    desc: "Find verified car showrooms, service garages, and tire retailers." 
  },
  { 
    name: "Healthcare", 
    icon: Stethoscope, 
    desc: "Search approved pharmacies, diagnostic clinics, and wellness clinics." 
  },
  { 
    name: "Building Materials", 
    icon: Hammer, 
    desc: "Check certified sanitaryware outlets, tile stores, and hardware shops." 
  },
  { 
    name: "Agriculture", 
    icon: Sprout, 
    desc: "Explore authorized pump retailers, fertilizer stores, and tractor dealers." 
  },
  { 
    name: "Industrial", 
    icon: Wrench, 
    desc: "Verify machine tools outlets, industrial bearings, and pump suppliers." 
  },
  { 
    name: "Lifestyle", 
    icon: Sparkles, 
    desc: "Discover official clothing boutiques, watch dealers, and optical stores." 
  }
];

export default function PopularCategories({ onSelectCategory }: PopularCategoriesProps) {
  return (
    <section className="space-y-6 select-none font-sans">
      <div>
        <h2 className="text-xl sm:text-2xl font-bold text-[#0F172A] dark:text-white font-serif tracking-tight">
          Browse by Category
        </h2>
        <p className="text-xs text-slate-500 dark:text-[#A1A1AA] mt-1">
          Quickly discover authorized vendors matching your specific product segment.
        </p>
      </div>

      {/* Grid: 4x2 on desktop, scrollable on mobile */}
      <div className="flex overflow-x-auto pb-4 gap-4 md:grid md:grid-cols-4 md:gap-6 scrollbar-thin scrollbar-track-transparent">
        {categories.map((cat, i) => {
          const IconComponent = cat.icon;
          return (
            <motion.div
              key={cat.name}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.35, delay: i * 0.03 }}
              onClick={() => onSelectCategory(cat.name)}
              className="group min-w-[240px] md:min-w-0 bg-white dark:bg-[#111113] border border-[#E5E7EB] dark:border-white/10 rounded-[20px] p-6 flex flex-col justify-between hover:border-[#2563EB] dark:hover:border-blue-500 hover:shadow-lg hover:shadow-blue-500/5 hover:-translate-y-1 transition-all duration-300 cursor-pointer"
            >
              <div className="space-y-4">
                {/* Large Icon Container */}
                <div className="h-12 w-12 rounded-[14px] bg-[#F8FAFC] dark:bg-[#09090B] border border-[#E5E7EB] dark:border-white/10 text-[#2563EB] flex items-center justify-center group-hover:scale-105 transition-transform duration-200 shadow-xs">
                  <IconComponent className="h-5.5 w-5.5" />
                </div>
                
                <div className="space-y-1 text-left">
                  <h3 className="text-sm font-bold text-[#0F172A] dark:text-white group-hover:text-[#2563EB] transition-colors leading-tight">
                    {cat.name}
                  </h3>
                  <p className="text-[11px] text-slate-400 dark:text-[#A1A1AA] leading-relaxed">
                    {cat.desc}
                  </p>
                </div>
              </div>

              {/* Bottom Arrow Indicator */}
              <div className="flex justify-end pt-4 mt-2 border-t border-slate-50 dark:border-white/5">
                <ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-[#2563EB] group-hover:translate-x-1 transition-all" />
              </div>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}
