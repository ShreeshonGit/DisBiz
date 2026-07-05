"use client";

import React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface PaginationProps {
  page: number;
  totalPages: number;
  totalItems: number;
  onPageChange: (newPage: number) => void;
}

export default function Pagination({
  page,
  totalPages,
  totalItems,
  onPageChange
}: PaginationProps) {
  if (totalItems === 0) return null;

  return (
    <div className="pt-6 border-t border-[#E5E7EB] dark:border-zinc-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-semibold select-none font-sans">
      <span className="text-slate-450 dark:text-zinc-500 text-center sm:text-left">
        Page {page} of {totalPages} ({totalItems} partners found)
      </span>

      <div className="flex gap-2">
        <button
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
          className="inline-flex items-center gap-1 px-4 py-2 border border-[#E5E7EB] dark:border-zinc-800 text-slate-700 dark:text-zinc-300 hover:bg-[#F8FAFC] dark:hover:bg-zinc-800 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer rounded-[12px] transition-colors"
        >
          <ChevronLeft className="h-4 w-4" />
          Previous
        </button>
        <button
          disabled={page >= totalPages}
          onClick={() => onPageChange(page + 1)}
          className="inline-flex items-center gap-1 px-4 py-2 border border-[#E5E7EB] dark:border-zinc-800 text-slate-700 dark:text-zinc-300 hover:bg-[#F8FAFC] dark:hover:bg-zinc-800 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer rounded-[12px] transition-colors"
        >
          Next
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
