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
    items: ["Mobile Phones", "Laptops", "TVs"]
  },
  {
    title: "Home Appliances",
    icon: FlameKindling,
    items: ["Refrigerators", "Washing Machines", "Air Conditioners"]
  },
  {
    title: "Furniture",
    icon: Bed,
    items: ["Mattresses", "Sofas", "Chairs"]
  },
  {
    title: "Building Materials",
    icon: Hammer,
    items: ["Tiles", "Paint", "Cement"]
  },
  {
    title: "Automotive",
    icon: Car,
    items: ["Two Wheelers", "Four Wheelers"]
  },
  {
    title: "Healthcare",
    icon: Stethoscope,
    items: ["Medical Equipment"]
  },
  {
    title: "Industrial",
    icon: Wrench,
    items: ["Machinery"]
  },
  {
    title: "Agriculture",
    icon: Sprout,
    items: ["Farm Equipment"]
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
          className="absolute left-1/2 -translate-x-1/2 top-full mt-2 w-[85vw] max-w-4xl bg-white/95 dark:bg-[#111113]/95 backdrop-blur-xl border border-slate-200 dark:border-white/10 rounded-[20px] shadow-lg p-6 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 z-50 text-left"
        >
          {categoriesData.map((cat) => {
            const IconComponent = cat.icon;
            return (
              <div key={cat.title} className="space-y-3.5">
                <div className="inline-flex items-center gap-2.5 px-3 py-1.5 rounded-[12px] bg-[#F8FAFC] dark:bg-[#09090B] border border-slate-100 dark:border-white/5 font-semibold text-xs text-slate-800 dark:text-white shadow-xs w-full">
                  <IconComponent className="h-4 w-4 text-[#2563EB]" />
                  <span>{cat.title}</span>
                </div>
                <ul className="space-y-2 pl-1.5 text-xs text-slate-500 dark:text-[#A1A1AA] font-medium">
                  {cat.items.map((item) => (
                    <li key={item}>
                      <button
                        onClick={() => onSelect(item)}
                        className="hover:text-[#2563EB] dark:hover:text-indigo-400 transition-colors duration-200 block w-full text-left"
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
