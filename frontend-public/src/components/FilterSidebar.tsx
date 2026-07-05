"use client";

import React, { useState } from "react";
import { SlidersHorizontal, X, RefreshCw, Check, Compass, Layers, MapPin, Tag } from "lucide-react";
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
      {/* Mobile filter trigger bar */}
      <div className="lg:hidden flex items-center justify-between bg-white dark:bg-zinc-900 border border-[#E5E7EB] dark:border-zinc-800 rounded-[16px] px-4 py-3 shadow-xs mb-4">
        <span className="text-xs font-semibold text-slate-700 dark:text-zinc-300">Filter Listings</span>
        <button
          onClick={() => setIsOpen(true)}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-slate-50 hover:bg-slate-105 dark:bg-zinc-800 dark:hover:bg-zinc-700 text-slate-805 dark:text-zinc-200 rounded-[12px] cursor-pointer transition-colors border border-[#E5E7EB] dark:border-zinc-800"
        >
          <SlidersHorizontal className="h-3.5 w-3.5" />
          Filter Settings
        </button>
      </div>

      {/* Desktop Vertical Sidebar - Sticky top-20 */}
      <div className="hidden lg:block lg:sticky lg:top-20 bg-white dark:bg-zinc-900 border border-[#E5E7EB] dark:border-zinc-800 rounded-[16px] p-5 space-y-6 shadow-xs">
        <div className="flex items-center justify-between pb-3 border-b border-[#E5E7EB] dark:border-zinc-800">
          <h3 className="text-sm font-bold text-[#0F172A] dark:text-zinc-150 font-serif">Filters</h3>
          <button
            onClick={onReset}
            className="text-[11px] font-semibold text-slate-400 hover:text-[#2563EB] dark:text-zinc-550 dark:hover:text-zinc-350 flex items-center gap-1 transition-colors"
          >
            <RefreshCw className="h-2.5 w-2.5" />
            Reset All
          </button>
        </div>

        {/* Group 1: Segment & Categories */}
        <div className="space-y-3 pb-4 border-b border-[#E5E7EB]/70 dark:border-zinc-800/60">
          <h4 className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider flex items-center gap-1.5">
            <Layers className="h-3.5 w-3.5 text-slate-400" />
            Segment
          </h4>
          <div className="space-y-1.5">
            <label className="text-[10px] font-medium text-slate-500 block">Industry Category</label>
            <input
              type="text"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              placeholder="e.g. Mattresses, Phones"
              className="w-full text-xs px-3 py-2.5 rounded-[12px] border border-[#E5E7EB] dark:border-zinc-800 bg-[#F8FAFC] dark:bg-zinc-950 focus:bg-white dark:focus:bg-zinc-900 focus:outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB]"
            />
          </div>
        </div>

        {/* Group 2: Brand Manufacturers */}
        <div className="space-y-3 pb-4 border-b border-[#E5E7EB]/70 dark:border-zinc-800/60">
          <h4 className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider flex items-center gap-1.5">
            <Tag className="h-3.5 w-3.5 text-slate-400" />
            Manufacturer
          </h4>
          <div className="space-y-1.5">
            <label className="text-[10px] font-medium text-slate-505 block">Select Brand</label>
            <select
              value={selectedBrand}
              onChange={(e) => setSelectedBrand(e.target.value)}
              className="w-full text-xs px-3 py-2.5 rounded-[12px] border border-[#E5E7EB] dark:border-zinc-800 bg-[#F8FAFC] dark:bg-zinc-950 focus:bg-white dark:focus:bg-zinc-900 focus:outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB] text-slate-700 dark:text-zinc-300"
            >
              <option value="">All Brands</option>
              {brands.map((b) => (
                <option key={b.id} value={b.id}>{b.name}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Group 3: Location Details */}
        <div className="space-y-3 pb-4 border-b border-[#E5E7EB]/70 dark:border-zinc-800/60">
          <h4 className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider flex items-center gap-1.5">
            <MapPin className="h-3.5 w-3.5 text-slate-400" />
            Geography
          </h4>
          <div className="grid grid-cols-1 gap-2.5">
            <div>
              <label className="text-[10px] font-medium text-slate-500 block mb-1">City</label>
              <input
                type="text"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                placeholder="Enter City"
                className="w-full text-xs px-3 py-2.5 rounded-[12px] border border-[#E5E7EB] dark:border-zinc-800 bg-[#F8FAFC] dark:bg-zinc-950 focus:bg-white dark:focus:bg-zinc-900 focus:outline-none"
              />
            </div>
            <div>
              <label className="text-[10px] font-medium text-slate-505 block mb-1">State</label>
              <input
                type="text"
                value={state}
                onChange={(e) => setState(e.target.value)}
                placeholder="Enter State"
                className="w-full text-xs px-3 py-2.5 rounded-[12px] border border-[#E5E7EB] dark:border-zinc-800 bg-[#F8FAFC] dark:bg-zinc-950 focus:bg-white dark:focus:bg-zinc-900 focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* Group 4: Format Type */}
        <div className="space-y-3 pb-4">
          <h4 className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider flex items-center gap-1.5">
            <Compass className="h-3.5 w-3.5 text-slate-400" />
            Outlet Format
          </h4>
          <div className="space-y-1.5">
            <label className="text-[10px] font-medium text-slate-505 block">Format Type</label>
            <select
              value={dealerType}
              onChange={(e) => setDealerType(e.target.value)}
              className="w-full text-xs px-3 py-2.5 rounded-[12px] border border-[#E5E7EB] dark:border-zinc-800 bg-[#F8FAFC] dark:bg-zinc-950 focus:bg-white dark:focus:bg-zinc-900 focus:outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB] text-slate-700 dark:text-zinc-305"
            >
              {dealerTypes.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Apply Trigger Button */}
        <button
          onClick={onApply}
          className="w-full h-11 text-xs font-bold bg-[#2563EB] hover:bg-blue-700 text-white rounded-[12px] flex items-center justify-center gap-1.5 transition-all cursor-pointer shadow-xs"
        >
          <Check className="h-4 w-4" />
          Apply Filters
        </button>
      </div>

      {/* Mobile Drawer Overlay */}
      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.3 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 bg-black z-50 cursor-pointer"
            />
            
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "tween", ease: "easeInOut", duration: 0.25 }}
              className="fixed right-0 top-0 bottom-0 w-80 bg-white dark:bg-zinc-950 border-l border-[#E5E7EB] dark:border-zinc-850 p-6 z-50 shadow-lg flex flex-col justify-between"
            >
              <div className="space-y-6">
                <div className="flex items-center justify-between pb-4 border-b border-[#E5E7EB] dark:border-zinc-900">
                  <h3 className="font-bold text-sm text-[#0F172A] dark:text-zinc-150">Search Filters</h3>
                  <button onClick={() => setIsOpen(false)} className="p-1 rounded-md hover:bg-slate-50 dark:hover:bg-zinc-800">
                    <X className="h-4 w-4" />
                  </button>
                </div>

                {/* Category */}
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-slate-455 dark:text-zinc-500 uppercase tracking-wider block">Category</label>
                  <input
                    type="text"
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    placeholder="All Categories"
                    className="w-full text-xs px-3 py-2.5 rounded-[12px] border border-[#E5E7EB] dark:border-zinc-800 bg-[#F8FAFC] dark:bg-zinc-900 focus:outline-none"
                  />
                </div>

                {/* Brand select */}
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-slate-455 dark:text-zinc-500 uppercase tracking-wider block">Brand</label>
                  <select
                    value={selectedBrand}
                    onChange={(e) => setSelectedBrand(e.target.value)}
                    className="w-full text-xs px-3 py-2.5 rounded-[12px] border border-[#E5E7EB] dark:border-zinc-800 bg-[#F8FAFC] dark:bg-zinc-900 focus:outline-none text-slate-700 dark:text-zinc-300"
                  >
                    <option value="">All Brands</option>
                    {brands.map((b) => (
                      <option key={b.id} value={b.id}>{b.name}</option>
                    ))}
                  </select>
                </div>

                {/* State */}
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-slate-455 dark:text-zinc-500 uppercase tracking-wider block">State</label>
                  <input
                    type="text"
                    value={state}
                    onChange={(e) => setState(e.target.value)}
                    placeholder="Enter state"
                    className="w-full text-xs px-3 py-2.5 rounded-[12px] border border-[#E5E7EB] dark:border-zinc-800 bg-[#F8FAFC] dark:bg-zinc-900 focus:outline-none"
                  />
                </div>

                {/* City */}
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-slate-455 dark:text-zinc-500 uppercase tracking-wider block">City</label>
                  <input
                    type="text"
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    placeholder="Enter city"
                    className="w-full text-xs px-3 py-2.5 rounded-[12px] border border-[#E5E7EB] dark:border-zinc-800 bg-[#F8FAFC] dark:bg-zinc-900 focus:outline-none"
                  />
                </div>

                {/* Dealer Type */}
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-slate-455 dark:text-zinc-500 uppercase tracking-wider block">Format Format</label>
                  <select
                    value={dealerType}
                    onChange={(e) => setDealerType(e.target.value)}
                    className="w-full text-xs px-3 py-2.5 rounded-[12px] border border-[#E5E7EB] dark:border-zinc-800 bg-[#F8FAFC] dark:bg-zinc-900 focus:outline-none text-slate-700 dark:text-zinc-300"
                  >
                    {dealerTypes.map((t) => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Drawer actions */}
              <div className="pt-4 border-t border-[#E5E7EB] dark:border-zinc-900 flex gap-2">
                <button
                  onClick={() => { onReset(); setIsOpen(false); }}
                  className="w-1/2 py-2.5 text-xs font-bold border border-[#E5E7EB] dark:border-zinc-800 rounded-[12px] hover:bg-slate-50 dark:hover:bg-zinc-900 text-slate-700 dark:text-zinc-350 cursor-pointer"
                >
                  Reset
                </button>
                <button
                  onClick={() => { onApply(); setIsOpen(false); }}
                  className="w-1/2 py-2.5 text-xs font-bold bg-[#2563EB] hover:bg-blue-700 text-white rounded-[12px] cursor-pointer"
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
