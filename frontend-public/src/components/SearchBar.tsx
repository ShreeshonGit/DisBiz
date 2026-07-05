"use client";

import React from "react";
import { Search, MapPin, RefreshCw } from "lucide-react";

interface Brand {
  id: string;
  name: string;
}

interface SearchBarProps {
  query: string;
  setQuery: (val: string) => void;
  selectedBrand: string;
  setSelectedBrand: (val: string) => void;
  city: string;
  setCity: (val: string) => void;
  state: string;
  setState: (val: string) => void;
  pincode: string;
  setPincode: (val: string) => void;
  selectedCategory?: string;
  setSelectedCategory?: (val: string) => void;
  brands: Brand[];
  onSubmit: (e: React.FormEvent) => void;
  onReset: () => void;
}

const CATEGORIES_LIST = [
  "Electronics",
  "Furniture",
  "Automotive",
  "Healthcare",
  "Building Materials",
  "Agriculture",
  "Industrial",
  "Lifestyle"
];

export default function SearchBar({
  query, setQuery,
  selectedBrand, setSelectedBrand,
  city, setCity,
  setState,
  setPincode,
  selectedCategory = "",
  setSelectedCategory,
  brands,
  onSubmit,
  onReset
}: SearchBarProps) {
  
  const handleLocalReset = () => {
    setState("");
    setPincode("");
    if (setSelectedCategory) setSelectedCategory("");
    onReset();
  };

  return (
    <div className="bg-white dark:bg-zinc-900 border border-[#E5E7EB] dark:border-zinc-800 rounded-[20px] p-6 sm:p-7 shadow-sm max-w-4xl mx-auto font-sans">
      <form onSubmit={onSubmit} className="space-y-5">
        {/* Modern 12-Column Grid Layout */}
        <div className="grid grid-cols-12 gap-4 items-center">
          {/* Query Input - 5 columns (approx 42%) */}
          <div className="col-span-12 md:col-span-5 relative">
            <Search className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-400 dark:text-zinc-550" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by dealer, brand or city..."
              className="w-full text-xs pl-10 pr-4 h-12 rounded-[12px] border border-[#E5E7EB] dark:border-zinc-800 bg-[#F8FAFC] dark:bg-zinc-950 focus:bg-white dark:focus:bg-zinc-900 focus:outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB] text-slate-800 dark:text-zinc-100 placeholder-slate-400 dark:placeholder-zinc-650 transition-all font-medium"
            />
          </div>

          {/* Brand select - 2 columns */}
          <div className="col-span-12 sm:col-span-6 md:col-span-2">
            <select
              value={selectedBrand}
              onChange={(e) => setSelectedBrand(e.target.value)}
              className="w-full text-xs px-3 h-12 rounded-[12px] border border-[#E5E7EB] dark:border-zinc-800 bg-[#F8FAFC] dark:bg-zinc-950 focus:bg-white dark:focus:bg-zinc-900 focus:outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB] text-slate-700 dark:text-zinc-300 transition-all font-semibold"
            >
              <option value="">All Brands</option>
              {brands.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>

          {/* Location Input - 2 columns */}
          <div className="col-span-12 sm:col-span-6 md:col-span-2 relative">
            <MapPin className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-400 dark:text-zinc-550" />
            <input
              type="text"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              placeholder="Location..."
              className="w-full text-xs pl-9 pr-4 h-12 rounded-[12px] border border-[#E5E7EB] dark:border-zinc-800 bg-[#F8FAFC] dark:bg-zinc-950 focus:bg-white dark:focus:bg-zinc-900 focus:outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB] text-slate-800 dark:text-zinc-100 placeholder-slate-400 dark:placeholder-zinc-650 transition-all font-semibold"
            />
          </div>

          {/* Category Dropdown - 3 columns */}
          <div className="col-span-12 sm:col-span-12 md:col-span-3">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory && setSelectedCategory(e.target.value)}
              className="w-full text-xs px-3 h-12 rounded-[12px] border border-[#E5E7EB] dark:border-zinc-800 bg-[#F8FAFC] dark:bg-zinc-950 focus:bg-white dark:focus:bg-zinc-900 focus:outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB] text-slate-700 dark:text-zinc-305 transition-all font-semibold"
            >
              <option value="">All Categories</option>
              {CATEGORIES_LIST.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Buttons Row - Reset Beside dominant CTA Find Dealers */}
        <div className="flex justify-end items-center gap-3 pt-4 border-t border-[#E5E7EB] dark:border-zinc-800">
          <button
            type="button"
            onClick={handleLocalReset}
            className="inline-flex items-center justify-center gap-1.5 px-4 h-12 text-xs font-bold border border-[#E5E7EB] dark:border-zinc-800 text-slate-650 dark:text-zinc-300 hover:bg-[#F8FAFC] dark:hover:bg-zinc-850 rounded-[12px] cursor-pointer transition-colors"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Reset
          </button>
          
          <button
            type="submit"
            className="inline-flex items-center justify-center gap-2 px-6 h-12 text-xs font-bold bg-[#2563EB] hover:bg-blue-700 text-white rounded-[12px] cursor-pointer transition-all hover:scale-[1.01]"
          >
            <Search className="h-4 w-4" />
            Find Dealers
          </button>
        </div>
      </form>
    </div>
  );
}
