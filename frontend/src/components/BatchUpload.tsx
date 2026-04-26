"use client";

import { useState, useRef } from "react";
import { EnrichmentResult, Lead, BatchStatus } from "@/types";
import { Upload, Loader2, FileSpreadsheet, AlertCircle } from "lucide-react";

interface BatchUploadProps {
  onComplete: (results: EnrichmentResult[], status: BatchStatus) => void;
  onProcessingChange: (processing: boolean) => void;
  onProgress?: (current: number, total: number, company: string) => void;
  onLeadEnriched?: (result: EnrichmentResult, counts: { tierA: number; tierB: number; tierC: number; errors: number }) => void;
}

export function BatchUpload({ onComplete, onProcessingChange, onProgress, onLeadEnriched }: BatchUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [progress, setProgress] = useState({ current: 0, total: 0, company: "" });
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    setUploadError(null);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    setUploadError(null);
    if (e.target.files && e.target.files[0]) {
      await handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file: File) => {
    const validExtensions = [".csv", ".xlsx", ".xls"];
    const hasValidExtension = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));

    if (!hasValidExtension) {
      setUploadError("Unsupported file format. Please upload CSV or XLSX.");
      return;
    }

    const MAX_SIZE = 20 * 1024 * 1024;
    if (file.size > MAX_SIZE) {
      setUploadError("File size exceeds 20MB limit.");
      return;
    }

    setFile(file);
    await processFile(file);
  };

  const processFile = async (file: File) => {
    setIsUploading(true);
    setUploadError(null);
    onProcessingChange(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("/api/upload-leads", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        setUploadError(data.error || "Upload failed. Please try again.");
        setIsUploading(false);
        onProcessingChange(false);
        return;
      }

      const rawLeads = data.leads;
      const total = rawLeads.length;
      setProgress({ current: 0, total, company: "" });

      const enrichedResults: EnrichmentResult[] = [];
      let tierA = 0, tierB = 0, tierC = 0, errors = 0;

      for (let i = 0; i < rawLeads.length; i++) {
        const rawLead = rawLeads[i];
        const lead: Lead = {
          name: rawLead.name || "",
          email: rawLead.email || "",
          company: rawLead.company || "",
          property_address: rawLead.property_address || "",
          city: rawLead.city === "[MISSING]" ? "" : rawLead.city,
          state: rawLead.state === "[MISSING]" ? "" : rawLead.state,
        };

        setProgress({ current: i + 1, total, company: lead.company });
        onProgress?.(i + 1, total, lead.company);

        try {
          const enrichResponse = await fetch("/api/enrich", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(lead),
          });

          let enriched: EnrichmentResult;

          if (enrichResponse.ok) {
            enriched = await enrichResponse.json();
            if (enriched.tier === "A") tierA++;
            else if (enriched.tier === "B") tierB++;
            else tierC++;
          } else {
            enriched = {
              tier: null,
              priority_score: 0,
              score_rationale: "Enrichment failed",
              key_data_points: {
                renter_pct: null,
                vacancy_rate: null,
                rent_growth_pct: null,
                median_income: null,
                total_renter_units: null,
                top_news_headline: null,
                company_summary: null,
                walkscore: null,
                transitscore: null,
                bikescore: null,
                walkscore_description: null,
                data_source: null,
                is_fallback: null,
                rent_growth_is_fallback: null,
              },
              sales_signal: "",
              talking_points: [],
              email_draft: { subject: "", body: "" },
              buying_signals: {
                expansion_detected: false,
                expansion_detail: null,
                funding_detected: false,
                funding_detail: null,
                leadership_change: false,
                leadership_detail: null,
                portfolio_growth: false,
                portfolio_detail: null,
              },
              objection_handling: {},
              peer_case_study: {
                similar_company: "",
                company_size: "",
                market: "",
                challenge: "",
                result: "",
              },
              roi_estimate: {},
              decision_maker_context: {
                company_size_tier: "Local",
                typical_buyer: "",
                primary_pain_point: "",
                what_they_google: "",
              },
              industry_benchmark: {
                avg_response_time_hours: 0,
                prospect_response_time: 0,
                avg_vacancy_rate: 0,
                prospect_market_vacancy: 0,
                avg_rent_growth: 0,
                prospect_market_rent_growth: 0,
              },
              estimated_time_saved_minutes: 0,
              _lead: lead,
              _needs_manual_review: rawLead.requires_review || false,
            };
            errors++;
          }

          enrichedResults.push(enriched);
          onLeadEnriched?.(enriched, { tierA, tierB, tierC, errors });
        } catch (err) {
          errors++;
          enrichedResults.push({
            tier: null,
            priority_score: 0,
            score_rationale: "Enrichment failed",
            key_data_points: {
              renter_pct: null,
              vacancy_rate: null,
              rent_growth_pct: null,
              median_income: null,
              total_renter_units: null,
              top_news_headline: null,
              company_summary: null,
              walkscore: null,
              transitscore: null,
              bikescore: null,
              walkscore_description: null,
              data_source: null,
              is_fallback: null,
              rent_growth_is_fallback: null,
            },
            sales_signal: "",
            talking_points: [],
            email_draft: { subject: "", body: "" },
            buying_signals: {
              expansion_detected: false,
              expansion_detail: null,
              funding_detected: false,
              funding_detail: null,
              leadership_change: false,
              leadership_detail: null,
              portfolio_growth: false,
              portfolio_detail: null,
            },
            objection_handling: {},
            peer_case_study: {
              similar_company: "",
              company_size: "",
              market: "",
              challenge: "",
              result: "",
            },
            roi_estimate: {},
            decision_maker_context: {
              company_size_tier: "Local" as const,
              typical_buyer: "",
              primary_pain_point: "",
              what_they_google: "",
            },
            industry_benchmark: {
              avg_response_time_hours: 0,
              prospect_response_time: 0,
              avg_vacancy_rate: 0,
              prospect_market_vacancy: 0,
              avg_rent_growth: 0,
              prospect_market_rent_growth: 0,
            },
            estimated_time_saved_minutes: 0,
            _lead: lead,
            _needs_manual_review: rawLead.requires_review || false,
          });
          const failedEnriched: EnrichmentResult = {
            tier: null,
            priority_score: 0,
            score_rationale: "Enrichment failed",
            key_data_points: {
              renter_pct: null,
              vacancy_rate: null,
              rent_growth_pct: null,
              median_income: null,
              total_renter_units: null,
              top_news_headline: null,
              company_summary: null,
              walkscore: null,
              transitscore: null,
              bikescore: null,
              walkscore_description: null,
              data_source: null,
              is_fallback: null,
              rent_growth_is_fallback: null,
            },
            sales_signal: "",
            talking_points: [],
            email_draft: { subject: "", body: "" },
            buying_signals: {
              expansion_detected: false,
              expansion_detail: null,
              funding_detected: false,
              funding_detail: null,
              leadership_change: false,
              leadership_detail: null,
              portfolio_growth: false,
              portfolio_detail: null,
            },
            objection_handling: {},
            peer_case_study: {
              similar_company: "",
              company_size: "",
              market: "",
              challenge: "",
              result: "",
            },
            roi_estimate: {},
            decision_maker_context: {
              company_size_tier: "Local" as const,
              typical_buyer: "",
              primary_pain_point: "",
              what_they_google: "",
            },
            industry_benchmark: {
              avg_response_time_hours: 0,
              prospect_response_time: 0,
              avg_vacancy_rate: 0,
              prospect_market_vacancy: 0,
              avg_rent_growth: 0,
              prospect_market_rent_growth: 0,
            },
            estimated_time_saved_minutes: 0,
            _lead: lead,
            _needs_manual_review: rawLead.requires_review || false,
          };
          onLeadEnriched?.(failedEnriched, { tierA, tierB, tierC, errors });
        }
      }

      const status: BatchStatus = {
        total,
        processed: total,
        tierA,
        tierB,
        tierC,
        errors,
      };

      onComplete(enrichedResults, status);
      setFile(null);
    } catch (error) {
      setUploadError("Upload failed. Please try again.");
    } finally {
      setIsUploading(false);
      onProcessingChange(false);
      setProgress({ current: 0, total: 0, company: "" });
    }
  };

  return (
    <div className="rounded-lg bg-zinc-900 p-4">
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => !isUploading && fileInputRef.current?.click()}
        className={`relative cursor-pointer rounded-lg border-2 border-dashed p-6 text-center transition-colors ${
          dragActive
            ? "border-indigo-500 bg-indigo-950/30"
            : uploadError
            ? "border-red-500/50"
            : "border-zinc-700 hover:border-zinc-600"
        } ${isUploading ? "pointer-events-none opacity-60" : ""}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={handleFileChange}
          className="hidden"
          disabled={isUploading}
        />

        {isUploading ? (
          <div className="flex flex-col items-center gap-2">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
            <p className="text-sm font-medium text-zinc-300">
              Enriching {progress.current} of {progress.total}...
            </p>
            {progress.company && (
              <p className="text-xs text-zinc-500 truncate max-w-[200px]">
                {progress.company}
              </p>
            )}
          </div>
        ) : file ? (
          <div className="flex flex-col items-center gap-2">
            <FileSpreadsheet className="h-8 w-8 text-emerald-500" />
            <p className="text-sm font-medium text-zinc-200">{file.name}</p>
            <p className="text-xs text-zinc-500">Click to change file</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <Upload className="h-8 w-8 text-zinc-500" />
            <p className="text-sm font-medium text-zinc-300">
              Drop file here or click to upload
            </p>
            <p className="text-xs text-zinc-500">
              CSV, XLSX (max 100 rows, 20MB)
            </p>
          </div>
        )}
      </div>

      {uploadError && (
        <div className="mt-3 flex items-center gap-2 text-red-400 text-sm">
          <AlertCircle className="h-4 w-4" />
          <span>{uploadError}</span>
        </div>
      )}
    </div>
  );
}