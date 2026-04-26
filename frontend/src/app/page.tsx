"use client";

import { useState, useCallback, useMemo } from "react";
import { ClayGrid } from "@/components/ClayGrid";
import { LeadList } from "@/components/LeadList";
import { SDRToolkit } from "@/components/SDRToolkit";
import { Toast } from "@/components/Toast";
import { EnrichmentResult, Lead, BatchStatus } from "@/types";
import { Zap, Download, ChevronLeft, ChevronRight } from "lucide-react";

const LEADS_PER_PAGE = 50;

export default function Home() {
  const [currentResult, setCurrentResult] = useState<EnrichmentResult | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [batchResults, setBatchResults] = useState<EnrichmentResult[]>([]);
  const [batchStatus, setBatchStatus] = useState<BatchStatus | null>(null);
  const [tierFilter, setTierFilter] = useState<string>("all");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [currentPage, setCurrentPage] = useState(1);
  const [showSDRToolkit, setShowSDRToolkit] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" | "syncing" | "info" } | null>(null);
  const [integrationStatus, setIntegrationStatus] = useState({
    slack: "online",
    sheets: "syncing",
    webhook: "active",
  });

  const handleLeadSubmit = async (lead: Lead) => {
    setIsProcessing(true);
    setShowSDRToolkit(false);

    try {
      const response = await fetch("/api/enrich", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(lead),
      });

      if (!response.ok) {
        throw new Error("Failed to enrich lead");
      }

      const result = await response.json();
      console.log("Enrichment Result:", {
        tier: result.tier,
        company: result._lead?.company,
        city: result._lead?.city
      });
      setCurrentResult(result);
      setBatchResults([result]);
      setBatchStatus({
        total: 1,
        processed: 1,
        tierA: result.tier === "A" ? 1 : 0,
        tierB: result.tier === "B" ? 1 : 0,
        tierC: result.tier === "C" ? 1 : 0,
        errors: result._needs_manual_review ? 1 : 0,
      });
      setCurrentPage(1);
      setShowSDRToolkit(true);
      setToast({ message: "Lead enriched successfully", type: "success" });
    } catch (error) {
      console.error("Error:", error);
      setToast({ message: "Failed to enrich lead", type: "error" });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleBatchComplete = useCallback((results: EnrichmentResult[], status: BatchStatus) => {
    setBatchResults(results);
    setBatchStatus(status);
    setCurrentPage(1);
    setToast({ message: `Batch complete: ${results.length} leads processed`, type: "success" });
  }, []);

  const handleBatchProgress = useCallback((current: number, total: number, company: string) => {
    setBatchStatus(prev => prev ? {
      ...prev,
      processed: current,
      total: total,
      currentLead: `${company} (${current}/${total})`
    } : null);
  }, []);

  const handleLeadEnriched = useCallback((result: EnrichmentResult, counts: { tierA: number; tierB: number; tierC: number; errors: number }) => {
    setBatchResults(prev => [...prev, result]);
    setBatchStatus(prev => prev ? { ...prev, ...counts } : null);
  }, []);

  const handleSelectResult = (result: EnrichmentResult) => {
    setCurrentResult(result);
    setShowSDRToolkit(true);
  };

  const handleUpdateLead = (index: number, updates: Partial<EnrichmentResult>) => {
    setBatchResults(prev => {
      const newResults = [...prev];
      newResults[index] = { ...newResults[index], ...updates };
      return newResults;
    });

    if (currentResult && batchResults[index]?._lead?.company === currentResult._lead?.company) {
      setCurrentResult(prev => prev ? { ...prev, ...updates } : null);
    }

    if (updates.tier) {
      setToast({ message: "Updating tier...", type: "syncing" });
      setIntegrationStatus(prev => ({ ...prev, sheets: "syncing" }));

      setTimeout(() => {
        setToast({ message: "Tier updated in Sheets", type: "success" });
        setIntegrationStatus(prev => ({ ...prev, sheets: "online" }));
      }, 1500);
    }
  };

  const handleCopyEmail = () => {
    if (currentResult?.email_draft) {
      const email = currentResult.email_draft;
      const emailText = typeof email === "string"
        ? email
        : `${email.subject || ""}\n\n${email.body || ""}`;
      navigator.clipboard.writeText(emailText);
      setToast({ message: "Email copied to clipboard", type: "success" });
    }
  };

  const handleResendToSlack = async () => {
    if (!currentResult?._lead) return;

    setIntegrationStatus(prev => ({ ...prev, slack: "syncing" }));
    setToast({ message: "Posting to Slack...", type: "syncing" });

    try {
      const response = await fetch("/api/slack", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lead: currentResult._lead,
          result: currentResult
        }),
      });

      const data = await response.json();
      if (data.success) {
        setToast({ message: "Posted to Slack", type: "success" });
      } else {
        setToast({ message: data.error || "Failed to post", type: "error" });
      }
    } catch (error) {
      setToast({ message: "Failed to post to Slack", type: "error" });
    }

    setIntegrationStatus(prev => ({ ...prev, slack: "online" }));
  };

  const handleExportToSheets = async () => {
    if (!currentResult?._lead) return;

    setIntegrationStatus(prev => ({ ...prev, sheets: "syncing" }));
    setToast({ message: "Exporting to Sheets...", type: "syncing" });

    try {
      const response = await fetch("/api/sheets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lead: currentResult._lead,
          result: currentResult
        }),
      });

      const data = await response.json();
      if (data.success) {
        setToast({ message: "Exported to Sheets", type: "success" });
      } else {
        setToast({ message: data.error || "Failed to export", type: "error" });
      }
    } catch (error) {
      setToast({ message: "Failed to export to Sheets", type: "error" });
    }

    setIntegrationStatus(prev => ({ ...prev, sheets: "online" }));
  };

  const handleExportCSV = async () => {
    if (batchResults.length === 0) return;

    setToast({ message: "Generating CSV...", type: "syncing" });

    try {
      const response = await fetch("/api/export/csv", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ results: batchResults }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `gtm_leads_${Date.now()}.csv`;
        a.click();
        URL.revokeObjectURL(url);
        setToast({ message: "CSV exported", type: "success" });
      } else {
        setToast({ message: "Failed to generate CSV", type: "error" });
      }
    } catch (error) {
      setToast({ message: "Failed to export CSV", type: "error" });
    }
  };

  const handleSendWebhook = async () => {
    if (!currentResult?._lead || currentResult.tier !== "A") return;

    setToast({ message: "Sending to Webhook...", type: "syncing" });

    try {
      const response = await fetch("/api/webhook", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lead: currentResult._lead,
          result: currentResult
        }),
      });

      const data = await response.json();
      if (data.success) {
        setToast({ message: "Sent to Webhook", type: "success" });
      } else {
        setToast({ message: data.error || "Failed to send", type: "error" });
      }
    } catch (error) {
      setToast({ message: "Failed to send to Webhook", type: "error" });
    }
  };

  const handleTierFilterChange = (tier: string) => {
    setTierFilter(tier);
    setCurrentPage(1);
  };

  const getStatusDot = (status: string) => {
    const colors = {
      online: "bg-emerald-500/50",
      syncing: "bg-amber-500/50",
      active: "bg-emerald-500/50",
      pending: "bg-zinc-600",
      offline: "bg-zinc-600",
    };
    const pulse = status === "syncing" ? "animate-pulse" : "";
    return `h-1.5 w-1.5 rounded-full ${colors[status as keyof typeof colors] || colors.pending} ${pulse}`;
  };

  const filteredResults = useMemo(() => {
    let filtered = tierFilter === "all" ? batchResults : batchResults.filter((r) => r.tier === tierFilter);
    if (searchTerm) {
      const lower = searchTerm.toLowerCase();
      filtered = filtered.filter((r) => {
        const company = (r._lead?.company || "").toLowerCase();
        const name = (r._lead?.name || "").toLowerCase();
        const city = (r._lead?.city || "").toLowerCase();
        return company.includes(lower) || name.includes(lower) || city.includes(lower);
      });
    }
    return filtered;
  }, [batchResults, tierFilter, searchTerm]);

  const totalPages = Math.max(1, Math.ceil(filteredResults.length / LEADS_PER_PAGE));
  const startIndex = (currentPage - 1) * LEADS_PER_PAGE + 1;
  const endIndex = Math.min(currentPage * LEADS_PER_PAGE, filteredResults.length);

  const goToPrevPage = () => {
    if (currentPage > 1) setCurrentPage(currentPage - 1);
  };

  const goToNextPage = () => {
    if (currentPage < totalPages) setCurrentPage(currentPage + 1);
  };

  return (
    <div className="flex h-screen w-full flex-col overflow-hidden bg-zinc-950">
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-zinc-800 bg-zinc-900/95 px-4 backdrop-blur">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <div className="flex flex-col">
            <h1 className="text-lg font-bold text-zinc-50 leading-tight">
              SignalDesk
            </h1>
            <p className="text-[10px] text-zinc-500 leading-none">
              Turn GTM data into instant answers and actions. Elise Signal
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5">
              <span className={getStatusDot(integrationStatus.slack)}></span>
              <span className="text-xs text-zinc-500">
                <span className="hidden sm:inline">Slack:</span> <span className="capitalize">{integrationStatus.slack}</span>
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className={getStatusDot(integrationStatus.sheets)}></span>
              <span className="text-xs text-zinc-500">
                <span className="hidden sm:inline">Sheets:</span> <span className="capitalize">{integrationStatus.sheets}</span>
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className={getStatusDot(integrationStatus.webhook)}></span>
              <span className="text-xs text-zinc-500">
                <span className="hidden sm:inline">Webhook:</span> <span className="capitalize">{integrationStatus.webhook}</span>
              </span>
            </div>
          </div>

          {batchResults.length > 0 && (
            <button
              onClick={handleExportCSV}
              className="flex items-center gap-2 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-indigo-700"
            >
              <Download className="h-3.5 w-3.5" />
              Export
            </button>
          )}
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <aside className="w-72 shrink-0 overflow-hidden border-r border-zinc-800">
          <div className="flex h-full flex-col">
            <div className="flex-1">
              <LeadList
                results={batchResults}
                selectedResult={currentResult}
                onSelectResult={handleSelectResult}
                onBatchComplete={handleBatchComplete}
                onProcessingChange={setIsProcessing}
                onProgress={handleBatchProgress}
                onLeadEnriched={handleLeadEnriched}
                onLeadSubmit={handleLeadSubmit}
                isProcessing={isProcessing}
                tierFilter={tierFilter}
                onTierFilterChange={handleTierFilterChange}
                searchTerm={searchTerm}
                onSearchTermChange={setSearchTerm}
              />
            </div>
            <div className="mt-auto flex items-center justify-center border-t border-zinc-800 px-4 py-4">
              <div className="flex h-9 w-9 items-center justify-center rounded-full border border-zinc-700 bg-zinc-800 text-xs font-medium text-zinc-400">
                N
              </div>
            </div>
          </div>
        </aside>

        <main className={`flex flex-1 min-w-0 flex-col overflow-hidden ${showSDRToolkit ? "mr-[400px]" : ""}`}>
          <div className="flex-1 overflow-auto p-4">
            <ClayGrid
              results={filteredResults}
              selectedResult={currentResult}
              onSelectResult={handleSelectResult}
              onUpdateLead={handleUpdateLead}
            />
          </div>
          {filteredResults.length > 0 && (
            <div className="flex items-center justify-center gap-4 border-t border-zinc-800 bg-zinc-900 px-4 py-3">
              <button
                onClick={goToPrevPage}
                disabled={currentPage === 1}
                className="flex items-center gap-1 rounded-md px-2 py-1 text-sm text-zinc-500 hover:bg-zinc-800 hover:text-zinc-300 disabled:cursor-not-allowed disabled:opacity-40"
              >
                <ChevronLeft className="h-4 w-4" />
                Prev
              </button>

              <div className="text-center">
                <div className="text-sm font-medium text-zinc-300">
                  Page {currentPage} of {totalPages}
                </div>
                <div className="text-xs text-zinc-500">
                  {filteredResults.length > 0 ? `${startIndex}-${endIndex} of ${filteredResults.length}` : "No leads"}
                </div>
              </div>

              <button
                onClick={goToNextPage}
                disabled={currentPage >= totalPages}
                className="flex items-center gap-1 rounded-md px-2 py-1 text-sm text-zinc-500 hover:bg-zinc-800 hover:text-zinc-300 disabled:cursor-not-allowed disabled:opacity-40"
              >
                Next
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          )}
        </main>

        <SDRToolkit
          isOpen={showSDRToolkit}
          onClose={() => setShowSDRToolkit(false)}
          result={currentResult}
          onResendToSlack={handleResendToSlack}
          onCopyEmail={handleCopyEmail}
          onExportToSheets={handleExportToSheets}
        />
      </div>

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}