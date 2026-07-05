"use client";

import React, { useState, useEffect } from "react";
import { 
  ShieldCheck, Phone, Globe, MapPin, 
  ExternalLink, Copy, Heart, CheckCircle2 
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
    setCopyFeedback("Copied!");
    setTimeout(() => setCopyFeedback(""), 2000);
  };

  const mapUrl = dealer.latitude && dealer.longitude
    ? `https://www.google.com/maps/search/?api=1&query=${dealer.latitude},${dealer.longitude}`
    : null;

  return (
    <div className="bg-white dark:bg-zinc-900 border border-[#E5E7EB] dark:border-zinc-800 rounded-[16px] p-6 hover:shadow-md transition-all duration-200 flex flex-col justify-between select-none shadow-xs hover:-translate-y-0.5">
      <div className="space-y-4">
        {/* Hierarchy 1: Dealer Name */}
        <h3 className="text-base font-bold text-[#0F172A] dark:text-zinc-150 font-serif leading-snug">
          {dealer.dealer_name}
        </h3>

        {/* Hierarchy 2: Status Indicator */}
        <div className="flex flex-wrap items-center gap-2 text-[10px] font-bold uppercase tracking-wider">
          <span className="inline-flex items-center px-2 py-0.5 rounded-[12px] bg-slate-50 dark:bg-zinc-800 text-slate-500 dark:text-zinc-350 border border-[#E5E7EB] dark:border-zinc-700">
            {dealer.brand_name}
          </span>
          <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-[12px] ${
            dealer.validation_status === "VALID"
              ? "bg-emerald-50 dark:bg-emerald-950/20 text-[#10B981] dark:text-emerald-400 border border-emerald-100/60 dark:border-emerald-900/20"
              : "bg-red-50 dark:bg-red-950/20 text-red-650 dark:text-red-400 border border-red-100/60 dark:border-red-900/20"
          }`}>
            <ShieldCheck className="h-3 w-3" />
            {dealer.validation_status === "VALID" ? "Verified Partner" : "Pending Audit"}
          </span>
        </div>

        {/* Hierarchy 3: Address */}
        <p className="text-xs text-slate-500 dark:text-zinc-400 leading-relaxed min-h-[36px]">
          {dealer.formatted_address || dealer.address}
        </p>

        {/* Hierarchy 4: Contact details or visual separator */}
        <div className="border-t border-dashed border-[#E5E7EB] dark:border-zinc-800 pt-3" />

        {/* Hierarchy 5: Metadata (Zip & Quality score) */}
        <div className="grid grid-cols-2 gap-4 pb-1">
          <div>
            <span className="text-[9px] text-slate-400 dark:text-zinc-500 block font-semibold uppercase tracking-wider">Pincode / Zip</span>
            <span className="text-xs font-bold text-slate-700 dark:text-zinc-300">{dealer.pincode || "--"}</span>
          </div>
          <div>
            <span className="text-[9px] text-slate-400 dark:text-zinc-500 block font-semibold uppercase tracking-wider">Confidence Score</span>
            <span className="inline-flex items-center gap-0.5 text-xs font-extrabold text-[#2563EB] dark:text-indigo-400">
              <CheckCircle2 className="h-3 w-3 text-[#10B981]" />
              {dealer.quality_score}%
            </span>
          </div>
        </div>
      </div>

      {/* Hierarchy 6: Actions (Dominant Directions, muted secondary) */}
      <div className="pt-4 border-t border-[#E5E7EB] dark:border-zinc-800 flex items-center justify-between mt-5 gap-2 text-xs">
        <div className="flex items-center gap-1">
          {/* Call */}
          {dealer.phone && (
            <a
              href={`tel:${dealer.phone}`}
              title="Call Partner"
              className="p-2.5 rounded-[12px] border border-[#E5E7EB] dark:border-zinc-800 text-slate-650 dark:text-zinc-400 hover:bg-slate-50 dark:hover:bg-zinc-850 hover:text-slate-900 dark:hover:text-zinc-100 transition-colors"
            >
              <Phone className="h-3.5 w-3.5" />
            </a>
          )}
          
          {/* Website */}
          {dealer.website && (
            <a
              href={dealer.website}
              target="_blank"
              rel="noopener noreferrer"
              title="Visit Webpage"
              className="p-2.5 rounded-[12px] border border-[#E5E7EB] dark:border-zinc-800 text-slate-650 dark:text-zinc-400 hover:bg-slate-50 dark:hover:bg-zinc-855 hover:text-slate-900 dark:hover:text-zinc-100 transition-colors"
            >
              <Globe className="h-3.5 w-3.5" />
            </a>
          )}
          
          {/* Copy Address */}
          <button
            onClick={copyAddress}
            title="Copy address"
            className="p-2.5 rounded-[12px] border border-[#E5E7EB] dark:border-zinc-800 text-slate-655 dark:text-zinc-400 hover:bg-slate-50 dark:hover:bg-zinc-855 hover:text-slate-900 dark:hover:text-zinc-100 transition-colors relative"
          >
            <Copy className="h-3.5 w-3.5" />
            {copyFeedback && (
              <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1.5 px-2 py-0.5 rounded bg-zinc-900 text-zinc-100 text-[10px] whitespace-nowrap shadow font-bold">
                {copyFeedback}
              </span>
            )}
          </button>

          {/* Save (Favorite) */}
          <button
            onClick={toggleFavorite}
            title={isFavorite ? "Remove from Favorites" : "Save to Favorites"}
            className="p-2.5 rounded-[12px] border border-[#E5E7EB] dark:border-zinc-800 text-slate-655 dark:text-zinc-400 hover:bg-slate-50 dark:hover:bg-zinc-855 hover:text-slate-900 dark:hover:text-zinc-100 transition-colors"
          >
            <Heart className={`h-3.5 w-3.5 transition-colors ${isFavorite ? "fill-red-500 text-red-500 border-transparent" : "text-slate-400 dark:text-zinc-550"}`} />
          </button>
        </div>

        {/* Dominant DIRECTIONS CTA */}
        {mapUrl ? (
          <a
            href={mapUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-[12px] bg-[#2563EB] hover:bg-blue-700 text-xs font-bold text-white transition-colors shadow-xs"
          >
            <MapPin className="h-3.5 w-3.5" />
            <span>Directions</span>
            <ExternalLink className="h-3 w-3 opacity-80" />
          </a>
        ) : (
          <span className="text-[10px] text-slate-400 italic">No coordinates</span>
        )}
      </div>
    </div>
  );
}
