"use client";

import React from "react";
import { Heart, HelpCircle, FileText } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 dark:border-zinc-800 bg-white/50 dark:bg-zinc-950/50 py-12 transition-colors duration-300 font-sans select-none">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8">
          
          {/* Logo & Description */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-indigo-500 to-blue-600 flex items-center justify-center text-white font-bold text-base shadow-sm">
                D
              </div>
              <span className="font-bold text-base tracking-tight text-slate-900 dark:text-zinc-50">
                Dealer Discovery
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-zinc-400 leading-relaxed font-medium">
              Connecting customers with authorized brand dealers, distributor offices, and repair centers across India.
            </p>
            <div className="flex gap-4.5 text-slate-400 dark:text-zinc-500 items-center">
              <span className="hover:text-indigo-600 dark:hover:text-indigo-400 cursor-not-allowed">
                <svg className="h-4 w-4 fill-current" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                </svg>
              </span>
              <span className="hover:text-indigo-600 dark:hover:text-indigo-400 cursor-not-allowed">
                <svg className="h-4 w-4 fill-current" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0z" />
                </svg>
              </span>
              <a 
                href="https://github.com" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
              >
                <svg className="h-4 w-4 fill-current" viewBox="0 0 24 24" aria-hidden="true">
                  <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.464-1.11-1.464-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.579.688.481C19.138 20.161 22 16.416 22 12c0-5.523-4.477-10-10-10z" />
                </svg>
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-slate-400 dark:text-zinc-505 uppercase tracking-wider">Quick Links</h4>
            <ul className="space-y-2 text-xs font-semibold text-slate-500 dark:text-zinc-400">
              <li className="hover:text-indigo-650 dark:hover:text-indigo-400 cursor-pointer">Home</li>
              <li className="hover:text-indigo-650 dark:hover:text-indigo-400 cursor-pointer">Brands Catalog</li>
              <li className="hover:text-indigo-650 dark:hover:text-indigo-400 cursor-pointer">Partners Grid</li>
              <li className="opacity-50 cursor-not-allowed">About Us</li>
              <li className="opacity-50 cursor-not-allowed">Contact</li>
            </ul>
          </div>

          {/* Categories Grid */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-slate-400 dark:text-zinc-505 uppercase tracking-wider">Categories</h4>
            <ul className="space-y-2 text-xs font-semibold text-slate-500 dark:text-zinc-400">
              <li className="hover:text-indigo-650 dark:hover:text-indigo-400 cursor-pointer">Electronics</li>
              <li className="hover:text-indigo-650 dark:hover:text-indigo-400 cursor-pointer">Furniture</li>
              <li className="hover:text-indigo-650 dark:hover:text-indigo-400 cursor-pointer">Automotive</li>
              <li className="hover:text-indigo-650 dark:hover:text-indigo-400 cursor-pointer">Healthcare</li>
              <li className="hover:text-indigo-650 dark:hover:text-indigo-400 cursor-pointer">Building Materials</li>
            </ul>
          </div>

          {/* Support */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-slate-400 dark:text-zinc-505 uppercase tracking-wider">Legal & Support</h4>
            <ul className="space-y-2 text-xs font-semibold text-slate-500 dark:text-zinc-400">
              <li className="hover:text-indigo-650 dark:hover:text-indigo-400 cursor-not-allowed inline-flex items-center gap-1.5">
                <FileText className="h-3.5 w-3.5" /> Privacy Policy
              </li>
              <li className="hover:text-indigo-650 dark:hover:text-indigo-400 cursor-not-allowed inline-flex items-center gap-1.5">
                <FileText className="h-3.5 w-3.5" /> Terms of Service
              </li>
              <li>
                <a 
                  href="http://localhost:3001" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="hover:text-indigo-650 dark:hover:text-indigo-400 underline inline-flex items-center gap-1.5"
                >
                  <HelpCircle className="h-3.5 w-3.5" /> Admin Console
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Copyright */}
        <div className="pt-8 border-t border-slate-150 dark:border-zinc-900 mt-10 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 dark:text-zinc-500 gap-4">
          <p>&copy; 2026 Dealer Discovery Platform. Verified Listings. Sprint 3.5 Stable.</p>
          <p className="inline-flex items-center gap-1">
            Made with <Heart className="h-3 w-3 fill-rose-500 text-rose-500" /> in India
          </p>
        </div>
      </div>
    </footer>
  );
}
