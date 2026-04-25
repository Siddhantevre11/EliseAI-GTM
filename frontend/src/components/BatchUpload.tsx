"use client";

import { useState, useRef, useCallback } from "react";
import { EnrichmentResult, Lead, BatchStatus } from "@/types";
import { Upload, Loader2, FileSpreadsheet } from "lucide-react";

interface BatchUploadProps {
  onComplete: (results: EnrichmentResult[], status: BatchStatus) => void;
  onProcessingChange: (processing: boolean) => void;
  onProgress?: (current: number, total: number, company: string) => void;
}

export function BatchUpload({ onComplete, onProcessingChange, onProgress }: BatchUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [totalLeads, setTotalLeads] = useState(0);
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

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      await handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file: File) => {
    if (!file.name.endsWith(".csv")) {
      alert("Please upload a CSV file");
      return;
    }
    setFile(file);
  };

  const processBatch = useCallback(async () => {
    if (!file) return;

    setIsProcessing(true);
    onProcessingChange(true);

    const text = await file.text();
    const lines = text.split("\n").filter((line) => line.trim());
    const headers = lines[0].split(",").map((h) => h.trim().toLowerCase());

    const leads: Lead[] = [];
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(",");
      const leadData: Record<string, string> = {};
      
      // Map CSV columns to lead fields
      headers.forEach((header, index) => {
        const headerMap: Record<string, string> = {
          "first name": "first_name",
          "last name": "last_name",
          "email": "email",
          "company": "company",
          "property address": "property_address",
          "city": "city",
          "state": "state",
          "zip": "zip",
        };
        const field = headerMap[header];
        if (field) {
          leadData[field] = values[index]?.trim() || "";
        }
      });
      
      // Combine First Name + Last Name → name
      const firstName = leadData["first_name"] || "";
      const lastName = leadData["last_name"] || "";
      const fullName = `${firstName} ${lastName}`.trim();
      
      // Create lead object with all fields
      const lead: Lead = {
        name: fullName,
        email: leadData["email"] || "",
        company: leadData["company"] || "",
        property_address: leadData["property_address"] || "",
        city: leadData["city"] || "",
        state: leadData["state"] || "",
      };
      
      if (lead.company || lead.name) {
        leads.push(lead);
      }
    }

    setTotalLeads(leads.length);

    const status: BatchStatus = {
      total: leads.length,
      processed: 0,
      tierA: 0,
      tierB: 0,
      tierC: 0,
      errors: 0,
    };

    const results: EnrichmentResult[] = [];

    for (let i = 0; i < leads.length; i++) {
      const lead = leads[i];
      setCurrentIndex(i + 1);
      onProgress?.(i + 1, leads.length, `${lead.company} (${lead.city}, ${lead.state})`);

      try {
        const response = await fetch("/api/enrich", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(lead),
        });

        const result = await response.json();
        results.push(result);

        status.processed++;
        if (result.tier === "A") status.tierA++;
        else if (result.tier === "B") status.tierB++;
        else if (result.tier === "C") status.tierC++;
        if (result._needs_manual_review) status.errors++;
      } catch (error) {
        results.push({
          tier: "C",
          priority_score: 0,
          score_rationale: "Manual research required due to data gaps: API call failed",
          email_draft: { subject: "", body: "" },
          talking_points: [],
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
          roi_estimate: {
            prospect_units: 0,
            inquiries_per_month_est: 0,
            avg_inquiry_handling_min: 0,
            time_saved_hours_month: 0,
            staff_cost_per_hour: 0,
            monthly_savings: 0,
            eliseai_cost_monthly: 0,
            net_monthly_roi: 0,
            annual_savings: 0,
          },
          decision_maker_context: {
            company_size_tier: "Local",
            typical_buyer: "",
            primary_pain_point: "",
            what_they_google: "",
          },
          industry_benchmark: {
            avg_response_time_hours: 4.2,
            prospect_response_time: 0,
            avg_vacancy_rate: 4.1,
            prospect_market_vacancy: 0,
            avg_rent_growth: 2.8,
            prospect_market_rent_growth: 0,
          },
          estimated_time_saved_minutes: 0,
          _needs_manual_review: true,
          _api_errors: ["API call failed"],
          _lead: lead,
        });
        status.errors++;
      }

      onComplete(results, { ...status });
    }

    setIsProcessing(false);
    onProcessingChange(false);
  }, [file, onComplete, onProcessingChange, onProgress]);

  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
      <h2 className="mb-4 text-lg font-semibold text-zinc-900 dark:text-zinc-50">
        Batch Upload
      </h2>

      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`relative cursor-pointer rounded-lg border-2 border-dashed p-8 text-center transition-colors ${
          dragActive
            ? "border-indigo-500 bg-indigo-50 dark:bg-indigo-950"
            : "border-zinc-300 dark:border-zinc-700"
        }`}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          className="hidden"
        />
        {file ? (
          <div className="flex flex-col items-center gap-2">
            <FileSpreadsheet className="h-8 w-8 text-indigo-600" />
            <p className="text-sm font-medium text-zinc-900 dark:text-zinc-50">
              {file.name}
            </p>
            <p className="text-xs text-zinc-500">Click to change file</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <Upload className="h-8 w-8 text-zinc-400" />
            <p className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
              Drop CSV file here or click to upload
            </p>
            <p className="text-xs text-zinc-500">
              Required columns: company, city, state
            </p>
          </div>
        )}
      </div>

      {file && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            processBatch();
          }}
          disabled={isProcessing}
          className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:opacity-50"
        >
          {isProcessing ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Processing {currentIndex}/{totalLeads}...
            </>
          ) : (
            <>
              <Upload className="h-4 w-4" />
              Process Batch
            </>
          )}
        </button>
      )}
    </div>
  );
}