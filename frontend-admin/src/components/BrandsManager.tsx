"use client";

import React, { useState, useEffect } from "react";
import { 
  Search, 
  Plus, 
  Edit2, 
  Trash2, 
  AlertCircle, 
  CheckCircle2, 
  ExternalLink,
  ChevronDown,
  ChevronUp,
  X,
  Loader2,
  RefreshCw,
  Info
} from "lucide-react";
import { Button } from "./ui/button";

interface Brand {
  id: string;
  name: string;
  slug: string;
  official_website: string;
  dealer_locator_url: string;
  logo_url?: string;
  industry: string;
  category: string;
  notes?: string;
  scraper_type: string;
  scrape_frequency: number;
  scraper_enabled: boolean;
  active: boolean;
  last_scraped?: string;
  created_at: string;
  updated_at: string;
}

interface Toast {
  id: string;
  type: "success" | "error";
  message: string;
}

const INDUSTRIES = [
  "Consumer Goods",
  "Electronics",
  "Retail",
  "Healthcare",
  "Industrial",
  "Automobile",
  "Sports",
  "Home & Living",
  "FMCG",
  "Other"
];

const CATEGORIES = [
  "Mobile Phones",
  "Consumer Electronics",
  "Furniture",
  "Home Appliances",
  "Kitchen",
  "Footwear",
  "Fashion",
  "Healthcare",
  "Sports",
  "Industrial",
  "Other"
];

