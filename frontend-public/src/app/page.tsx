"use client";

import React, { useState, useEffect } from "react";
import { Search, ShieldCheck, MapPin, Globe, Moon, Sun, Lock } from "lucide-react";

export default function Home() {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    // Check local storage or system preference
    const storedTheme = localStorage.getItem("theme");
    const systemPrefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    
    if (storedTheme === "dark" || (!storedTheme && systemPrefersDark)) {
      setIsDarkMode(true);
      document.documentElement.classList.add("dark");
    } else {
      setIsDarkMode(false);
      document.documentElement.classList.remove("dark");
    }
  }, []);

  const toggleTheme = () => {
    if (isDarkMode) {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
      setIsDarkMode(false);
    } else {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
      setIsDarkMode(true);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-zinc-950 dark:text-zinc-50 transition-colors duration-300 flex flex-col font-sans">
      {/* Background Decorative Grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:14px_24px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none" />

      {/* Navigation */}
      <header className="sticky top-0 z-50 border-b border-slate-200/80 dark:border-zinc-800/80 bg-white/70 dark:bg-zinc-950/70 backdrop-blur-md transition-colors duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="h-9 w-9 rounded-lg bg-zinc-900 dark:bg-zinc-100 flex items-center justify-center text-white dark:text-zinc-900 font-bold text-lg shadow-sm">
              D
            </div>
            <span className="font-semibold text-lg tracking-tight select-none">
              Dealer Discovery Platform
            </span>
          </div>

          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600 dark:text-zinc-400">
            <a href="#features" className="hover:text-slate-950 dark:hover:text-zinc-50 transition-colors">Features</a>
            <a href="#about" className="hover:text-slate-950 dark:hover:text-zinc-50 transition-colors">How It Works</a>
            <span className="text-slate-300 dark:text-zinc-800">|</span>
            <span className="flex items-center gap-1.5 text-slate-400 dark:text-zinc-600 cursor-not-allowed">
              <Lock className="h-3 w-3" />
              API Docs
            </span>
          </nav>

          <div className="flex items-center gap-4">
            <button
              id="theme-toggle-btn"
              onClick={toggleTheme}
              className="p-2 rounded-lg border border-slate-200 dark:border-zinc-800 hover:bg-slate-100 dark:hover:bg-zinc-900 transition-colors"
              aria-label="Toggle Theme"
            >
              {isDarkMode ? <Sun className="h-4.5 w-4.5 text-amber-400" /> : <Moon className="h-4.5 w-4.5 text-slate-600" />}
            </button>
            
            <a
              id="admin-console-link"
              href="http://localhost:3001"
              target="_blank"
              rel="noopener noreferrer"
              className="hidden sm:inline-flex items-center justify-center text-xs font-medium bg-zinc-900 text-zinc-50 hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200 px-4 py-2 rounded-lg shadow-sm transition-colors"
            >
              Admin Portal
            </a>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-grow flex flex-col justify-center max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28 relative z-10">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-xs font-medium text-slate-600 dark:text-zinc-400 mb-6 animate-fade-in">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Sprint 1: Architecture Established
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-slate-900 dark:text-zinc-50 mb-6 leading-[1.15]">
            Find Official <br className="sm:hidden" />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-500 dark:from-zinc-50 dark:to-zinc-500">
              Authorized Dealers
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-slate-600 dark:text-zinc-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Search for official dealers and distributors of your favorite brands across India.
          </p>

          {/* Disabled Search Bar */}
          <div className="max-w-xl mx-auto relative group">
            <div className="absolute -inset-1 rounded-xl bg-slate-200 dark:bg-zinc-800 opacity-25 group-hover:opacity-40 blur transition duration-300" />
            <div className="relative flex items-center bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl shadow-md p-2">
              <Search className="h-5 w-5 text-slate-400 dark:text-zinc-600 ml-3 flex-shrink-0" />
              <input
                id="landing-search-input"
                type="text"
                disabled
                placeholder="Search brands (e.g. Sony, Apple, Samsung)..."
                className="w-full bg-transparent border-0 focus:ring-0 focus:outline-none text-slate-400 dark:text-zinc-600 px-3 py-2 cursor-not-allowed select-none text-sm"
              />
              <button
                id="landing-search-btn"
                disabled
                className="bg-slate-100 text-slate-400 dark:bg-zinc-800 dark:text-zinc-600 px-4 py-2 rounded-lg text-xs font-semibold select-none cursor-not-allowed whitespace-nowrap"
              >
                Search
              </button>
            </div>
            <p className="text-xs text-slate-400 dark:text-zinc-500 mt-3 text-center">
              * Search capability will launch in Sprint 2.
            </p>
          </div>
        </div>

        {/* Feature Cards Grid */}
        <section id="features" className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-12">
          {/* Card 1 */}
          <div className="group bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-2xl p-8 hover:shadow-lg dark:hover:shadow-black/20 hover:-translate-y-1 transition-all duration-300">
            <div className="h-12 w-12 rounded-xl bg-slate-50 dark:bg-zinc-800 border border-slate-100 dark:border-zinc-700 flex items-center justify-center mb-6 group-hover:bg-slate-100 dark:group-hover:bg-zinc-700 transition-colors">
              <ShieldCheck className="h-6 w-6 text-slate-800 dark:text-zinc-200" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900 dark:text-zinc-100 mb-2">
              100% Authorized Networks
            </h3>
            <p className="text-sm text-slate-600 dark:text-zinc-400 leading-relaxed">
              Verify sellers directly from official brand lists to guarantee genuine products and official warranties.
            </p>
          </div>

          {/* Card 2 */}
          <div className="group bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-2xl p-8 hover:shadow-lg dark:hover:shadow-black/20 hover:-translate-y-1 transition-all duration-300">
            <div className="h-12 w-12 rounded-xl bg-slate-50 dark:bg-zinc-800 border border-slate-100 dark:border-zinc-700 flex items-center justify-center mb-6 group-hover:bg-slate-100 dark:group-hover:bg-zinc-700 transition-colors">
              <MapPin className="h-6 w-6 text-slate-800 dark:text-zinc-200" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900 dark:text-zinc-100 mb-2">
              Pan-India Coverage
            </h3>
            <p className="text-sm text-slate-600 dark:text-zinc-400 leading-relaxed">
              Discover distributors, wholesalers, and physical retail outlets spanning all Indian states and major cities.
            </p>
          </div>

          {/* Card 3 */}
          <div className="group bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-2xl p-8 hover:shadow-lg dark:hover:shadow-black/20 hover:-translate-y-1 transition-all duration-300">
            <div className="h-12 w-12 rounded-xl bg-slate-50 dark:bg-zinc-800 border border-slate-100 dark:border-zinc-700 flex items-center justify-center mb-6 group-hover:bg-slate-100 dark:group-hover:bg-zinc-700 transition-colors">
              <Globe className="h-6 w-6 text-slate-800 dark:text-zinc-200" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900 dark:text-zinc-100 mb-2">
              Modular Architecture
            </h3>
            <p className="text-sm text-slate-600 dark:text-zinc-400 leading-relaxed">
              Built on a decoupled stack featuring Next.js 15, FastAPI, and Supabase for speed and scalability.
            </p>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 dark:border-zinc-800 bg-white/50 dark:bg-zinc-950/50 py-12 transition-colors duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-6">
          <p className="text-xs text-slate-500 dark:text-zinc-500">
            &copy; 2026 Dealer Discovery Platform. All rights reserved. Sprint 1 Release.
          </p>
          <div className="flex gap-6 text-xs text-slate-500 dark:text-zinc-400">
            <span className="hover:text-slate-800 dark:hover:text-zinc-200 cursor-not-allowed">Terms</span>
            <span className="hover:text-slate-800 dark:hover:text-zinc-200 cursor-not-allowed">Privacy</span>
            <a href="http://localhost:3001" target="_blank" rel="noopener noreferrer" className="hover:text-slate-800 dark:hover:text-zinc-200 underline">Admin Console</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
