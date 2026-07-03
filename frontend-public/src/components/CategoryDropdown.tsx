"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Laptop, 
  FlameKindling, 
  Bed, 
  Hammer, 
  Car, 
  Stethoscope, 
  Wrench, 
  Sprout
} from "lucide-react";

interface CategoryDropdownProps {
  isOpen: boolean;
  onSelect: (category: string) => void;
}

const categoriesData = [
  {
    title: "Electronics",
    icon: Laptop,
    items: ["Mobile Phones", "Laptops", "TVs"],
    color: "from-blue-500/10 to-indigo-500/10 text-indigo-600 dark:text-indigo-400"
  },
  {
    title: "Home Appliances",
    icon: FlameKindling,
    items: ["Refrigerators", "Washing Machines", "Air Conditioners"],
    color: "from-amber-500/10 to-orange-500/10 text-amber-600 dark:text-amber-450"
  },
  {
    title: "Furniture",
    icon: Bed,
    items: ["Mattresses", "Sofas", "Chairs"],
    color: "from-emerald-500/10 to-teal-500/10 text-emerald-600 dark:text-emerald-400"
  },
  {
    title: "Building Materials",
    icon: Hammer,
    items: ["Tiles", "Paint", "Cement"],
    color: "from-rose-500/10 to-pink-500/10 text-rose-600 dark:text-rose-450"
  },
  {
    title: "Automotive",
    icon: Car,
    items: ["Two Wheelers", "Four Wheelers"],
    color: "from-cyan-500/10 to-sky-500/10 text-cyan-600 dark:text-cyan-400"
  },
  {
    title: "Healthcare",
    icon: Stethoscope,
    items: ["Medical Equipment"],
    color: "from-purple-500/10 to-violet-500/10 text-purple-600 dark:text-purple-400"
  },
  {
    title: "Industrial",
    icon: Wrench,
    items: ["Machinery"],
    color: "from-zinc-500/10 to-slate-500/10 text-slate-700 dark:text-slate-350"
  },
  {
    title: "Agriculture",
    icon: Sprout,
    items: ["Farm Equipment"],
    color: "from-green-500/10 to-emerald-500/10 text-green-600 dark:text-green-400"
  }
];

export default function CategoryDropdown({ isOpen, onSelect }: CategoryDropdownProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
          transition={{ duration: 0.2, ease: "easeOut" }}
          className="absolute left-1/2 -translate-x-1/2 top-full mt-2 w-[85vw] max-w-4xl bg-white/90 dark:bg-zinc-950/90 backdrop-blur-xl border border-slate-200/80 dark:border-zinc-800/80 rounded-2xl shadow-2xl p-6 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 z-50 text-left"
        >
          {categoriesData.map((cat) => {
            const IconComponent = cat.icon;
            return (
              <div key={cat.title} className="space-y-3.5">
                <div className={`inline-flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-gradient-to-br ${cat.color} font-semibold text-xs border border-slate-100 dark:border-zinc-900 shadow-sm w-full`}>
                  <IconComponent className="h-4 w-4" />
                  <span>{cat.title}</span>
                </div>
                <ul className="space-y-2 pl-1.5 text-xs text-slate-500 dark:text-zinc-400 font-medium">
                  {cat.items.map((item) => (
                    <li key={item}>
                      <button
                        onClick={() => onSelect(item)}
                        className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors duration-200 block w-full text-left"
                      >
                        {item}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
