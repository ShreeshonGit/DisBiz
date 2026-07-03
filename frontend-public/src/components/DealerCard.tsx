"use client";

import React, { useState, useEffect } from "react";
import { 
  ShieldCheck, Phone, Mail, Globe, MapPin, 
  ExternalLink, Copy, Share2, Heart 
} from "lucide-react";

interface Dealer {
  id: string;
  brand_name: string;
  dealer_name: string;
  address: string;
  city: string;
  state: string;
  pincode: string;
  latitude?: number;
  longitude?: number;
  phone?: string;
  email?: string;
  website?: string;
  formatted_address?: string;
  quality_score: number;
  validation_status: "VALID" | "INVALID";
}

interface DealerCardProps {
  dealer: Dealer;
}

export default function DealerCard({ dealer }: DealerCardProps) {
  const [isFavorite, setIsFavorite] = useState(false);
  const [copyFeedback, setCopyFeedback] = useState("");
  const [shareFeedback, setShareFeedback] = useState(false);

  useEffect(() => {
    const favs = JSON.parse(localStorage.getItem("dealer_favorites") || "[]");
    setIsFavorite(favs.includes(dealer.id));
  }, [dealer.id]);

  const toggleFavorite = (e: React.MouseEvent) => {
    e.stopPropagation();
    const favs = JSON.parse(localStorage.getItem("dealer_favorites") || "[]");
    let updated;
    if (favs.includes(dealer.id)) {
      updated = favs.filter((id: string) => id !== dealer.id);
      setIsFavorite(false);
    } else {
      updated = [...favs, dealer.id];
      setIsFavorite(true);
    }
    localStorage.setItem("dealer_favorites", JSON.stringify(updated));
  };

  const copyAddress = (e: React.MouseEvent) => {
    e.stopPropagation();
    const addr = dealer.formatted_address || dealer.address;
    navigator.clipboard.writeText(addr);
    setCopyFeedback("Copied Address!");
    setTimeout(() => setCopyFeedback(""), 2000);
  };

  const shareDealer = (e: React.MouseEvent) => {
    e.stopPropagation();
    const shareUrl = `${window.location.origin}?query=${encodeURIComponent(dealer.dealer_name)}`;
    navigator.clipboard.writeText(shareUrl);
    setShareFeedback(true);
    setTimeout(() => setShareFeedback(false), 2000);
  };

  const mapUrl = dealer.latitude && dealer.longitude
    ? `https://www.google.com/maps/search/?api=1&query=${dealer.latitude},${dealer.longitude}`
    : null;

  return (
    <div className="group bg-white dark:bg-zinc-900 border border-slate-200/80 dark:border-zinc-800/80 rounded-2xl p-6 hover:shadow-lg dark:hover:shadow-black/25 transition-all duration-300 hover:-translate-y-0.5 flex flex-col justify-between relative overflow-hidden select-none">
      <div className="space-y-4">
        {/* Header Badges */}
        <div className="flex justify-between items-center text-[10px] font-bold uppercase tracking-wider">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-lg bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-300 border border-slate-200/40 dark:border-zinc-700/40">
            {dealer.brand_name}
          </span>
          <div className="flex items-center gap-2">
            <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-lg ${
              dealer.validation_status === "VALID"
                ? "bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-900/30"
                : "bg-red-50 dark:bg-red-950/20 text-red-600 dark:text-red-400 border border-red-100 dark:border-red-900/30"
            }`}>
              <ShieldCheck className="h-3 w-3" />
              {dealer.validation_status}
            </span>
            <button 
              onClick={toggleFavorite}
              className="p-1 rounded-md hover:bg-slate-50 dark:hover:bg-zinc-800 transition-colors"
            >
              <Heart className={`h-4.5 w-4.5 transition-colors ${isFavorite ? "fill-red-500 text-red-500" : "text-slate-400 dark:text-zinc-500 hover:text-red-500"}`} />
            </button>
          </div>
        </div>

        {/* Dealer Info */}
        <div className="space-y-1.5">
          <h3 className="text-base font-bold text-slate-900 dark:text-zinc-100 leading-snug group-hover:text-indigo-650 dark:group-hover:text-indigo-400 transition-colors">
            {dealer.dealer_name}
          </h3>
          <p className="text-xs text-slate-500 dark:text-zinc-400 leading-relaxed font-medium">
            {dealer.formatted_address || dealer.address}
          </p>
        </div>

        {/* Coordinates and Quality Score Grid */}
        <div className="text-[11px] font-semibold text-slate-500 dark:text-zinc-400 grid grid-cols-2 gap-x-4 gap-y-2 pb-1 border-t border-dashed border-slate-150 dark:border-zinc-800/80 pt-3.5">
          <div>
            <span className="text-[9px] text-slate-400 dark:text-zinc-500 block font-normal">Pincode</span>
            {dealer.pincode || "--"}
          </div>
          <div>
            <span className="text-[9px] text-slate-400 dark:text-zinc-500 block font-normal">Score</span>
            <span className="text-indigo-600 dark:text-indigo-400 font-bold">{dealer.quality_score}%</span>
          </div>
          {dealer.latitude && dealer.longitude && (
            <div className="col-span-2">
              <span className="text-[9px] text-slate-400 dark:text-zinc-500 block font-normal">GPS Location</span>
              {dealer.latitude.toFixed(5)}, {dealer.longitude.toFixed(5)}
            </div>
          )}
        </div>
      </div>

      {/* Footer Contact Row */}
      <div className="pt-4 border-t border-slate-100 dark:border-zinc-800/80 flex items-center justify-between mt-5 gap-2 text-xs">
        <div className="flex gap-2">
          {dealer.phone && (
            <a
              href={`tel:${dealer.phone}`}
              title="Call Dealer"
              className="p-2 rounded-xl border border-slate-200 dark:border-zinc-800 text-slate-600 dark:text-zinc-400 hover:bg-slate-50 dark:hover:bg-zinc-800 hover:text-slate-900 dark:hover:text-zinc-100 transition-all duration-200"
            >
              <Phone className="h-4 w-4" />
            </a>
          )}
          {dealer.email && (
            <a
              href={`mailto:${dealer.email}`}
              title="Email Dealer"
              className="p-2 rounded-xl border border-slate-200 dark:border-zinc-800 text-slate-600 dark:text-zinc-400 hover:bg-slate-50 dark:hover:bg-zinc-800 hover:text-slate-900 dark:hover:text-zinc-100 transition-all duration-200"
            >
              <Mail className="h-4 w-4" />
            </a>
          )}
          {dealer.website && (
            <a
              href={dealer.website}
              target="_blank"
              rel="noopener noreferrer"
              title="Visit Webpage"
              className="p-2 rounded-xl border border-slate-200 dark:border-zinc-800 text-slate-600 dark:text-zinc-400 hover:bg-slate-50 dark:hover:bg-zinc-800 hover:text-slate-900 dark:hover:text-zinc-100 transition-all duration-200"
            >
              <Globe className="h-4 w-4" />
            </a>
          )}
          <button
            onClick={copyAddress}
            title="Copy address to clipboard"
            className="p-2 rounded-xl border border-slate-200 dark:border-zinc-800 text-slate-600 dark:text-zinc-400 hover:bg-slate-50 dark:hover:bg-zinc-800 hover:text-slate-900 dark:hover:text-zinc-100 transition-all duration-200 relative"
          >
            <Copy className="h-4 w-4" />
            {copyFeedback && (
              <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1.5 px-2 py-0.5 rounded bg-zinc-900 text-zinc-100 text-[10px] whitespace-nowrap shadow font-bold">
                {copyFeedback}
              </span>
            )}
          </button>
          <button
            onClick={shareDealer}
            title="Copy share link"
            className="p-2 rounded-xl border border-slate-200 dark:border-zinc-800 text-slate-600 dark:text-zinc-400 hover:bg-slate-50 dark:hover:bg-zinc-800 hover:text-slate-900 dark:hover:text-zinc-100 transition-all duration-200 relative"
          >
            <Share2 className="h-4 w-4" />
            {shareFeedback && (
              <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1.5 px-2 py-0.5 rounded bg-zinc-900 text-zinc-100 text-[10px] whitespace-nowrap shadow font-bold">
                Link Copied!
              </span>
            )}
          </button>
        </div>

        {mapUrl && (
          <a
            href={mapUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-xs text-slate-650 dark:text-zinc-350 hover:text-indigo-600 dark:hover:text-indigo-400 font-bold transition-colors"
          >
            <MapPin className="h-4 w-4 text-rose-500" />
            <span>Navigate</span>
            <ExternalLink className="h-3 w-3 opacity-60" />
          </a>
        )}
      </div>
    </div>
  );
}
