"use client";

import React, { useState, useEffect } from "react";
import {
  LayoutDashboard,
  Award,
  Users,
  Cpu,
  FileCode,
  Settings as SettingsIcon,
  Menu,
  X,
  Sun,
  Moon,
  Database,
  Clock,
  ExternalLink
} from "lucide-react";
import BrandsManager from "@/components/BrandsManager";
import ScraperController from "@/components/ScraperController";

import Link from "next/link";

type Tab = "Dashboard" | "Brands" | "Dealers" | "Scraping" | "Automation" | "Logs" | "Settings";

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState<Tab>("Dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
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

  const navItems = [
    { name: "Dashboard" as Tab, icon: LayoutDashboard },
    { name: "Brands" as Tab, icon: Award },
    { name: "Dealers" as Tab, icon: Users },
    { name: "Scraping" as Tab, icon: Cpu },
    { name: "Automation" as Tab, icon: Clock },
    { name: "Logs" as Tab, icon: FileCode },
    { name: "Settings" as Tab, icon: SettingsIcon },
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-zinc-950 dark:text-zinc-100 flex transition-colors duration-300 font-sans">
      {/* Sidebar - Desktop */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 border-r border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 transition-transform duration-300 transform md:translate-x-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="h-16 flex items-center justify-between px-6 border-b border-slate-200 dark:border-zinc-800">
          <div className="flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-lg bg-zinc-950 dark:bg-zinc-100 flex items-center justify-center text-white dark:text-zinc-950 font-bold text-md shadow-sm">
              A
            </div>
            <span className="font-semibold text-base tracking-tight select-none">
              DDP Admin Portal
            </span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-1 rounded-md md:hidden hover:bg-slate-100 dark:hover:bg-zinc-800 text-slate-500 dark:text-zinc-400"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="p-4 space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.name;
            
            if (item.name === "Automation") {
              return (
                <Link
                  key={item.name}
                  href="/automation"
                  id={`sidebar-link-${item.name.toLowerCase()}`}
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 text-slate-650 dark:text-zinc-400 hover:bg-slate-50 dark:hover:bg-zinc-900 hover:text-slate-950 dark:hover:text-zinc-100"
                >
                  <Icon className="h-4.5 w-4.5 text-slate-400 dark:text-zinc-500" />
                  {item.name}
                </Link>
              );
            }
            
            return (
              <button
                key={item.name}
                id={`sidebar-link-${item.name.toLowerCase()}`}
                onClick={() => setActiveTab(item.name)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? "bg-slate-100 text-slate-900 dark:bg-zinc-800 dark:text-zinc-50 shadow-sm"
                    : "text-slate-650 dark:text-zinc-400 hover:bg-slate-50 dark:hover:bg-zinc-900 hover:text-slate-950 dark:hover:text-zinc-100"
                }`}
              >
                <Icon className={`h-4.5 w-4.5 ${isActive ? "text-slate-900 dark:text-zinc-50" : "text-slate-400 dark:text-zinc-500"}`} />
                {item.name}
              </button>
            );
          })}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-200 dark:border-zinc-800 bg-slate-50/50 dark:bg-zinc-900/50">
          <div className="flex items-center justify-between text-xs text-slate-400 dark:text-zinc-500">
            <span>Sprint 1 Base</span>
            <span className="flex items-center gap-1 font-semibold text-emerald-600 dark:text-emerald-500">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              API Ready
            </span>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className={`flex-grow md:pl-64 flex flex-col min-h-screen transition-all duration-300`}>
        {/* Top Header */}
        <header className="h-16 border-b border-slate-200 dark:border-zinc-800 bg-white/70 dark:bg-zinc-950/70 backdrop-blur-md sticky top-0 z-35 px-4 sm:px-6 flex items-center justify-between transition-colors duration-300">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-1.5 rounded-lg md:hidden border border-slate-200 dark:border-zinc-800 hover:bg-slate-100 dark:hover:bg-zinc-800 text-slate-500 dark:text-zinc-400"
            >
              <Menu className="h-5 w-5" />
            </button>
            <h2 className="text-md font-semibold tracking-tight text-slate-700 dark:text-zinc-300 select-none">
              {activeTab}
            </h2>
          </div>

          <div className="flex items-center gap-3">
            {/* View Landing Page Shortcut */}
            <a
              href="http://localhost:3002"
              target="_blank"
              rel="noopener noreferrer"
              className="hidden sm:inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-800 dark:text-zinc-400 dark:hover:text-zinc-200 border border-slate-200 dark:border-zinc-800 px-3 py-1.5 rounded-lg bg-slate-50/50 dark:bg-zinc-900/50 transition-colors"
            >
              <span>View Public App</span>
              <ExternalLink className="h-3 w-3" />
            </a>

            {/* Dark Mode Toggle */}
            <button
              id="admin-theme-toggle-btn"
              onClick={toggleTheme}
              className="p-2 rounded-lg border border-slate-200 dark:border-zinc-800 hover:bg-slate-100 dark:hover:bg-zinc-900 transition-colors"
              aria-label="Toggle Theme"
            >
              {isDarkMode ? <Sun className="h-4.5 w-4.5 text-amber-400" /> : <Moon className="h-4.5 w-4.5 text-slate-600" />}
            </button>
          </div>
        </header>

        {/* Dynamic Page Container */}
        <main className="flex-grow p-4 sm:p-8 max-w-6xl w-full mx-auto relative z-10">
          {activeTab === "Dashboard" && (
            <div className="space-y-8 animate-fade-in">
              {/* Header and Welcome */}
              <div className="border-b border-slate-200 dark:border-zinc-800 pb-6">
                <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-zinc-50 mb-2">
                  Welcome to Dealer Discovery Admin
                </h1>
                <p className="text-slate-600 dark:text-zinc-400">
                  This is the control panel for monitoring crawled brands, managing verified dealers list, and configuring scraping tasks.
                </p>
              </div>

              {/* Metric Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Metric 1 */}
                <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-5 hover:shadow-sm transition-all duration-200">
                  <div className="flex justify-between items-start mb-4">
                    <span className="text-xs font-semibold text-slate-500 dark:text-zinc-500 uppercase tracking-wider">
                      Monitored Brands
                    </span>
                    <Award className="h-5 w-5 text-slate-400 dark:text-zinc-500" />
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-bold text-slate-900 dark:text-zinc-50">0</span>
                    <span className="text-xs text-slate-400 dark:text-zinc-500">Brands Loaded</span>
                  </div>
                </div>

                {/* Metric 2 */}
                <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-5 hover:shadow-sm transition-all duration-200">
                  <div className="flex justify-between items-start mb-4">
                    <span className="text-xs font-semibold text-slate-500 dark:text-zinc-500 uppercase tracking-wider">
                      Verified Outlets
                    </span>
                    <Users className="h-5 w-5 text-slate-400 dark:text-zinc-500" />
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-bold text-slate-900 dark:text-zinc-50">0</span>
                    <span className="text-xs text-slate-400 dark:text-zinc-500">Dealers Audited</span>
                  </div>
                </div>

                {/* Metric 3 */}
                <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-5 hover:shadow-sm transition-all duration-200">
                  <div className="flex justify-between items-start mb-4">
                    <span className="text-xs font-semibold text-slate-500 dark:text-zinc-500 uppercase tracking-wider">
                      Scraper Status
                    </span>
                    <Cpu className="h-5 w-5 text-slate-400 dark:text-zinc-500" />
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-lg font-bold text-slate-900 dark:text-zinc-50 uppercase tracking-tight">
                      Idle
                    </span>
                    <span className="text-xs text-slate-400 dark:text-zinc-500">0 Running Tasks</span>
                  </div>
                </div>

                {/* Metric 4 */}
                <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-5 hover:shadow-sm transition-all duration-200">
                  <div className="flex justify-between items-start mb-4">
                    <span className="text-xs font-semibold text-slate-500 dark:text-zinc-500 uppercase tracking-wider">
                      DB Connection
                    </span>
                    <Database className="h-5 w-5 text-slate-400 dark:text-zinc-500" />
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-sm font-semibold text-emerald-600 dark:text-emerald-500 uppercase tracking-tight">
                      Configured
                    </span>
                    <span className="text-xs text-slate-400 dark:text-zinc-500">Supabase</span>
                  </div>
                </div>
              </div>

              {/* Status Section */}
              <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-6">
                <h3 className="text-md font-semibold text-slate-900 dark:text-zinc-50 mb-4 flex items-center gap-2">
                  <Clock className="h-4.5 w-4.5 text-slate-400 dark:text-zinc-500" />
                  Latest System Activity
                </h3>
                <div className="space-y-4">
                  <div className="flex items-start gap-4 text-sm border-b border-slate-100 dark:border-zinc-800 pb-3">
                    <span className="text-xs text-slate-400 dark:text-zinc-500 bg-slate-100 dark:bg-zinc-800 px-2 py-0.5 rounded whitespace-nowrap">
                      19:08:46
                    </span>
                    <div>
                      <p className="font-medium text-slate-800 dark:text-zinc-300">Sprint 1 Project Initialized</p>
                      <p className="text-xs text-slate-500 dark:text-zinc-500">Successfully set up public and admin Next.js 15 apps and FastAPI modular backend.</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-4 text-sm pb-1">
                    <span className="text-xs text-slate-400 dark:text-zinc-500 bg-slate-100 dark:bg-zinc-800 px-2 py-0.5 rounded whitespace-nowrap">
                      System
                    </span>
                    <div>
                      <p className="font-medium text-slate-800 dark:text-zinc-300">Database Connection Client Active</p>
                      <p className="text-xs text-slate-500 dark:text-zinc-500">Supabase SDK ready for table definition and CRUD operations in Sprint 2.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "Brands" && (
            <div className="animate-fade-in">
              <BrandsManager />
            </div>
          )}

          {activeTab === "Dealers" && (
            <div className="space-y-6 animate-fade-in">
              <div className="border-b border-slate-200 dark:border-zinc-800 pb-6">
                <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-zinc-50 mb-2">
                  Authorized Dealers & Distributors
                </h1>
                <p className="text-slate-600 dark:text-zinc-400">
                  Verify and edit addresses, phone numbers, website links, and coordinates of registered brand outlets.
                </p>
              </div>
              <div className="border border-dashed border-slate-300 dark:border-zinc-800 rounded-2xl p-16 text-center max-w-xl mx-auto">
                <Users className="h-12 w-12 text-slate-300 dark:text-zinc-700 mx-auto mb-4" />
                <h3 className="font-semibold text-slate-800 dark:text-zinc-200 mb-1">Dealers Directory Empty</h3>
                <p className="text-sm text-slate-500 dark:text-zinc-500 mb-6">Imported dealers from web scraping jobs will appear here for verification.</p>
                <button disabled className="bg-slate-200 text-slate-400 dark:bg-zinc-800 dark:text-zinc-600 px-4 py-2 rounded-lg text-xs font-semibold select-none cursor-not-allowed">
                  New Dealer Entry (Sprint 2)
                </button>
              </div>
            </div>
          )}

          {activeTab === "Scraping" && (
            <div className="animate-fade-in">
              <ScraperController />
            </div>
          )}

          {activeTab === "Logs" && (
            <div className="space-y-6 animate-fade-in">
              <div className="border-b border-slate-200 dark:border-zinc-800 pb-6">
                <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-zinc-50 mb-2">
                  System Logs
                </h1>
                <p className="text-slate-600 dark:text-zinc-400">
                  Review historical error alerts, API traffic logs, and crawler diagnostics reports.
                </p>
              </div>
              <div className="bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-5 font-mono text-xs text-slate-700 dark:text-zinc-400 leading-relaxed shadow-sm">
                <p className="text-slate-400 dark:text-zinc-600">[2026-07-03 19:08:46] INFO: Initializing Sprint 1 Framework components...</p>
                <p className="text-slate-400 dark:text-zinc-600">[2026-07-03 19:08:54] INFO: Next.js 15 app router initialized at D:\DisBiz\dealer-discovery-platform\frontend-public</p>
                <p className="text-slate-400 dark:text-zinc-600">[2026-07-03 19:10:28] INFO: Next.js 15 app router initialized at D:\DisBiz\dealer-discovery-platform\frontend-admin</p>
                <p className="text-slate-400 dark:text-zinc-600">[2026-07-03 19:13:29] INFO: FastAPI application configured under D:\DisBiz\dealer-discovery-platform\backend</p>
                <p className="text-slate-400 dark:text-zinc-600">[2026-07-03 19:13:38] WARN: Supabase connection details missing. Supabase Client in standby mode.</p>
                <p className="text-emerald-600 dark:text-emerald-400">[2026-07-03 19:14:01] SUCCESS: API server health check configured at GET /health. Response: {"{\"status\": \"ok\"}"}</p>
                <p className="text-emerald-600 dark:text-emerald-400">[2026-07-03 19:14:48] SUCCESS: Sprint 1 codebase compiled and validated without error.</p>
              </div>
            </div>
          )}

          {activeTab === "Settings" && (
            <div className="space-y-8 animate-fade-in">
              <div className="border-b border-slate-200 dark:border-zinc-800 pb-6">
                <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-zinc-50 mb-2">
                  Console Settings
                </h1>
                <p className="text-slate-600 dark:text-zinc-400">
                  Update environment configurations, API integrations, and database access settings.
                </p>
              </div>
              
              <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-6 space-y-6">
                <div>
                  <h3 className="text-sm font-semibold text-slate-800 dark:text-zinc-200 mb-1">Backend Connection URL</h3>
                  <p className="text-xs text-slate-500 dark:text-zinc-500 mb-3">Target API endpoint for standard requests.</p>
                  <input
                    disabled
                    type="text"
                    value="http://localhost:8000"
                    className="w-full bg-slate-50 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 rounded-lg p-2.5 text-sm text-slate-500 dark:text-zinc-400 cursor-not-allowed"
                  />
                </div>
                
                <div>
                  <h3 className="text-sm font-semibold text-slate-800 dark:text-zinc-200 mb-1">Supabase API Key Status</h3>
                  <p className="text-xs text-slate-500 dark:text-zinc-500 mb-3">Client configuration key status.</p>
                  <div className="inline-flex items-center gap-2 text-xs bg-amber-500/10 text-amber-600 dark:text-amber-500 border border-amber-500/20 px-3 py-1.5 rounded-lg">
                    <span>Standby (Using placeholder credentials)</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
