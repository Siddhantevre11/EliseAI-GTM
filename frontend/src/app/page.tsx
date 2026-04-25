"use client";

import { useState, useCallback } from "react";
import { LeadForm } from "@/components/LeadForm";
import { BatchUpload } from "@/components/BatchUpload";
import { LeadDetail } from "@/components/LeadDetail";
import { ResultsCard } from "@/components/ResultsCard";
import { InspectDrawer } from "@/components/InspectDrawer";
import { EnrichmentResult, Lead, BatchStatus } from "@/types";
import { Zap, Users, TrendingUp, Clock, RefreshCw } from "lucide-react";

type View = "input" | "batch";

export default function Home() {
  const [currentResult, setCurrentResult] = useState<EnrichmentResult | null>(null);
  const [currentLead, setCurrentLead] = useState<Lead | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [batchResults, setBatchResults] = useState<EnrichmentResult[]>([]);
  const [batchStatus, setBatchStatus] = useState<BatchStatus | null>(null);
  const [view, setView] = useState<View>("input");
  const [showInspector, setShowInspector] = useState(false);
  const [inspectingResult, setInspectingResult] = useState<EnrichmentResult | null>(null);

  const handleLeadSubmit = async (lead: Lead) => {
    setIsProcessing(true);
    setCurrentLead(lead);
    setCurrentResult(null);

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
      setCurrentResult(result);
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleBatchComplete = useCallback((results: EnrichmentResult[], status: BatchStatus) => {
    setBatchResults(results);
    setBatchStatus(status);
  }, []);

  const handleBatchProgress = useCallback((current: number, total: number, company: string) => {
    setBatchStatus(prev => prev ? {
      ...prev,
      processed: current,
      total: total,
      currentLead: `${company} (${current}/${total})`
    } : null);
  }, []);

  const handleSelectResult = (result: EnrichmentResult) => {
    setCurrentResult(result);
    setCurrentLead(result._lead as Lead || null);
  };

  const handleInspectResult = (result: EnrichmentResult) => {
    setInspectingResult(result);
    setShowInspector(true);
  };

  const handleNewLead = () => {
    setCurrentResult(null);
    setCurrentLead(null);
  };

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950">
      <header className="sticky top-0 z-50 border-b border-zinc-200 bg-white/95 px-6 py-4 backdrop-blur dark:border-zinc-800 dark:bg-zinc-900/95">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600">
              <Zap className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-zinc-900 dark:text-zinc-50">
                EliseAI GTM
              </h1>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">
                Lead Enrichment Engine
              </p>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <div className="hidden items-center gap-4 text-sm text-zinc-500 lg:flex">
              <span className="flex items-center gap-1.5">
                <Users className="h-4 w-4" />
                4 APIs
              </span>
              <span className="flex items-center gap-1.5">
                <TrendingUp className="h-4 w-4" />
                Strategy A/B/C
              </span>
              <span className="flex items-center gap-1.5">
                <Clock className="h-4 w-4" />
                45 min saved/lead
              </span>
            </div>

            {currentResult && (
              <button
                onClick={handleNewLead}
                className="flex items-center gap-2 rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700"
              >
                <RefreshCw className="h-4 w-4" />
                New Lead
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-8">
        {currentResult && currentLead ? (
          <LeadDetail lead={currentLead} result={currentResult} />
        ) : (
          <div className="grid gap-8 lg:grid-cols-2">
            <div className="space-y-6">
              <div className="flex gap-2">
                <button
                  onClick={() => setView("input")}
                  className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                    view === "input"
                      ? "bg-indigo-600 text-white"
                      : "bg-white text-zinc-700 hover:bg-zinc-100 dark:bg-zinc-800 dark:text-zinc-300"
                  }`}
                >
                  Single Lead
                </button>
                <button
                  onClick={() => setView("batch")}
                  className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                    view === "batch"
                      ? "bg-indigo-600 text-white"
                      : "bg-white text-zinc-700 hover:bg-zinc-100 dark:bg-zinc-800 dark:text-zinc-300"
                  }`}
                >
                  Batch Upload
                </button>
              </div>

              {view === "input" ? (
                <LeadForm onSubmit={handleLeadSubmit} isProcessing={isProcessing} />
              ) : (
                <BatchUpload
                  onComplete={handleBatchComplete}
                  onProcessingChange={setIsProcessing}
                  onProgress={handleBatchProgress}
                />
              )}
            </div>

            <div className="space-y-6">
              {batchResults.length > 0 && batchStatus && (
                <ResultsCard
                  results={batchResults}
                  status={batchStatus}
                  onSelectResult={handleSelectResult}
                  onInspectResult={handleInspectResult}
                />
              )}

              {batchResults.length === 0 && (
                <div className="rounded-xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
                  <h2 className="mb-4 text-lg font-semibold text-zinc-900 dark:text-zinc-50">
                    How It Works
                  </h2>
                  <ol className="space-y-4">
                    <Step number={1} title="Upload Leads" description="CSV with company, city, state" />
                    <Step number={2} title="Enrich Data" description="Census, FRED, News APIs" />
                    <Step number={3} title="AI Scoring" description="Tier A/B/C + Email" />
                    <Step number={4} title="Export" description="Sales battlecard CSV" />
                  </ol>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      <InspectDrawer
        isOpen={showInspector}
        onClose={() => setShowInspector(false)}
        rawData={inspectingResult?._raw_data || {}}
        company={inspectingResult?._lead?.company}
        city={inspectingResult?._lead?.city}
      />
    </div>
  );
}

function Step({
  number,
  title,
  description,
}: {
  number: number;
  title: string;
  description: string;
}) {
  return (
    <li className="flex gap-4">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-sm font-bold text-indigo-600 dark:bg-indigo-900 dark:text-indigo-400">
        {number}
      </div>
      <div>
        <h3 className="text-sm font-medium text-zinc-900 dark:text-zinc-50">{title}</h3>
        <p className="text-sm text-zinc-500">{description}</p>
      </div>
    </li>
  );
}