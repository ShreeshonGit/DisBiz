"use client";

import React, { useState, useEffect, useRef } from "react";
import { 
  Cpu, 
  Search, 
  Play, 
  Eye, 
  AlertTriangle, 
  CheckCircle2, 
  Loader2, 
  Terminal, 
  Clock, 
  Ban, 
  Globe,
  X
} from "lucide-react";
import { Button } from "./ui/button";

interface Brand {
  id: string;
  name: string;
  official_website: string;
  dealer_locator_url: string;
  industry: string;
  category: string;
}

interface ScrapeJob {
  id: string;
  brand_id: string;
  brand_name: string;
  status: "Queued" | "Running" | "Completed" | "Failed" | "Cancelled";
  started_at: string;
  completed_at?: string;
  duration_seconds?: number;
  records_found: number;
  records_saved: number;
  error_message?: string;
}

interface PreviewDealer {
  name: string;
  address: string;
  city?: string;
  state?: string;
  pincode?: string;
  phone?: string;
  email?: string;
  latitude?: number;
  longitude?: number;
  validation_status: "VALID" | "INVALID";
  validation_errors: string[];
}

interface Toast {
  id: string;
  type: "success" | "error";
  message: string;
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export default function ScraperController() {
  // Lists
  const [brands, setBrands] = useState<Brand[]>([]);
  const [jobs, setJobs] = useState<ScrapeJob[]>([]);
  const [selectedBrandId, setSelectedBrandId] = useState<string>("");
  const selectedBrand = brands.find(b => b.id === selectedBrandId);

  // States
  const [loadingBrands, setLoadingBrands] = useState(true);
  const [loadingJobs, setLoadingJobs] = useState(true);
  const [detecting, setDetecting] = useState(false);
  const [previewing, setPreviewing] = useState(false);
  const [cancellingJobId, setCancellingJobId] = useState<string | null>(null);

  // Detection Results state
  const [detectionResult, setDetectionResult] = useState<{
    detected_locator_type: string;
    suggested_scraper_type: string;
    status_code: number;
    content_length: number;
  } | null>(null);

  // Preview Results state
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewResult, setPreviewResult] = useState<{
    brand_name: string;
    locator_url: string;
    total_extracted: number;
    preview_records: PreviewDealer[];
    logs: string[];
  } | null>(null);

