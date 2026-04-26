"use client";

import { useState, useMemo } from "react";
import { EnrichmentResult } from "@/types";
import { Search, Upload, User } from "lucide-react";
import { BatchUpload } from "./BatchUpload";
import { LeadForm } from "./LeadForm";

const SMART_VIEWS: { id: string; label: string; tier: string }[] = [
  { id: "all", label: "All Leads", tier: "all" },
  { id: "a", label: "Tier A Priority", tier: "A" },
  { id: "b", label: "Tier B Potential", tier: "B" },
  { id: "c", label: "Tier C Nurture", tier: "C" },
  { id: "review", label: "Needs Review", tier: "NEEDS_REVIEW" },
];

interface LeadListProps {
  results: EnrichmentResult[];
  selectedResult: EnrichmentResult | null;
  onSelectResult: (result: EnrichmentResult) => void;
  onBatchComplete: (results: EnrichmentResult[], status: any) => void;
  onProcessingChange: (processing: boolean) => void;
  onProgress: (current: number, total: number, company: string) => void;
  onLeadEnriched: (result: EnrichmentResult, counts: { tierA: number; tierB: number; tierC: number; errors: number }) => void;
  onLeadSubmit: (lead: any) => void;
  isProcessing: boolean;
  tierFilter: string;
  onTierFilterChange: (tier: string) => void;
}

export function LeadList({
  results,
  selectedResult,
  onSelectResult,
  onBatchComplete,
  onProcessingChange,
  onProgress,
  onLeadEnriched,
  onLeadSubmit,
  isProcessing,
  tierFilter,
  onTierFilterChange,
}: LeadListProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [showInput, setShowInput] = useState(false);

  const tierCounts = useMemo(() => {
    const counts: Record<string, number> = { all: results.length, A: 0, B: 0, C: 0, NEEDS_REVIEW: 0 };
    results.forEach((r) => {
      if (r.tier === "A") counts.A++;
      else if (r.tier === "B") counts.B++;
      else if (r.tier === "C") counts.C++;
      else if (r.tier === "NEEDS_REVIEW") counts.NEEDS_REVIEW++;
    });
    return counts;
  }, [results]);

  const handleViewChange = (tier: string) => {
    onTierFilterChange(tier);
  };

  const getTierCount = (tier: string): number => {
    if (tier === "all") return results.length;
    return tierCounts[tier] || 0;
  };

  return (
    <div className="flex h-full flex-col p-4">
      <div className="mb-4 space-y-3">
        <div className="flex gap-2">
          <button
            onClick={() => setShowInput(false)}
            className={`flex flex-1 items-center justify-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
              !showInput
                ? "bg-indigo-600 text-white"
                : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700 hover:text-zinc-200"
            }`}
          >
            <Upload className="h-4 w-4" />
            Upload
          </button>
          <button
            onClick={() => setShowInput(true)}
            className={`flex flex-1 items-center justify-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
              showInput
                ? "bg-indigo-600 text-white"
                : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700 hover:text-zinc-200"
            }`}
          >
            <User className="h-4 w-4" />
            Single Lead
          </button>
        </div>

        {!showInput ? (
          <BatchUpload
            onComplete={onBatchComplete}
            onProcessingChange={onProcessingChange}
            onProgress={onProgress}
            onLeadEnriched={onLeadEnriched}
          />
        ) : (
          <div className="rounded-lg bg-zinc-900 p-3">
            <LeadForm onSubmit={onLeadSubmit} isProcessing={isProcessing} />
          </div>
        )}
      </div>

      <div className="mb-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" />
          <input
            type="text"
            placeholder="Search company..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-2 pl-10 pr-3 text-sm text-zinc-100 placeholder:text-zinc-600 focus:border-indigo-500 focus:outline-none"
          />
        </div>
      </div>

      <div className="mb-4">
        <p className="mb-2 text-xs font-semibold tracking-wider text-zinc-500 uppercase">
          Smart Views
        </p>
        <div className="space-y-1">
          {SMART_VIEWS.map((view) => {
            const isActive = tierFilter === view.tier;
            const count = getTierCount(view.tier);
            
            return (
              <button
                key={view.id}
                onClick={() => handleViewChange(view.tier!)}
                className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActive
                    ? "bg-zinc-800 text-zinc-100"
                    : "text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-300"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span>{view.label}</span>
                  <span className={`text-xs ${isActive ? "text-zinc-400" : "text-zinc-600"}`}>
                    {count}
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}