"use client";

import React from "react";
import { motion } from "framer-motion";
import { 
  Smartphone, Bed, Car, Stethoscope, 
  Hammer, Sprout, Wrench, Sparkles 
} from "lucide-react";

interface PopularCategoriesProps {
  onSelectCategory: (category: string) => void;
}

const categories = [
  { name: "Electronics", icon: Smartphone, gradient: "from-blue-500/10 to-indigo-500/10 text-blue-600 dark:text-blue-400" },
  { name: "Furniture", icon: Bed, gradient: "from-emerald-500/10 to-teal-500/10 text-emerald-600 dark:text-emerald-400" },
  { name: "Automotive", icon: Car, gradient: "from-cyan-500/10 to-sky-500/10 text-cyan-600 dark:text-cyan-400" },
  { name: "Healthcare", icon: Stethoscope, gradient: "from-purple-500/10 to-violet-500/10 text-purple-600 dark:text-purple-400" },
  { name: "Building Materials", icon: Hammer, gradient: "from-rose-500/10 to-pink-500/10 text-rose-600 dark:text-rose-450" },
  { name: "Agriculture", icon: Sprout, gradient: "from-green-500/10 to-emerald-500/10 text-green-600 dark:text-green-400" },
  { name: "Industrial", icon: Wrench, gradient: "from-zinc-500/10 to-slate-500/10 text-slate-700 dark:text-slate-350" },
  { name: "Lifestyle", icon: Sparkles, gradient: "from-amber-500/10 to-orange-500/10 text-amber-600 dark:text-amber-450" }
];

export default function PopularCategories({ onSelectCategory }: PopularCategoriesProps) {
  return (
    <section className="space-y-6 select-none font-sans">
      <div>
        <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-zinc-50">
          Browse by Popular Category
        </h2>
        <p className="text-xs text-slate-500 dark:text-zinc-400 mt-1 font-medium">
          Quickly discover authorized vendors matching your specific product segment.
        </p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        {categories.map((cat, i) => {
          const IconComponent = cat.icon;
          return (
            <motion.div
              key={cat.name}
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.35, delay: i * 0.04 }}
              onClick={() => onSelectCategory(cat.name)}
              className="group bg-white dark:bg-zinc-900 border border-slate-200/80 dark:border-zinc-800/80 rounded-2xl p-5 hover:shadow-md cursor-pointer transition-all duration-300 hover:-translate-y-0.5 flex flex-col items-center justify-center text-center space-y-3 relative overflow-hidden"
            >
              <div className={`p-3.5 rounded-2xl bg-gradient-to-br ${cat.gradient} group-hover:scale-110 transition-transform duration-300 shadow-inner`}>
                <IconComponent className="h-6 w-6" />
              </div>
              <span className="text-xs font-bold text-slate-800 dark:text-zinc-200 group-hover:text-indigo-650 dark:group-hover:text-indigo-400 transition-colors">
                {cat.name}
              </span>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}
