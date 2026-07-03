"use client";

import React, { useState } from "react";
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

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/80 dark:border-zinc-800/80 bg-white/70 dark:bg-zinc-950/70 backdrop-blur-md transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between relative">
        {/* Left Side Logo & Categories */}
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-2.5 cursor-pointer select-none">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-indigo-500 to-blue-600 flex items-center justify-center text-white font-bold text-lg shadow-md shadow-blue-500/20">
              D
            </div>
            <span className="font-bold text-lg tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-slate-900 via-slate-800 to-slate-650 dark:from-zinc-50 dark:via-zinc-200 dark:to-zinc-450">
              Dealer Discovery
            </span>
          </div>

          {/* Categories Megamenu trigger */}
          <div className="hidden md:block relative">
            <button
              onClick={() => setIsCatOpen(!isCatOpen)}
              className="inline-flex items-center gap-1.5 text-sm font-semibold text-slate-600 dark:text-zinc-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors duration-200 cursor-pointer"
            >
              Categories
              <ChevronDown className={`h-4 w-4 transition-transform duration-250 ${isCatOpen ? "rotate-180" : ""}`} />
            </button>
            <CategoryDropdown isOpen={isCatOpen} onSelect={(c) => { onSelectCategory(c); setIsCatOpen(false); }} />
          </div>
        </div>

        {/* Desktop Navigation Links */}
        <nav className="hidden md:flex items-center gap-6 text-sm font-semibold text-slate-600 dark:text-zinc-300">
          <span className="hover:text-indigo-600 dark:hover:text-indigo-400 cursor-pointer transition-colors duration-200">Home</span>
          <span onClick={() => setIsCatOpen(!isCatOpen)} className="hover:text-indigo-600 dark:hover:text-indigo-400 cursor-pointer transition-colors duration-200">Categories</span>
          <span className="hover:text-indigo-600 dark:hover:text-indigo-400 cursor-pointer transition-colors duration-200">Brands</span>
          <span className="hover:text-indigo-600 dark:hover:text-indigo-400 cursor-pointer transition-colors duration-200">Dealers</span>
          <span className="hover:text-indigo-600 dark:hover:text-indigo-400 cursor-not-allowed opacity-50">About</span>
          <span className="hover:text-indigo-600 dark:hover:text-indigo-400 cursor-not-allowed opacity-50">Contact</span>
        </nav>

        {/* Right Actions */}
        <div className="flex items-center gap-3">
          <button
            onClick={onSearchClick}
            className="p-2 rounded-xl border border-slate-200 dark:border-zinc-800 hover:bg-slate-100 dark:hover:bg-zinc-900 text-slate-600 dark:text-zinc-300 cursor-pointer transition-all duration-200"
            aria-label="Search"
          >
            <Search className="h-4.5 w-4.5" />
          </button>
          
          <button
            onClick={toggleTheme}
            className="p-2 rounded-xl border border-slate-200 dark:border-zinc-800 hover:bg-slate-100 dark:hover:bg-zinc-900 cursor-pointer transition-all duration-200"
            aria-label="Toggle Theme"
          >
            {isDarkMode ? <Sun className="h-4.5 w-4.5 text-amber-450" /> : <Moon className="h-4.5 w-4.5 text-slate-650" />}
          </button>

          {/* Mobile Menu Toggle */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 rounded-xl border border-slate-200 dark:border-zinc-800 hover:bg-slate-100 dark:hover:bg-zinc-900 md:hidden cursor-pointer text-slate-600 dark:text-zinc-300"
          >
            {isMobileMenuOpen ? <X className="h-4.5 w-4.5" /> : <Menu className="h-4.5 w-4.5" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Navigation */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 px-4 py-4 space-y-3 flex flex-col text-sm font-semibold text-slate-600 dark:text-zinc-300">
          <span className="hover:text-indigo-600 dark:hover:text-indigo-400 cursor-pointer py-1.5">Home</span>
          <span className="hover:text-indigo-600 dark:hover:text-indigo-400 cursor-pointer py-1.5" onClick={() => { setIsCatOpen(!isCatOpen); setIsMobileMenuOpen(false); }}>Categories</span>
          <span className="hover:text-indigo-600 dark:hover:text-indigo-400 cursor-pointer py-1.5">Brands</span>
          <span className="hover:text-indigo-600 dark:hover:text-indigo-400 cursor-pointer py-1.5">Dealers</span>
          <span className="opacity-50 py-1.5">About</span>
          <span className="opacity-50 py-1.5">Contact</span>
        </div>
      )}
    </header>
  );
}
