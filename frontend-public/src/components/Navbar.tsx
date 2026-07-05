"use client";

import React, { useState, useEffect } from "react";
import { Sun, Moon, Search, ChevronDown, Menu, X } from "lucide-react";
import CategoryDropdown from "./CategoryDropdown";

interface NavbarProps {
  isDarkMode: boolean;
  toggleTheme: () => void;
  onSelectCategory: (category: string) => void;
  onSearchClick: () => void;
}

export default function Navbar({ 
  isDarkMode, 
  toggleTheme, 
  onSelectCategory,
  onSearchClick 
}: NavbarProps) {
  const [isCatOpen, setIsCatOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header className={`sticky top-0 z-50 transition-all duration-300 ${
      scrolled 
        ? "bg-white/95 dark:bg-[#09090B]/95 border-b border-[#E5E7EB] dark:border-white/10 shadow-xs py-3" 
        : "bg-transparent py-4"
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between relative">
        {/* Left Side Logo */}
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-2.5 cursor-pointer select-none">
            <div className="h-9 w-9 rounded-lg bg-[#0F172A] dark:bg-zinc-100 flex items-center justify-center text-white dark:text-[#09090B] font-extrabold text-lg">
              D
            </div>
            <span className="font-bold text-lg tracking-tight text-[#0F172A] dark:text-zinc-50 font-serif">
              Dealer Discovery
            </span>
          </div>

          {/* Categories megamenu desktop */}
          <div className="hidden md:block relative">
            <button
              onClick={() => setIsCatOpen(!isCatOpen)}
              className="inline-flex items-center gap-1 text-sm font-semibold text-slate-650 dark:text-zinc-350 hover:text-[#2563EB] dark:hover:text-indigo-400 transition-colors cursor-pointer"
            >
              Categories
              <ChevronDown className={`h-4 w-4 transition-transform duration-200 ${isCatOpen ? "rotate-180" : ""}`} />
            </button>
            <CategoryDropdown isOpen={isCatOpen} onSelect={(c) => { onSelectCategory(c); setIsCatOpen(false); }} />
          </div>
        </div>

        {/* Desktop Links */}
        <nav className="hidden md:flex items-center gap-6 text-sm font-semibold text-slate-650 dark:text-zinc-350">
          <span className="hover:text-[#2563EB] dark:hover:text-indigo-400 cursor-pointer transition-colors">Categories</span>
          <span className="hover:text-[#2563EB] dark:hover:text-indigo-400 cursor-pointer transition-colors">Brands</span>
          <span className="hover:text-[#2563EB] dark:hover:text-indigo-400 cursor-pointer transition-colors">Dealers</span>
          <span className="hover:text-[#2563EB] dark:hover:text-indigo-400 cursor-not-allowed opacity-40">About</span>
          <span className="hover:text-[#2563EB] dark:hover:text-indigo-400 cursor-not-allowed opacity-40">Contact</span>
        </nav>

        {/* Right Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={onSearchClick}
            className="p-2 rounded-[12px] border border-[#E5E7EB] dark:border-white/10 hover:bg-slate-50 dark:hover:bg-zinc-900 text-slate-600 dark:text-zinc-300 cursor-pointer transition-colors"
            aria-label="Search"
          >
            <Search className="h-4 w-4" />
          </button>
          
          <button
            onClick={toggleTheme}
            className="p-2 rounded-[12px] border border-[#E5E7EB] dark:border-white/10 hover:bg-slate-50 dark:hover:bg-zinc-900 cursor-pointer transition-colors"
            aria-label="Toggle Theme"
          >
            {isDarkMode ? <Sun className="h-4 w-4 text-amber-500" /> : <Moon className="h-4 w-4 text-slate-600" />}
          </button>

          {/* Mobile Menu Trigger */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 rounded-[12px] border border-[#E5E7EB] dark:border-white/10 hover:bg-slate-55 dark:hover:bg-zinc-900 md:hidden cursor-pointer text-slate-655 dark:text-zinc-300"
          >
            {isMobileMenuOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t border-[#E5E7EB] dark:border-white/10 bg-white dark:bg-[#09090B] px-4 py-4 space-y-3 flex flex-col text-sm font-semibold text-slate-600 dark:text-zinc-300">
          <span className="hover:text-[#2563EB] dark:hover:text-indigo-400 cursor-pointer py-1.5">Categories</span>
          <span className="hover:text-[#2563EB] dark:hover:text-indigo-400 cursor-pointer py-1.5">Brands</span>
          <span className="hover:text-[#2563EB] dark:hover:text-indigo-400 cursor-pointer py-1.5">Dealers</span>
          <span className="opacity-40 py-1.5">About</span>
          <span className="opacity-40 py-1.5">Contact</span>
        </div>
      )}
    </header>
  );
}
