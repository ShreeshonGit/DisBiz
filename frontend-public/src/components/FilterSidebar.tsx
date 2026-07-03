"use client";

import React, { useState } from "react";
import { SlidersHorizontal, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface Brand {
  id: string;
  name: string;
}

interface FilterSidebarProps {
  brands: Brand[];
  selectedBrand: string;
  setSelectedBrand: (val: string) => void;
  selectedCategory: string;
  setSelectedCategory: (val: string) => void;
  city: string;
  setCity: (val: string) => void;
  state: string;
  setState: (val: string) => void;
  dealerType: string;
  setDealerType: (val: string) => void;
  onApply: () => void;
  onReset: () => void;
}

const dealerTypes = [
  { value: "", label: "All Formats" },
  { value: "service", label: "Service Center" },
  { value: "distributor", label: "Distributor" },
  { value: "retail", label: "Retail Store" }
];

export default function FilterSidebar({
  brands,
  selectedBrand, setSelectedBrand,
  selectedCategory, setSelectedCategory,
  city, setCity,
  state, setState,
  dealerType, setDealerType,
  onApply,
  onReset
}: FilterSidebarProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="w-full select-none font-sans">
      {/* Mobile filter toggle trigger */}
      <div className="md:hidden flex items-center justify-between bg-white dark:bg-zinc-900 border border-slate-200/80 dark:border-zinc-800/80 rounded-xl px-4 py-3 shadow-sm">
        <span className="text-xs font-bold text-slate-700 dark:text-zinc-300">Search Filter Parameters</span>
        <button
          onClick={() => setIsOpen(true)}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold bg-slate-100 hover:bg-slate-200 dark:bg-zinc-800 dark:hover:bg-zinc-700 text-slate-800 dark:text-zinc-200 rounded-lg cursor-pointer transition-colors"
        >
          <SlidersHorizontal className="h-3.5 w-3.5" />
          Filter Settings
        </button>
      </div>

      {/* Desktop Horizontal Layout */}
      <div className="hidden md:grid grid-cols-5 gap-4 items-center bg-slate-50/50 dark:bg-zinc-950/20 border border-slate-200/60 dark:border-zinc-800/60 rounded-xl p-4">
        {/* Dealer Format/Type */}
        <div>
          <label className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider block mb-1.5">Format Type</label>
          <select
            value={dealerType}
            onChange={(e) => setDealerType(e.target.value)}
            className="w-full text-xs px-3 py-2 rounded-lg border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 focus:outline-none focus:ring-1 focus:ring-blue-500/20 text-slate-700 dark:text-zinc-300"
          >
            {dealerTypes.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </div>

        {/* Selected Category */}
        <div>
          <label className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider block mb-1.5">Industry Segment</label>
          <input
            type="text"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            placeholder="e.g. Mattresses, Phones"
            className="w-full text-xs px-3 py-2 rounded-lg border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 focus:outline-none focus:ring-1 focus:ring-blue-500/20 text-slate-700 dark:text-zinc-300 font-medium"
          />
        </div>

        {/* Brand */}
        <div>
          <label className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider block mb-1.5">Partner Brand</label>
          <select
            value={selectedBrand}
            onChange={(e) => setSelectedBrand(e.target.value)}
            className="w-full text-xs px-3 py-2 rounded-lg border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 focus:outline-none focus:ring-1 focus:ring-blue-500/20 text-slate-700 dark:text-zinc-300"
          >
            <option value="">All Brands</option>
            {brands.map((b) => (
              <option key={b.id} value={b.id}>{b.name}</option>
            ))}
          </select>
        </div>

        {/* Location (State/City) */}
        <div>
          <label className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider block mb-1.5">District / State</label>
          <div className="grid grid-cols-2 gap-2">
            <input
              type="text"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              placeholder="City"
              className="w-full text-xs px-2.5 py-2 rounded-lg border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 focus:outline-none text-slate-700 dark:text-zinc-300 font-medium"
            />
            <input
              type="text"
              value={state}
              onChange={(e) => setState(e.target.value)}
              placeholder="State"
              className="w-full text-xs px-2.5 py-2 rounded-lg border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 focus:outline-none text-slate-700 dark:text-zinc-300 font-medium"
            />
          </div>
        </div>

        {/* Buttons */}
        <div className="flex gap-2 justify-end pt-3">
          <button
            onClick={onReset}
            className="px-3.5 py-2 text-xs font-bold border border-slate-200 dark:border-zinc-800 hover:bg-slate-50 dark:hover:bg-zinc-800 rounded-lg cursor-pointer text-slate-600 dark:text-zinc-400 transition-colors"
          >
            Reset
          </button>
          <button
            onClick={onApply}
            className="px-4 py-2 text-xs font-bold bg-zinc-900 text-zinc-50 hover:bg-zinc-800 dark:bg-zinc-50 dark:text-zinc-950 dark:hover:bg-zinc-200 rounded-lg cursor-pointer transition-colors"
          >
            Apply
          </button>
        </div>
      </div>

      {/* Mobile Drawer Backdrop + Overlay */}
      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.4 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 bg-black z-50 cursor-pointer"
            />
            
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "tween", ease: "easeInOut", duration: 0.3 }}
              className="fixed right-0 top-0 bottom-0 w-80 bg-white dark:bg-zinc-950 border-l border-slate-200 dark:border-zinc-850 p-6 z-50 shadow-2xl flex flex-col justify-between"
            >
              <div className="space-y-6">
                <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-zinc-900">
                  <h3 className="font-bold text-sm text-slate-900 dark:text-zinc-150">Search Filters</h3>
                  <button onClick={() => setIsOpen(false)} className="p-1 rounded-md hover:bg-slate-150 dark:hover:bg-zinc-800">
                    <X className="h-4 w-4" />
                  </button>
                </div>

                {/* Categories */}
                <div className="space-y-2">
                  <label className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider block">Category</label>
                  <input
                    type="text"
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    placeholder="All Categories"
                    className="w-full text-xs px-3 py-2.5 rounded-lg border border-slate-200 dark:border-zinc-800 bg-slate-50 dark:bg-zinc-900 focus:outline-none"
                  />
                </div>

                {/* Brands */}
                <div className="space-y-2">
                  <label className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider block">Brand</label>
                  <select
                    value={selectedBrand}
                    onChange={(e) => setSelectedBrand(e.target.value)}
                    className="w-full text-xs px-3 py-2.5 rounded-lg border border-slate-200 dark:border-zinc-800 bg-slate-50 dark:bg-zinc-900 focus:outline-none"
                  >
                    <option value="">All Brands</option>
                    {brands.map((b) => (
                      <option key={b.id} value={b.id}>{b.name}</option>
                    ))}
                  </select>
                </div>

                {/* State */}
                <div className="space-y-2">
                  <label className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider block">State</label>
                  <input
                    type="text"
                    value={state}
                    onChange={(e) => setState(e.target.value)}
                    placeholder="Enter state"
                    className="w-full text-xs px-3 py-2.5 rounded-lg border border-slate-200 dark:border-zinc-800 bg-slate-50 dark:bg-zinc-900 focus:outline-none"
                  />
                </div>

                {/* City */}
                <div className="space-y-2">
                  <label className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider block">City</label>
                  <input
                    type="text"
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    placeholder="Enter city"
                    className="w-full text-xs px-3 py-2.5 rounded-lg border border-slate-200 dark:border-zinc-800 bg-slate-50 dark:bg-zinc-900 focus:outline-none"
                  />
                </div>

                {/* Dealer Type */}
                <div className="space-y-2">
                  <label className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider block">Format Format</label>
                  <select
                    value={dealerType}
                    onChange={(e) => setDealerType(e.target.value)}
                    className="w-full text-xs px-3 py-2.5 rounded-lg border border-slate-200 dark:border-zinc-800 bg-slate-50 dark:bg-zinc-900 focus:outline-none"
                  >
                    {dealerTypes.map((t) => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Action Drawer Buttons */}
              <div className="pt-4 border-t border-slate-100 dark:border-zinc-900 flex gap-2">
                <button
                  onClick={() => { onReset(); setIsOpen(false); }}
                  className="w-1/2 py-2.5 text-xs font-bold border border-slate-200 dark:border-zinc-800 rounded-lg hover:bg-slate-50 dark:hover:bg-zinc-900 text-slate-700 dark:text-zinc-350 cursor-pointer"
                >
                  Reset
                </button>
                <button
                  onClick={() => { onApply(); setIsOpen(false); }}
                  className="w-1/2 py-2.5 text-xs font-bold bg-zinc-900 text-zinc-50 dark:bg-zinc-50 dark:text-zinc-950 dark:hover:bg-zinc-200 rounded-lg cursor-pointer"
                >
                  Apply
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
