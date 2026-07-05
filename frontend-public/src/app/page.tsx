"use client";

import React, { useState, useEffect, useRef } from "react";
import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import SearchBar from "@/components/SearchBar";
import Stats from "@/components/Stats";
import BrandGrid from "@/components/BrandGrid";
import DealerCard from "@/components/DealerCard";
import FilterSidebar from "@/components/FilterSidebar";
import Pagination from "@/components/Pagination";
import Footer from "@/components/Footer";
import PopularCategories from "@/components/PopularCategories";
import WhyChooseUs from "@/components/WhyChooseUs";

interface Brand {
  id: string;
  name: string;
  official_website: string;
  category?: string;
  industry?: string;
}

interface Dealer {
  id: string;
  brand_id: string;
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
  country: string;
  quality_score: number;
  validation_status: "VALID" | "INVALID";
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export default function Home() {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [dealers, setDealers] = useState<Dealer[]>([]);
  const [totalDealers, setTotalDealers] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Search & Filter State
  const [query, setQuery] = useState("");
  const [selectedBrand, setSelectedBrand] = useState("");
  const [city, setCity] = useState("");
  const [state, setState] = useState("");
  const [pincode, setPincode] = useState("");
  const [dealerType, setDealerType] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");

  const [sortBy, setSortBy] = useState("name");
  const [sortOrder, setSortOrder] = useState("asc");
  const [page, setPage] = useState(1);
  const limit = 9;

  const searchSectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const storedTheme = localStorage.getItem("theme") || "dark";
    if (storedTheme === "dark") {
      setIsDarkMode(true);
      document.documentElement.classList.add("dark");
    } else {
      setIsDarkMode(false);
      document.documentElement.classList.remove("dark");
    }
    fetchBrands();
  }, []);

  useEffect(() => {
    fetchDealers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, sortBy, sortOrder]);

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

  const fetchBrands = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/brands`);
      const data = await res.json();
      if (res.ok && data.success) setBrands(data.data || []);
    } catch (err) {
      console.error("Failed to load brands:", err);
    }
  };

  const fetchDealers = async (resetPage = false) => {
    setLoading(true);
    setError(null);
    try {
      const currentPage = resetPage ? 1 : page;
      if (resetPage) setPage(1);

      const params = new URLSearchParams();
      if (query.trim()) params.append("query", query.trim());
      if (selectedBrand) params.append("brand_id", selectedBrand);
      if (city.trim()) params.append("city", city.trim());
      if (state.trim()) params.append("state", state.trim());
      if (pincode.trim()) params.append("pincode", pincode.trim());
      params.append("sort_by", sortBy);
      params.append("sort_order", sortOrder);
      params.append("page", currentPage.toString());
      params.append("limit", limit.toString());

      const res = await fetch(`${BACKEND_URL}/api/v1/scraper/dealers/search?${params.toString()}`);
      const data = await res.json();
      if (res.ok && data.success) {
        let results = data.data.dealers || [];
        if (dealerType) {
          results = results.filter((d: Dealer) => {
            const val = (d.dealer_name + " " + d.address).toLowerCase();
            return val.includes(dealerType.toLowerCase());
          });
        }
        if (selectedCategory) {
          const matchingBrandIds = brands
            .filter((b) => (b.category || b.industry || "").toLowerCase().includes(selectedCategory.toLowerCase()))
            .map((b) => b.id);
          if (matchingBrandIds.length > 0) {
            results = results.filter((d: Dealer) => matchingBrandIds.includes(d.brand_id));
          }
        }

        setDealers(results);
        setTotalDealers(results.length > 0 ? data.data.total : 0);
      } else {
        throw new Error(data.message || "Failed to load dealers.");
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error fetching search results.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleResetFilters = () => {
    setQuery("");
    setSelectedBrand("");
    setCity("");
    setState("");
    setPincode("");
    setDealerType("");
    setSelectedCategory("");
    setSortBy("name");
    setSortOrder("asc");
    setPage(1);
    fetchDealers(true);
  };

  const handleSelectCategory = (category: string) => {
    setSelectedCategory(category);
    scrollToSearch();
    fetchDealers(true);
  };

  const handleSelectBrand = (brandId: string) => {
    setSelectedBrand(brandId);
    scrollToSearch();
    fetchDealers(true);
  };

  const scrollToSearch = () => {
    searchSectionRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const totalPages = Math.ceil(totalDealers / limit) || 1;

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-900 dark:bg-[#09090B] dark:text-white transition-colors duration-250 flex flex-col font-sans relative">
      <Navbar 
        isDarkMode={isDarkMode} 
        toggleTheme={toggleTheme} 
        onSelectCategory={handleSelectCategory}
        onSearchClick={scrollToSearch}
      />

      <Hero>
        <SearchBar
          query={query} setQuery={setQuery}
          selectedBrand={selectedBrand} setSelectedBrand={setSelectedBrand}
          city={city} setCity={setCity}
          state={state} setState={setState}
          pincode={pincode} setPincode={setPincode}
          selectedCategory={selectedCategory} setSelectedCategory={setSelectedCategory}
          brands={brands}
          onSubmit={(e) => { e.preventDefault(); fetchDealers(true); }}
          onReset={handleResetFilters}
        />

        {/* Trusted Brands Row */}
        <div className="pt-6 space-y-3.5 select-none">
          <p className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-widest text-center">
            Trusted by leading manufacturers
          </p>
          <div className="flex flex-wrap items-center justify-center gap-2.5 overflow-x-auto pb-2 scrollbar-none">
            {["Bosch", "Titan", "Lava", "Sleepwell", "Kajaria", "Havells", "Asian Paints", "Anchor"].map((brandName) => (
              <div
                key={brandName}
                onClick={() => {
                  const found = brands.find(b => b.name.toLowerCase() === brandName.toLowerCase());
                  if (found) {
                    handleSelectBrand(found.id);
                  } else {
                    setQuery(brandName);
                    fetchDealers(true);
                  }
                }}
                className="px-4 py-2 rounded-full bg-white dark:bg-[#111113] border border-[#E5E7EB] dark:border-white/10 text-xs font-bold text-slate-700 dark:text-zinc-300 hover:text-[#2563EB] dark:hover:text-indigo-400 hover:border-[#2563EB] cursor-pointer transition-all shadow-xs"
              >
                {brandName}
              </div>
            ))}
          </div>
        </div>
      </Hero>

      <Stats />

      <main className="flex-grow max-w-[1280px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-16 space-y-24 z-15 relative">
        <PopularCategories onSelectCategory={handleSelectCategory} />

        <BrandGrid brands={brands} onSelectBrand={handleSelectBrand} />

        {/* Search Results Column Wrapper */}
        <div ref={searchSectionRef} className="space-y-6 pt-4 font-sans">
          <div className="flex flex-col lg:flex-row gap-8 items-start">
            {/* Desktop Filters Sidebar */}
            <aside className="w-full lg:w-64 shrink-0">
              <FilterSidebar
                brands={brands}
                selectedBrand={selectedBrand} setSelectedBrand={setSelectedBrand}
                selectedCategory={selectedCategory} setSelectedCategory={setSelectedCategory}
                city={city} setCity={setCity}
                state={state} setState={setState}
                dealerType={dealerType} setDealerType={setDealerType}
                onApply={() => fetchDealers(true)}
                onReset={handleResetFilters}
              />
            </aside>

            {/* Dealers Directory Content Column */}
            <div className="flex-grow w-full space-y-6">
              {/* Header and sorting */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E5E7EB] dark:border-zinc-800 pb-4">
                <div>
                  <h2 className="text-xl font-bold text-[#0F172A] dark:text-zinc-50 font-serif">
                    Authorized Service & Retail Partners
                  </h2>
                  <p className="text-xs text-slate-500 dark:text-zinc-400 mt-1">
                    Showing {totalDealers} active locations based on your search filters.
                  </p>
                </div>
                
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-slate-400 font-semibold">Sort By</span>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="px-3 h-9 rounded-[12px] border border-[#E5E7EB] dark:border-zinc-800 bg-white dark:bg-zinc-900 focus:outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB] text-slate-700 dark:text-zinc-300 font-semibold cursor-pointer"
                  >
                    <option value="name">Dealer Name</option>
                    <option value="quality_score">Confidence Score</option>
                  </select>
                  <select
                    value={sortOrder}
                    onChange={(e) => setSortOrder(e.target.value)}
                    className="px-3 h-9 rounded-[12px] border border-[#E5E7EB] dark:border-zinc-800 bg-white dark:bg-zinc-900 focus:outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB] text-slate-700 dark:text-zinc-300 font-semibold cursor-pointer"
                  >
                    <option value="asc">Ascending</option>
                    <option value="desc">Descending</option>
                  </select>
                </div>
              </div>

              {error && (
                <div className="p-4 bg-red-50/10 border border-red-500/20 text-red-650 dark:text-red-450 rounded-[12px] text-xs font-semibold text-center">
                  {error}
                </div>
              )}

              {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                  {[...Array(6)].map((_, i) => (
                    <div key={i} className="border border-[#E5E7EB] dark:border-zinc-850 rounded-[16px] p-6 bg-white dark:bg-zinc-900 space-y-4 animate-pulse">
                      <div className="flex justify-between items-center">
                        <div className="h-4 bg-slate-200 dark:bg-zinc-800 w-16 rounded-[12px]" />
                        <div className="h-4 bg-slate-200 dark:bg-zinc-800 w-12 rounded-[12px]" />
                      </div>
                      <div className="h-5 bg-slate-200 dark:bg-zinc-800 w-3/4 rounded-[12px]" />
                      <div className="h-4 bg-slate-200 dark:bg-zinc-800 w-5/6 rounded-[12px]" />
                      <div className="h-4 bg-slate-200 dark:bg-zinc-800 w-full rounded-[12px]" />
                    </div>
                  ))}
                </div>
              ) : dealers.length === 0 ? (
                <div className="text-center py-16 bg-white dark:bg-zinc-900 border border-[#E5E7EB] dark:border-zinc-850 rounded-[16px] space-y-3">
                  <h3 className="font-bold text-sm text-[#0F172A] dark:text-zinc-200">No partner listings found</h3>
                  <p className="text-xs text-slate-500 max-w-xs mx-auto">Broaden location filters or reset parameters to see default directories.</p>
                  <button onClick={handleResetFilters} className="px-4 py-2 text-xs font-bold bg-[#2563EB] hover:bg-blue-700 text-white rounded-[12px] cursor-pointer">Reset Filters</button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                  {dealers.map((d) => (
                    <DealerCard key={d.id} dealer={d} />
                  ))}
                </div>
              )}

              <Pagination
                page={page}
                totalPages={totalPages}
                totalItems={totalDealers}
                onPageChange={setPage}
              />
            </div>
          </div>
        </div>

        <WhyChooseUs />
      </main>

      <Footer />
    </div>
  );
}