  // Toasts
  const [toasts, setToasts] = useState<Toast[]>([]);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const addToast = (type: "success" | "error", message: string) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  // Initial Fetches
  const fetchBrands = async () => {
    setLoadingBrands(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/brands`);
      const data = await res.json();
      if (data.success) {
        setBrands(data.data || []);
      }
    } catch {
      addToast("error", "Failed to fetch brands list.");
    } finally {
      setLoadingBrands(false);
    }
  };

  const fetchJobs = async (silent = false) => {
    if (!silent) setLoadingJobs(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/scraper/jobs`);
      const data = await res.json();
      if (data.success) {
        setJobs(data.data || []);
      }
    } catch {
      if (!silent) addToast("error", "Failed to fetch scraper jobs history.");
    } finally {
      if (!silent) setLoadingJobs(false);
    }
  };

  useEffect(() => {
    fetchBrands();
    fetchJobs();

    // Auto refresh job history every 5 seconds
    intervalRef.current = setInterval(() => {
      fetchJobs(true);
    }, 5000);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Action Handlers
  const handleAutoDetect = async () => {
    if (!selectedBrandId) return;
    setDetecting(true);
    setDetectionResult(null);
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/scraper/detect`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ brand_id: selectedBrandId })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setDetectionResult(data.data);
        addToast("success", "Locator type auto-detected successfully.");
      } else {
        throw new Error(data.message || "Detection request failed.");
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Auto-detection encountered an error.";
      addToast("error", msg);
    } finally {
      setDetecting(false);
    }
  };

  const handlePreviewScrape = async () => {
    if (!selectedBrandId) return;
    setPreviewing(true);
    setPreviewResult(null);
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/scraper/preview`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ brand_id: selectedBrandId })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setPreviewResult(data.data);
        setPreviewOpen(true);
        addToast("success", "Preview completed. Displaying extracted records.");
      } else {
        throw new Error(data.message || "Preview request failed.");
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Preview scrape failed to run.";
      addToast("error", msg);
    } finally {
      setPreviewing(false);
    }
  };

  const handleCancelJob = async (jobId: string) => {
    setCancellingJobId(jobId);
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/scraper/cancel/${jobId}`, {
        method: "POST"
      });
      const data = await res.json();
      if (res.ok && data.success) {
        addToast("success", "Job cancelled successfully.");
        fetchJobs(true);
      } else {
        throw new Error(data.message || "Cancellation failed.");
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Could not cancel job.";
      addToast("error", msg);
    } finally {
      setCancellingJobId(null);
    }
  };

  const formatDate = (dateStr: string) => {
    try {
      const d = new Date(dateStr);
      return d.toLocaleTimeString("en-IN", { hour: "numeric", minute: "2-digit" }) + 
        ", " + d.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Panel */}
      <div className="border-b border-slate-200 dark:border-zinc-800 pb-5">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-zinc-50">
          Scraping Controllers
        </h1>
        <p className="text-sm text-slate-500 dark:text-zinc-400 mt-1">
          Perform website structure auto-detection, view live preview runs, and trace crawler execution logs.
        </p>
      </div>

      {/* Selector & Actions Card */}
      <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-6 shadow-sm">
        <div className="max-w-xl space-y-6">
          {/* Brand Dropdown */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-700 dark:text-zinc-300 block">
              Select Brand Catalog *
            </label>
            <select
              value={selectedBrandId}
              onChange={(e) => {
                setSelectedBrandId(e.target.value);
                setDetectionResult(null);
              }}
              className="w-full bg-slate-50 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 rounded-lg p-2.5 text-sm focus:outline-none"
              disabled={loadingBrands}
            >
              <option value="">-- Choose a Brand --</option>
              {brands.map((b) => (
                <option key={b.id} value={b.id}>{b.name}</option>
              ))}
            </select>
          </div>

          {/* Selected Brand Stats */}
          {selectedBrand && (
            <div className="space-y-4 pt-4 border-t border-slate-100 dark:border-zinc-850 animate-fade-in">
              <div className="flex flex-col gap-1.5">
                <span className="text-xs text-slate-400 dark:text-zinc-500">Official Locator URL</span>
                <a 
                  href={selectedBrand.dealer_locator_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-sm text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1.5 font-medium"
                >
                  <Globe className="h-4 w-4" />
                  {selectedBrand.dealer_locator_url}
                </a>
              </div>

              {/* Auto Detection Box */}
              {detectionResult && (
                <div className="bg-slate-50 dark:bg-zinc-950/40 border border-slate-250/60 dark:border-zinc-800 rounded-xl p-4 grid grid-cols-2 gap-4 text-xs">
                  <div>
                    <span className="text-slate-400 dark:text-zinc-500 block mb-0.5">Detected Type</span>
                    <span className="font-semibold text-slate-800 dark:text-zinc-200">{detectionResult.detected_locator_type}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 dark:text-zinc-500 block mb-0.5">Suggested Scraper</span>
                    <span className="font-semibold text-slate-800 dark:text-zinc-200">{detectionResult.suggested_scraper_type}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 dark:text-zinc-500 block mb-0.5">HTTP Status</span>
                    <span className={`font-semibold ${detectionResult.status_code === 200 ? "text-emerald-600" : "text-amber-600"}`}>
                      {detectionResult.status_code}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 dark:text-zinc-500 block mb-0.5">Response Size</span>
                    <span className="font-semibold text-slate-800 dark:text-zinc-200">{(detectionResult.content_length / 1024).toFixed(1)} KB</span>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex flex-wrap gap-3 pt-2">
                <Button
                  id="btn-auto-detect"
                  variant="outline"
                  size="sm"
                  onClick={handleAutoDetect}
                  disabled={detecting || previewing}
                  className="flex items-center gap-1.5"
                >
                  {detecting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Search className="h-3.5 w-3.5" />}
                  Auto Detect Type
                </Button>
                <Button
                  id="btn-preview-scrape"
                  variant="outline"
                  size="sm"
                  onClick={handlePreviewScrape}
                  disabled={detecting || previewing}
                  className="flex items-center gap-1.5"
                >
                  {previewing ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Eye className="h-3.5 w-3.5" />}
                  Preview Scrape
                </Button>
                
                {/* Disabled Scraper Trigger */}
                <div className="group relative">
                  <Button
                    id="btn-start-scrape"
                    size="sm"
                    disabled
                    className="bg-slate-200 text-slate-400 dark:bg-zinc-800 dark:text-zinc-600 cursor-not-allowed select-none flex items-center gap-1.5"
                  >
                    <Play className="h-3.5 w-3.5" />
                    Start Full Scrape
                  </Button>
                  <div className="absolute bottom-full mb-2 hidden group-hover:block bg-zinc-950 text-zinc-100 text-[10px] px-2 py-1.5 rounded-md shadow-md whitespace-nowrap z-50">
                    * Full scraping runs will launch in Sprint 3.2.
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Job History Panel */}
      <div className="space-y-4">
        <h3 className="text-md font-semibold text-slate-800 dark:text-zinc-200 flex items-center gap-2">
          <Clock className="h-4.5 w-4.5 text-slate-400 dark:text-zinc-500" />
          Scraper Job History
        </h3>

        <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl overflow-hidden shadow-sm">
          {loadingJobs ? (
            <div className="p-6 space-y-3 animate-pulse">
              <div className="h-10 bg-slate-100 dark:bg-zinc-800 rounded-lg" />
              <div className="h-12 bg-slate-50 dark:bg-zinc-800/40 rounded-lg" />
              <div className="h-12 bg-slate-50 dark:bg-zinc-800/40 rounded-lg" />
            </div>
          ) : jobs.length === 0 ? (
            <div className="p-12 text-center max-w-sm mx-auto">
              <Cpu className="h-10 w-10 text-slate-300 dark:text-zinc-700 mx-auto mb-3" />
              <h4 className="font-semibold text-slate-800 dark:text-zinc-200 mb-1">No Jobs Run Yet</h4>
              <p className="text-xs text-slate-500 dark:text-zinc-500">Scraping tasks executed manually or via automation will display history here.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-zinc-800 bg-slate-50/50 dark:bg-zinc-900/50 text-xs font-semibold text-slate-500 dark:text-zinc-500 uppercase tracking-wider">
                    <th className="px-6 py-3.5">Brand</th>
                    <th className="px-6 py-3.5">Started At</th>
                    <th className="px-6 py-3.5">Status</th>
                    <th className="px-6 py-3.5">Extracted</th>
                    <th className="px-6 py-3.5">Duration</th>
                    <th className="px-6 py-3.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-zinc-850">
                  {jobs.map((job) => (
                    <tr key={job.id} className="hover:bg-slate-50/50 dark:hover:bg-zinc-900/30 transition-colors">
                      <td className="px-6 py-4 font-medium text-slate-900 dark:text-zinc-50">
                        {job.brand_name}
                      </td>
                      <td className="px-6 py-4 text-xs text-slate-500 dark:text-zinc-500">
                        {formatDate(job.started_at)}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          job.status === "Completed" ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400" :
                          job.status === "Running" ? "bg-amber-500/10 text-amber-600 dark:text-amber-400" :
                          job.status === "Queued" ? "bg-blue-500/10 text-blue-600 dark:text-blue-400" :
                          "bg-red-500/10 text-red-600 dark:text-red-400"
                        }`}>
                          {job.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-xs text-slate-600 dark:text-zinc-400">
                        {job.records_found} parsed
                      </td>
                      <td className="px-6 py-4 text-xs text-slate-500 dark:text-zinc-500">
                        {job.duration_seconds ? `${job.duration_seconds}s` : "--"}
                      </td>
                      <td className="px-6 py-4 text-right">
                        {(job.status === "Running" || job.status === "Queued") ? (
                          <button
                            onClick={() => handleCancelJob(job.id)}
                            disabled={cancellingJobId === job.id}
                            className="text-xs font-semibold text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 disabled:opacity-50 inline-flex items-center gap-1.5"
                          >
                            <Ban className="h-3 w-3" />
                            Cancel
                          </button>
                        ) : (
                          <span className="text-xs text-slate-400 dark:text-zinc-600 font-normal">--</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* ========================================================= */}
      {/* PREVIEW RUN DRAWER/MODAL                                  */}
      {/* ========================================================= */}
      {previewOpen && previewResult && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 dark:bg-black/80 backdrop-blur-sm">
          <div className="w-full max-w-4xl bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-2xl shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-200 flex flex-col max-h-[90vh]">
            
            {/* Header */}
            <div className="px-6 py-4 border-b border-slate-200 dark:border-zinc-800 flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold text-slate-900 dark:text-zinc-50">
                  Scraper Preview: {previewResult.brand_name}
                </h2>
                <p className="text-xs text-slate-500 dark:text-zinc-500">
                  Successfully parsed {previewResult.total_extracted} records. Mock run results only (no database write).
                </p>
              </div>
              <button 
                onClick={() => setPreviewOpen(false)}
                className="p-1 rounded-md text-slate-400 hover:bg-slate-100 dark:hover:bg-zinc-800 hover:text-slate-600 dark:hover:text-zinc-300"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Content Tabs */}
            <div className="flex-grow overflow-y-auto p-6 space-y-6">
              {/* Parsed Dealers Table */}
              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-slate-700 dark:text-zinc-300 uppercase tracking-wider">
                  Extracted Records (Limit 10)
                </h4>
                <div className="border border-slate-150 dark:border-zinc-800 rounded-lg overflow-hidden max-h-64 overflow-y-auto text-xs">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="bg-slate-50 dark:bg-zinc-900 border-b border-slate-150 dark:border-zinc-800 font-semibold text-slate-500 dark:text-zinc-500">
                        <th className="p-3">Dealer</th>
                        <th className="p-3">Address</th>
                        <th className="p-3">Phone</th>
                        <th className="p-3">Validation</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-zinc-850">
                      {previewResult.preview_records.map((rec, i) => (
                        <tr key={i} className="hover:bg-slate-50/30 dark:hover:bg-zinc-900/10">
                          <td className="p-3 font-semibold text-slate-800 dark:text-zinc-200">{rec.name}</td>
                          <td className="p-3 text-slate-600 dark:text-zinc-400">
                            {rec.address}
                            {rec.pincode && <span className="ml-1 font-mono text-[10px] bg-slate-100 dark:bg-zinc-800 px-1 py-0.5 rounded">{rec.pincode}</span>}
                          </td>
                          <td className="p-3 text-slate-600 dark:text-zinc-400 font-mono">{rec.phone || "--"}</td>
                          <td className="p-3">
                            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                              rec.validation_status === "VALID" 
                                ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400" 
                                : "bg-red-500/10 text-red-600 dark:text-red-400"
                            }`}>
                              {rec.validation_status}
                            </span>
                            {rec.validation_errors.length > 0 && (
                              <div className="text-[10px] text-red-500 mt-1 max-w-[200px] leading-tight">
                                * {rec.validation_errors.join(", ")}
                              </div>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Diagnostic Terminal Logs */}
              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-slate-700 dark:text-zinc-300 uppercase tracking-wider flex items-center gap-1">
                  <Terminal className="h-4 w-4 text-indigo-500" />
                  Crawler Console Execution Diagnostics
                </h4>
                <div className="bg-slate-950 text-zinc-300 font-mono text-[10px] p-4 rounded-xl max-h-48 overflow-y-auto space-y-1 shadow-inner leading-relaxed">
                  {previewResult.logs.map((logLine, i) => (
                    <p 
                      key={i} 
                      className={
                        logLine.includes("ERROR") || logLine.includes("failed") ? "text-red-400" :
                        logLine.includes("SUCCESS") || logLine.includes("successful") ? "text-emerald-400" : 
                        "text-zinc-400"
                      }
                    >
                      {logLine}
                    </p>
                  ))}
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="px-6 py-4 bg-slate-50/50 dark:bg-zinc-900/50 border-t border-slate-200 dark:border-zinc-800 flex justify-end">
              <Button size="sm" onClick={() => setPreviewOpen(false)} className="bg-zinc-900 text-zinc-50 dark:bg-zinc-50 dark:text-zinc-950">
                Close Preview
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Toast Notifications */}
      <div className="fixed bottom-6 right-6 z-55 flex flex-col gap-3 w-full max-w-sm">
        {toasts.map((t) => (
          <div 
            key={t.id}
            className={`p-4 rounded-xl border shadow-lg flex items-start gap-3 text-sm animate-in slide-in-from-bottom-5 duration-300 ${
              t.type === "success" 
                ? "bg-white dark:bg-zinc-900 border-emerald-250 dark:border-emerald-900/40 text-emerald-950 dark:text-emerald-450" 
                : "bg-white dark:bg-zinc-900 border-red-250 dark:border-red-900/40 text-red-950 dark:text-red-450"
            }`}
          >
            {t.type === "success" ? (
              <CheckCircle2 className="h-5 w-5 text-emerald-500 flex-shrink-0" />
            ) : (
              <AlertTriangle className="h-5 w-5 text-red-500 flex-shrink-0" />
            )}
            <p className="flex-grow font-medium leading-normal">{t.message}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
