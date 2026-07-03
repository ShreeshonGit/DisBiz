"use client";

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { ShieldCheck, ArrowUpRight } from "lucide-react";

interface Brand {
  id: string;
  name: string;
  official_website: string;
  category?: string;
  industry?: string;
}

interface BrandGridProps {
  brands: Brand[];
  onSelectBrand: (brandId: string) => void;
}

export default function BrandGrid({ brands, onSelectBrand }: BrandGridProps) {
  const [counts, setCounts] = useState<Record<string, number>>({});

  useEffect(() => {
    // Dynamically query dealer count per brand from search API
    const fetchCounts = async () => {
      const newCounts: Record<string, number> = {};
      for (const brand of brands.slice(0, 6)) {
        try {
          const res = await fetch(`/api/v1/scraper/dealers/search?brand_id=${brand.id}&limit=1`);
          const data = await res.json();
          if (data.success) {
            newCounts[brand.id] = data.data.total || 0;
          }
        } catch {
          newCounts[brand.id] = 0;
        }
      }
      setCounts(newCounts);
    };

    if (brands.length > 0) {
      fetchCounts();
    }
  }, [brands]);

  // Featured first 6 brands
  const featured = brands.slice(0, 6);

  if (featured.length === 0) return null;

  return (
    <section className="space-y-6 select-none">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-zinc-50">
            Featured Partner Brands
          </h2>
          <p className="text-xs text-slate-500 dark:text-zinc-400 mt-1 font-medium">
            Explore verified network catalogs from leading manufacturers across India.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {featured.map((brand, i) => {
          const dealerCount = counts[brand.id] !== undefined ? counts[brand.id] : "...";
          const category = brand.category || brand.industry || "General";
          
          return (
            <motion.div
              key={brand.id}
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.05 }}
              onClick={() => onSelectBrand(brand.id)}
              className="group bg-white dark:bg-zinc-900 border border-slate-200/80 dark:border-zinc-800/80 rounded-2xl p-5 hover:shadow-lg dark:hover:shadow-black/25 cursor-pointer transition-all duration-300 hover:-translate-y-1 relative overflow-hidden"
            >
              {/* Card gradient glow overlay on hover */}
              <div className="absolute inset-0 bg-gradient-to-tr from-blue-500/5 via-indigo-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />

              <div className="flex items-start justify-between relative z-10">
                {/* Brand Logo Initials Circle */}
                <div className="h-11 w-11 rounded-xl bg-slate-50 dark:bg-zinc-950 border border-slate-250/60 dark:border-zinc-800 flex items-center justify-center font-bold text-sm text-slate-800 dark:text-zinc-200 shadow-inner group-hover:scale-105 transition-transform duration-300">
                  {brand.name.slice(0, 2).toUpperCase()}
                </div>
                <div className="flex gap-1.5 items-center">
                  <span className="inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-400">
                    <ShieldCheck className="h-3 w-3" />
                    Verified
                  </span>
                  <ArrowUpRight className="h-4.5 w-4.5 text-slate-450 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                </div>
              </div>

              <div className="mt-5 space-y-1.5 relative z-10">
                <h3 className="text-base font-bold text-slate-900 dark:text-zinc-100 leading-snug group-hover:text-indigo-650 dark:group-hover:text-indigo-400 transition-colors">
                  {brand.name}
                </h3>
                <div className="flex items-center justify-between text-xs font-semibold text-slate-500 dark:text-zinc-400">
                  <span>{category}</span>
                  <span className="text-slate-400 dark:text-zinc-500">{dealerCount} Partners</span>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}
