"use client";

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { ShieldCheck, ArrowRight } from "lucide-react";

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

  const featured = brands.slice(0, 6);

  if (featured.length === 0) return null;

  return (
    <section className="space-y-6 select-none font-sans">
      <div>
        <h2 className="text-xl sm:text-2xl font-bold text-[#0F172A] dark:text-white font-serif tracking-tight">
          Featured Brands
        </h2>
        <p className="text-xs text-slate-500 dark:text-[#A1A1AA] mt-1">
          Explore manufacturer-authorized retail catalogs and distribution channels.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {featured.map((brand, i) => {
          const dealerCount = counts[brand.id] !== undefined ? counts[brand.id] : "...";
          const category = brand.category || brand.industry || "General";
          
          return (
            <motion.div
              key={brand.id}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.35, delay: i * 0.04 }}
              onClick={() => onSelectBrand(brand.id)}
              className="group bg-white dark:bg-[#111113] border border-[#E5E7EB] dark:border-white/10 rounded-[16px] p-6 hover:border-[#2563EB] dark:hover:border-blue-500 hover:shadow-lg hover:shadow-blue-500/5 hover:-translate-y-1 transition-all duration-300 cursor-pointer flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between">
                  {/* Logo wrapper */}
                  <div className="h-14 w-14 rounded-[12px] bg-[#F8FAFC] dark:bg-[#09090B] border border-[#E5E7EB] dark:border-white/10 flex items-center justify-center font-extrabold text-base text-[#0F172A] dark:text-white shadow-xs">
                    {brand.name.slice(0, 2).toUpperCase()}
                  </div>
                  
                  <span className="inline-flex items-center gap-1.5 text-[9px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/20 text-[#10B981] dark:text-emerald-450 border border-emerald-100 dark:border-emerald-900/20">
                    <ShieldCheck className="h-3.5 w-3.5" />
                    Verified
                  </span>
                </div>

                <div className="mt-5 space-y-1">
                  <h3 className="text-base font-bold text-[#0F172A] dark:text-white font-serif leading-tight">
                    {brand.name}
                  </h3>
                  <span className="text-[10px] text-slate-400 dark:text-[#A1A1AA] font-semibold block uppercase tracking-wider">
                    {category}
                  </span>
                </div>
              </div>

              {/* Bottom count and CTA Explore trigger */}
              <div className="mt-6 pt-4 border-t border-slate-100 dark:border-white/5 flex items-center justify-between">
                <span className="text-xs font-bold text-[#2563EB] dark:text-indigo-400">
                  {dealerCount} Active Dealers
                </span>
                
                <span className="inline-flex items-center gap-1 text-xs font-bold text-slate-700 dark:text-zinc-300 group-hover:text-[#2563EB] dark:group-hover:text-indigo-400 transition-colors">
                  Explore Catalog
                  <ArrowRight className="h-3.5 w-3.5 group-hover:translate-x-1 transition-transform" />
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}