const SCRAPER_TYPES = ["STATIC_HTML", "PLAYWRIGHT", "API", "CUSTOM"];

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export default function BrandsManager() {
  // State
  const [brands, setBrands] = useState<Brand[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [sortField, setSortField] = useState<keyof Brand>("name");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(5);
  
  // Modal & Dialog state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<"create" | "edit">("create");
  const [selectedBrand, setSelectedBrand] = useState<Brand | null>(null);
  
  // Delete Dialog state
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [brandToDelete, setBrandToDelete] = useState<Brand | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  // Form State
  const [formData, setFormData] = useState({
    name: "",
    official_website: "",
    dealer_locator_url: "",
    industry: INDUSTRIES[0],
    category: CATEGORIES[0],
    logo_url: "",
    scraper_type: SCRAPER_TYPES[0],
    scrape_frequency: 7,
    notes: "",
    scraper_enabled: true,
    active: true
  });
  const [formErrors, setFormErrors] = useState<string[]>([]);
  const [submitLoading, setSubmitLoading] = useState(false);

  // Toast notifications State
  const [toasts, setToasts] = useState<Toast[]>([]);

  // Helpers
  const addToast = (type: "success" | "error", message: string) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  // Fetch Brands
  const fetchBrands = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/brands`);
      if (!res.ok) {
        throw new Error(`Server returned HTTP ${res.status}`);
      }
      const data = await res.json();
      if (data.success) {
        setBrands(data.data || []);
      } else {
        throw new Error(data.message || "Failed to load brands.");
      }
    } catch (err) {
      const error = err as Error;
      addToast("error", error.message || "Network error: Could not fetch brands.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBrands();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Form Handlers
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    if (type === "checkbox") {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData((prev) => ({ ...prev, [name]: checked }));
    } else if (name === "scrape_frequency") {
      setFormData((prev) => ({ ...prev, [name]: parseInt(value) || 1 }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const validateForm = (): boolean => {
    const errors: string[] = [];
    if (!formData.name.trim()) errors.push("Brand Name is required.");
    if (!formData.official_website.trim()) {
      errors.push("Official Website URL is required.");
    } else if (!formData.official_website.startsWith("http://") && !formData.official_website.startsWith("https://")) {
      errors.push("Official Website must start with http:// or https://");
    }
    
    if (!formData.dealer_locator_url.trim()) {
      errors.push("Dealer Locator URL is required.");
    } else if (!formData.dealer_locator_url.startsWith("http://") && !formData.dealer_locator_url.startsWith("https://")) {
      errors.push("Dealer Locator URL must start with http:// or https://");
    }

    if (formData.logo_url.trim() && !formData.logo_url.startsWith("http://") && !formData.logo_url.startsWith("https://")) {
      errors.push("Logo URL must be empty or start with http:// or https://");
    }

    if (formData.scrape_frequency < 1) {
      errors.push("Scrape frequency must be at least 1 day.");
    }

    setFormErrors(errors);
    return errors.length === 0;
  };

  const handleOpenCreate = () => {
    setFormData({
      name: "",
      official_website: "",
      dealer_locator_url: "",
      industry: INDUSTRIES[0],
      category: CATEGORIES[0],
      logo_url: "",
      scraper_type: SCRAPER_TYPES[0],
      scrape_frequency: 7,
      notes: "",
      scraper_enabled: true,
      active: true
    });
    setFormErrors([]);
    setModalMode("create");
    setSelectedBrand(null);
    setIsModalOpen(true);
  };

  const handleOpenEdit = (brand: Brand) => {
    setFormData({
      name: brand.name,
      official_website: brand.official_website,
      dealer_locator_url: brand.dealer_locator_url,
      industry: brand.industry,
      category: brand.category,
      logo_url: brand.logo_url || "",
      scraper_type: brand.scraper_type,
      scrape_frequency: brand.scrape_frequency,
      notes: brand.notes || "",
      scraper_enabled: brand.scraper_enabled,
      active: brand.active
    });
    setFormErrors([]);
    setModalMode("edit");
    setSelectedBrand(brand);
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setSubmitLoading(true);
    try {
      const payload = {
        ...formData,
        logo_url: formData.logo_url.trim() ? formData.logo_url : null,
        notes: formData.notes.trim() ? formData.notes : null
      };

      const url = modalMode === "create" 
        ? `${BACKEND_URL}/api/v1/brands` 
        : `${BACKEND_URL}/api/v1/brands/${selectedBrand?.id}`;
        
      const method = modalMode === "create" ? "POST" : "PUT";

      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const result = await res.json();
      if (!res.ok || !result.success) {
        const errMsg = result.errors && result.errors.length > 0 
          ? result.errors.join(", ") 
          : (result.message || `Server returned HTTP ${res.status}`);
        throw new Error(errMsg);
      }

      addToast("success", modalMode === "create" ? "Brand created successfully." : "Brand updated successfully.");
      setIsModalOpen(false);
      fetchBrands();
    } catch (err) {
      const error = err as Error;
      setFormErrors([error.message]);
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleOpenDelete = (brand: Brand) => {
    setBrandToDelete(brand);
    setIsDeleteOpen(true);
  };

  const handleDelete = async () => {
    if (!brandToDelete) return;
    setDeleteLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/brands/${brandToDelete.id}`, {
        method: "DELETE"
      });
      const result = await res.json();
      if (!res.ok || !result.success) {
        throw new Error(result.message || "Failed to delete brand.");
      }
      addToast("success", `Deleted brand '${brandToDelete.name}' successfully.`);
      setIsDeleteOpen(false);
      setBrandToDelete(null);
      fetchBrands();
    } catch (err) {
      const error = err as Error;
      addToast("error", error.message || "Network error. Could not delete brand.");
    } finally {
      setDeleteLoading(false);
    }
  };

  // Sorting logic
  const handleSort = (field: keyof Brand) => {
    if (sortField === field) {
      setSortDirection((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortDirection("asc");
    }
  };

  // Filtering & Search
  const filteredBrands = brands.filter((brand) => {
    const q = searchQuery.toLowerCase();
    return (
      brand.name.toLowerCase().includes(q) ||
      brand.industry.toLowerCase().includes(q) ||
      brand.category.toLowerCase().includes(q) ||
      brand.scraper_type.toLowerCase().includes(q)
    );
  });

  // Sorting processing
  const sortedBrands = [...filteredBrands].sort((a, b) => {
    let valA = a[sortField];
    let valB = b[sortField];

    if (valA === undefined) valA = "";
    if (valB === undefined) valB = "";

    if (typeof valA === "string" && typeof valB === "string") {
      return sortDirection === "asc"
        ? valA.localeCompare(valB)
        : valB.localeCompare(valA);
    } else if (typeof valA === "boolean" && typeof valB === "boolean") {
      return sortDirection === "asc"
        ? (valA ? 1 : 0) - (valB ? 1 : 0)
        : (valB ? 1 : 0) - (valA ? 1 : 0);
    } else if (typeof valA === "number" && typeof valB === "number") {
      return sortDirection === "asc" ? valA - valB : valB - valA;
    } else {
      const strA = String(valA);
      const strB = String(valB);
      return sortDirection === "asc" ? strA.localeCompare(strB) : strB.localeCompare(strA);
    }
  });

  // Pagination processing
  const totalPages = Math.ceil(sortedBrands.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const paginatedBrands = sortedBrands.slice(startIndex, startIndex + pageSize);

  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery]);

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return "Never";
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric"
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Panel */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-200 dark:border-zinc-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-zinc-50">
            Brand Catalog
          </h1>
          <p className="text-sm text-slate-500 dark:text-zinc-400 mt-1">
            Create, audit, and configure scraper frequencies for monitored brands.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={fetchBrands}
            className="flex items-center gap-1.5"
            disabled={loading}
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
            Sync
          </Button>
          <Button
            id="btn-add-brand"
            size="sm"
            onClick={handleOpenCreate}
            className="bg-zinc-900 text-zinc-50 dark:bg-zinc-50 dark:text-zinc-950 flex items-center gap-1.5 hover:bg-zinc-800 dark:hover:bg-zinc-200"
          >
            <Plus className="h-4 w-4" />
            Add Brand
          </Button>
        </div>
      </div>

      {/* Control Panel: Search & Stats */}
      <div className="flex flex-col md:flex-row gap-4 justify-between">
        <div className="relative max-w-sm w-full">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400 dark:text-zinc-600" />
          <input
            id="brand-search-input"
            type="text"
            placeholder="Search by name, industry, category..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-lg py-2 pl-9 pr-4 text-sm focus:outline-none focus:ring-1 focus:ring-slate-400 dark:focus:ring-zinc-600"
          />
          {searchQuery && (
            <button 
              onClick={() => setSearchQuery("")}
              className="absolute right-3 top-2.5 text-xs text-slate-400 hover:text-slate-600 dark:text-zinc-600 dark:hover:text-zinc-400"
            >
              Clear
            </button>
          )}
        </div>
        <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-zinc-500">
          <span>Found {sortedBrands.length} brands</span>
        </div>
      </div>

      {/* Main Grid / Table */}
      <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl overflow-hidden shadow-sm">
        {loading ? (
          /* Skeleton Loader */
          <div className="p-6 space-y-4">
            <div className="h-10 bg-slate-100 dark:bg-zinc-800 rounded-lg animate-pulse" />
            <div className="space-y-3">
              {[...Array(pageSize)].map((_, i) => (
                <div key={i} className="h-12 bg-slate-50/50 dark:bg-zinc-800/40 rounded-lg animate-pulse" />
              ))}
            </div>
          </div>
        ) : paginatedBrands.length === 0 ? (
          /* Empty State */
          <div className="p-16 text-center max-w-xl mx-auto">
            <Info className="h-12 w-12 text-slate-300 dark:text-zinc-700 mx-auto mb-4" />
            <h3 className="font-semibold text-slate-800 dark:text-zinc-200 mb-1">
              No Brands Discovered
            </h3>
            <p className="text-sm text-slate-500 dark:text-zinc-500 mb-6">
              {searchQuery ? "No matches found for your filter criteria." : "Create the first verified brand catalog to kickstart discovery."}
            </p>
            {searchQuery ? (
              <Button variant="outline" size="sm" onClick={() => setSearchQuery("")}>
                Reset Filter
              </Button>
            ) : (
              <Button size="sm" onClick={handleOpenCreate} className="bg-zinc-900 text-zinc-50 dark:bg-zinc-50 dark:text-zinc-950">
                Add New Brand
              </Button>
            )}
          </div>
        ) : (
          /* Data Table */
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm border-collapse">
              <thead>
                <tr className="border-b border-slate-200 dark:border-zinc-800 bg-slate-50/50 dark:bg-zinc-900/50 text-xs font-semibold text-slate-500 dark:text-zinc-500 uppercase tracking-wider select-none">
                  <th className="px-6 py-4">Logo</th>
                  <th className="px-6 py-4 cursor-pointer hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors" onClick={() => handleSort("name")}>
                    <div className="flex items-center gap-1">
                      Brand
                      {sortField === "name" && (sortDirection === "asc" ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />)}
                    </div>
                  </th>
                  <th className="px-6 py-4 cursor-pointer hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors" onClick={() => handleSort("industry")}>
                    <div className="flex items-center gap-1">
                      Industry
                      {sortField === "industry" && (sortDirection === "asc" ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />)}
                    </div>
                  </th>
                  <th className="px-6 py-4 cursor-pointer hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors" onClick={() => handleSort("category")}>
                    <div className="flex items-center gap-1">
                      Category
                      {sortField === "category" && (sortDirection === "asc" ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />)}
                    </div>
                  </th>
                  <th className="px-6 py-4">Scraper</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 cursor-pointer hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors" onClick={() => handleSort("last_scraped")}>
                    <div className="flex items-center gap-1">
                      Last Scraped
                      {sortField === "last_scraped" && (sortDirection === "asc" ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />)}
                    </div>
                  </th>
                  <th className="px-6 py-4 cursor-pointer hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors" onClick={() => handleSort("created_at")}>
                    <div className="flex items-center gap-1">
                      Created At
                      {sortField === "created_at" && (sortDirection === "asc" ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />)}
                    </div>
                  </th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-zinc-800">
                {paginatedBrands.map((brand) => (
                  <tr key={brand.id} className="hover:bg-slate-50/50 dark:hover:bg-zinc-900/30 transition-colors">
                    <td className="px-6 py-4">
                      {brand.logo_url ? (
                        <img 
                          src={brand.logo_url} 
                          alt={`${brand.name} Logo`} 
                          className="h-7 w-7 rounded-md object-contain border border-slate-100 dark:border-zinc-800 bg-white"
                          onError={(e) => {
                            (e.target as HTMLImageElement).src = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=40&h=40&q=80"; // fallback
                          }}
                        />
                      ) : (
                        <div className="h-7 w-7 rounded-md bg-slate-100 dark:bg-zinc-800 flex items-center justify-center text-xs font-semibold text-slate-400 dark:text-zinc-500 uppercase">
                          {brand.name.substring(0, 2)}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-900 dark:text-zinc-50">
                      <div className="flex flex-col">
                        <span>{brand.name}</span>
                        <span className="text-xs text-slate-400 dark:text-zinc-500 font-normal">/{brand.slug}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-slate-600 dark:text-zinc-400">{brand.industry}</td>
                    <td className="px-6 py-4 text-slate-600 dark:text-zinc-400">{brand.category}</td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col gap-0.5 text-xs text-slate-600 dark:text-zinc-400">
                        <span className="font-mono bg-slate-100 dark:bg-zinc-800 px-1.5 py-0.5 rounded w-max">{brand.scraper_type}</span>
                        <span className="text-slate-400 dark:text-zinc-500">Every {brand.scrape_frequency}d</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap gap-1.5">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                          brand.active 
                            ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400" 
                            : "bg-slate-500/10 text-slate-600 dark:text-slate-400"
                        }`}>
                          {brand.active ? "Active" : "Inactive"}
                        </span>
                        {brand.scraper_enabled && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-500/10 text-amber-600 dark:text-amber-400">
                            Auto
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-slate-500 dark:text-zinc-500 text-xs">
                      {formatDate(brand.last_scraped)}
                    </td>
                    <td className="px-6 py-4 text-slate-500 dark:text-zinc-500 text-xs">
                      {formatDate(brand.created_at)}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <a 
                          href={brand.official_website} 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          className="p-1 text-slate-400 hover:text-slate-700 dark:hover:text-zinc-300 rounded"
                          title="Visit Official Site"
                        >
                          <ExternalLink className="h-4 w-4" />
                        </a>
                        <button
                          onClick={() => handleOpenEdit(brand)}
                          className="p-1 text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 rounded"
                          title="Edit Brand"
                        >
                          <Edit2 className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleOpenDelete(brand)}
                          className="p-1 text-slate-400 hover:text-red-600 dark:hover:text-red-400 rounded"
                          title="Delete Brand"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination controls */}
        {!loading && totalPages > 1 && (
          <div className="px-6 py-4 border-t border-slate-200 dark:border-zinc-800 flex items-center justify-between bg-slate-50/30 dark:bg-zinc-900/10">
            <span className="text-xs text-slate-500 dark:text-zinc-500">
              Showing page {currentPage} of {totalPages}
            </span>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="xs"
                disabled={currentPage === 1}
                onClick={() => setCurrentPage((c) => c - 1)}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                size="xs"
                disabled={currentPage === totalPages}
                onClick={() => setCurrentPage((c) => c + 1)}
              >
                Next
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* ========================================================= */}
      {/* MODAL FORM OVERLAY (ADD/EDIT BRAND)                       */}
      {/* ========================================================= */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 dark:bg-black/80 backdrop-blur-sm">
          <div className="w-full max-w-2xl bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-2xl shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-200 flex flex-col max-h-[90vh]">
            
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-slate-200 dark:border-zinc-800 flex items-center justify-between">
              <h2 className="text-lg font-bold text-slate-900 dark:text-zinc-50">
                {modalMode === "create" ? "Add New Brand" : "Edit Brand details"}
              </h2>
              <button 
                onClick={() => setIsModalOpen(false)}
                className="p-1 rounded-md text-slate-400 hover:bg-slate-100 dark:hover:bg-zinc-800 hover:text-slate-600 dark:hover:text-zinc-300"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Modal Body / Form */}
            <form onSubmit={handleSubmit} className="flex-grow overflow-y-auto p-6 space-y-6">
              
              {/* Errors Block */}
              {formErrors.length > 0 && (
                <div className="bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/30 rounded-xl p-4 flex gap-3 text-sm text-red-700 dark:text-red-400">
                  <AlertCircle className="h-5 w-5 flex-shrink-0" />
                  <div className="space-y-1">
                    <p className="font-semibold">Please resolve the following errors:</p>
                    <ul className="list-disc list-inside space-y-0.5 text-xs">
                      {formErrors.map((err, i) => <li key={i}>{err}</li>)}
                    </ul>
                  </div>
                </div>
              )}

              {/* Rows */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* Brand Name */}
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-slate-700 dark:text-zinc-300 block">
                    Brand Name *
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    placeholder="e.g. Sony"
                    className="w-full bg-slate-50 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-slate-400 dark:focus:ring-zinc-600"
                  />
                </div>

                {/* Industry */}
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-slate-700 dark:text-zinc-300 block">
                    Industry *
                  </label>
                  <select
                    name="industry"
                    value={formData.industry}
                    onChange={handleInputChange}
                    className="w-full bg-slate-50 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 rounded-lg p-2.5 text-sm focus:outline-none"
                  >
                    {INDUSTRIES.map((ind) => (
                      <option key={ind} value={ind}>{ind}</option>
                    ))}
                  </select>
                </div>

                {/* Official Website */}
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-slate-700 dark:text-zinc-300 block">
                    Official Website URL *
                  </label>
                  <input
                    type="text"
                    name="official_website"
                    value={formData.official_website}
                    onChange={handleInputChange}
                    placeholder="https://www.sony.co.in"
                    className="w-full bg-slate-50 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-slate-400 dark:focus:ring-zinc-600"
                  />
                </div>

                {/* Category */}
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-slate-700 dark:text-zinc-300 block">
                    Category *
                  </label>
                  <select
                    name="category"
                    value={formData.category}
                    onChange={handleInputChange}
                    className="w-full bg-slate-50 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 rounded-lg p-2.5 text-sm focus:outline-none"
                  >
                    {CATEGORIES.map((cat) => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>

                {/* Dealer Locator URL */}
                <div className="space-y-2 md:col-span-2">
                  <label className="text-xs font-semibold text-slate-700 dark:text-zinc-300 block">
                    Dealer Locator URL *
                  </label>
                  <input
                    type="text"
                    name="dealer_locator_url"
                    value={formData.dealer_locator_url}
                    onChange={handleInputChange}
                    placeholder="https://www.sony.co.in/microsite/retailshops/"
                    className="w-full bg-slate-50 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-slate-400 dark:focus:ring-zinc-600"
                  />
                </div>

                {/* Logo URL */}
                <div className="space-y-2 md:col-span-2">
                  <label className="text-xs font-semibold text-slate-700 dark:text-zinc-300 block">
                    Logo Image URL
                  </label>
                  <input
                    type="text"
                    name="logo_url"
                    value={formData.logo_url}
                    onChange={handleInputChange}
                    placeholder="https://example.com/logo.png"
                    className="w-full bg-slate-50 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-slate-400 dark:focus:ring-zinc-600"
                  />
                </div>

                {/* Scraper Config Section */}
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-slate-700 dark:text-zinc-300 block">
                    Scraper Type
                  </label>
                  <select
                    name="scraper_type"
                    value={formData.scraper_type}
                    onChange={handleInputChange}
                    className="w-full bg-slate-50 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 rounded-lg p-2.5 text-sm focus:outline-none"
                  >
                    {SCRAPER_TYPES.map((type) => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>

                {/* Scrape Frequency */}
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-slate-700 dark:text-zinc-300 block">
                    Scrape Frequency (Days)
                  </label>
                  <input
                    type="number"
                    name="scrape_frequency"
                    value={formData.scrape_frequency}
                    onChange={handleInputChange}
                    min="1"
                    className="w-full bg-slate-50 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-slate-400 dark:focus:ring-zinc-600"
                  />
                </div>

                {/* Toggle Controls */}
                <div className="flex items-center gap-6 md:col-span-2 pt-2 bg-slate-50 dark:bg-zinc-850 p-4 rounded-xl">
                  <label className="flex items-center gap-2 cursor-pointer select-none">
                    <input
                      type="checkbox"
                      name="scraper_enabled"
                      checked={formData.scraper_enabled}
                      onChange={handleInputChange}
                      className="rounded border-slate-300 dark:border-zinc-700 h-4 w-4 text-slate-900 focus:ring-slate-400"
                    />
                    <div className="text-xs">
                      <span className="font-semibold text-slate-800 dark:text-zinc-200 block">Automated Scraper Enabled</span>
                      <span className="text-slate-400 dark:text-zinc-500">Run background index scans.</span>
                    </div>
                  </label>

                  <label className="flex items-center gap-2 cursor-pointer select-none">
                    <input
                      type="checkbox"
                      name="active"
                      checked={formData.active}
                      onChange={handleInputChange}
                      className="rounded border-slate-300 dark:border-zinc-700 h-4 w-4 text-slate-900 focus:ring-slate-400"
                    />
                    <div className="text-xs">
                      <span className="font-semibold text-slate-800 dark:text-zinc-200 block">Show Publicly (Active)</span>
                      <span className="text-slate-400 dark:text-zinc-500">Render brand in client catalog.</span>
                    </div>
                  </label>
                </div>

                {/* Notes */}
                <div className="space-y-2 md:col-span-2">
                  <label className="text-xs font-semibold text-slate-700 dark:text-zinc-300 block">
                    Notes & Description
                  </label>
                  <textarea
                    name="notes"
                    value={formData.notes}
                    onChange={handleInputChange}
                    rows={3}
                    placeholder="Provide comments or credentials requirements for this brand Locator page..."
                    className="w-full bg-slate-50 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-slate-400 dark:focus:ring-zinc-600"
                  />
                </div>

              </div>
            </form>

            {/* Modal Footer */}
            <div className="px-6 py-4 border-t border-slate-200 dark:border-zinc-800 bg-slate-50/50 dark:bg-zinc-900/50 flex justify-end gap-3">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsModalOpen(false)}
                disabled={submitLoading}
              >
                Cancel
              </Button>
              <Button
                size="sm"
                onClick={handleSubmit}
                disabled={submitLoading}
                className="bg-zinc-900 text-zinc-50 dark:bg-zinc-50 dark:text-zinc-950 flex items-center gap-1"
              >
                {submitLoading && <Loader2 className="h-3 w-3 animate-spin" />}
                {modalMode === "create" ? "Create Brand" : "Save Changes"}
              </Button>
            </div>

          </div>
        </div>
      )}

      {/* ========================================================= */}
      {/* CONFIRM DELETE DIALOG OVERLAY                             */}
      {/* ========================================================= */}
      {isDeleteOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 dark:bg-black/80 backdrop-blur-sm">
          <div className="w-full max-w-md bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-2xl shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div className="p-6">
              <div className="flex gap-4 items-start text-red-600 dark:text-red-400 mb-4">
                <AlertCircle className="h-8 w-8 flex-shrink-0" />
                <div>
                  <h3 className="text-lg font-bold text-slate-900 dark:text-zinc-50">
                    Delete Brand Confirmation
                  </h3>
                  <p className="text-sm text-slate-500 dark:text-zinc-500 mt-2">
                    Are you sure you want to delete <strong className="text-slate-800 dark:text-zinc-200">&apos;{brandToDelete?.name}&apos;</strong>?
                  </p>
                  <p className="text-xs text-slate-400 dark:text-zinc-600 mt-2">
                    This action is irreversible and will delete all associated scrapers and crawler history files.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="px-6 py-4 bg-slate-50/50 dark:bg-zinc-900/50 border-t border-slate-100 dark:border-zinc-800 flex justify-end gap-3">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setIsDeleteOpen(false);
                  setBrandToDelete(null);
                }}
                disabled={deleteLoading}
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                size="sm"
                onClick={handleDelete}
                disabled={deleteLoading}
                className="flex items-center gap-1"
              >
                {deleteLoading && <Loader2 className="h-3 w-3 animate-spin" />}
                Confirm Delete
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================= */}
      {/* TOAST NOTIFICATION CONTAINER                              */}
      {/* ========================================================= */}
      <div className="fixed bottom-6 right-6 z-55 flex flex-col gap-3 w-full max-w-sm">
        {toasts.map((toast) => (
          <div 
            key={toast.id}
            className={`p-4 rounded-xl border shadow-lg flex items-start gap-3 text-sm animate-in slide-in-from-bottom-5 duration-300 ${
              toast.type === "success" 
                ? "bg-white dark:bg-zinc-900 border-emerald-250 dark:border-emerald-900/40 text-emerald-950 dark:text-emerald-450" 
                : "bg-white dark:bg-zinc-900 border-red-250 dark:border-red-900/40 text-red-950 dark:text-red-450"
            }`}
          >
            {toast.type === "success" ? (
              <CheckCircle2 className="h-5 w-5 text-emerald-500 flex-shrink-0" />
            ) : (
              <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
            )}
            <p className="flex-grow font-medium leading-normal">{toast.message}</p>
          </div>
        ))}
      </div>

    </div>
  );
}
