"use client";

import { useState } from "react";
import { EnrichmentResult, BatchStatus } from "@/types";
import { TierBadge } from "@/components/TierBadge";
import { Download, CheckCircle2, XCircle, Clock, Eye, AlertTriangle } from "lucide-react";

interface ResultsCardProps {
  results: EnrichmentResult[];
  status: BatchStatus;
  onSelectResult?: (result: EnrichmentResult) => void;
  onInspectResult?: (result: EnrichmentResult) => void;
}

export function ResultsCard({ results, status, onSelectResult, onInspectResult }: ResultsCardProps) {
  const [inspectingResult, setInspectingResult] = useState<EnrichmentResult | null>(null);

  const downloadCSV = () => {
    const headers = [
      "name", "email", "company", "property_address", "city", "state",
      "tier", "priority_score", "score_rationale",
      "renter_pct", "vacancy_rate", "rent_growth_pct", "median_income",
      "walkscore", "transitscore", "bikescore",
      "first_talking_point", "second_talking_point", "third_talking_point",
      "email_subject", "email_body", 
      "expansion_detected", "funding_detected", "leadership_change", "portfolio_growth",
      "has_yardi_response", "too_expensive_response", "have_team_response",
      "sales_signal", "needs_review", "api_errors"
    ];

    const rows = results.map((r) => {
      const lead = r._lead || { name: "", email: "", company: "", property_address: "", city: "", state: "" };
      const kdp = r.key_data_points || {};
      const email = r.email_draft as { subject?: string; body?: string } | string || { subject: "", body: "" };
      const emailSubject = typeof email === "string" ? "" : (email.subject || "");
      const emailBody = typeof email === "string" ? email : (email.body || "");
      const buying = r.buying_signals || {};
      const objections = r.objection_handling || {};
      const talkingPoints = r.talking_points || [];

      return [
        lead.name || "",
        lead.email || "",
        lead.company || "",
        lead.property_address || "",
        lead.city || "",
        lead.state || "",
        r.tier || "",
        r.priority_score?.toString() || "",
        r.score_rationale || "",
        kdp.renter_pct?.toString() || "",
        kdp.vacancy_rate?.toString() || "",
        kdp.rent_growth_pct?.toString() || "",
        kdp.median_income?.toString() || "",
        kdp.walkscore?.toString() || "",
        kdp.transitscore?.toString() || "",
        kdp.bikescore?.toString() || "",
        talkingPoints[0] || "",
        talkingPoints[1] || "",
        talkingPoints[2] || "",
        (emailSubject || "").replace(/"/g, '""'),
        (emailBody || "").replace(/"/g, '""'),
        buying.expansion_detected ? "true" : "false",
        buying.funding_detected ? "true" : "false",
        buying.leadership_change ? "true" : "false",
        buying.portfolio_growth ? "true" : "false",
        objections.has_yardi || "",
        objections.too_expensive || "",
        objections.have_team || "",
        r.sales_signal || "",
        r._needs_manual_review ? "true" : "false",
        r._api_errors?.join("; ") || "",
      ];
    });

    const csv = [
      headers.join(","),
      ...rows.map((row) => row.map((cell) => `"${cell}"`).join(","))
    ].join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `gtm_leads_${Date.now()}.csv`;
    a.click();
  };

  return (
    <div className="rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
            Batch Results
          </h2>
          {status.currentLead && (
            <p className="text-sm text-zinc-500">
              Processing: {status.currentLead}
            </p>
          )}
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={downloadCSV}
            className="flex items-center gap-2 text-sm text-indigo-600 hover:text-indigo-700"
          >
            <Download className="h-4 w-4" />
            Download CSV
          </button>
        </div>
      </div>

      {/* Tier Priority Summary */}
      <div className="mb-4 rounded-lg border border-zinc-200 bg-zinc-50 p-3 dark:border-zinc-700 dark:bg-zinc-800/50">
        <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-zinc-500">
          Priority Summary
        </h3>
        <div className="flex gap-4">
          <div className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-green-500"></span>
            <span className="text-sm text-zinc-700 dark:text-zinc-300">
              <span className="font-semibold">{status.tierA}</span> Tier A
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-yellow-500"></span>
            <span className="text-sm text-zinc-700 dark:text-zinc-300">
              <span className="font-semibold">{status.tierB}</span> Tier B
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-zinc-400"></span>
            <span className="text-sm text-zinc-700 dark:text-zinc-300">
              <span className="font-semibold">{status.tierC}</span> Tier C
            </span>
          </div>
        </div>
      </div>

      <div className="mb-4 grid grid-cols-4 gap-4">
        <div className="rounded-lg bg-zinc-50 p-3 dark:bg-zinc-800">
          <div className="text-2xl font-bold text-zinc-900 dark:text-zinc-50">
            {status.processed}
            <span className="text-sm font-normal text-zinc-500">/{status.total}</span>
          </div>
          <div className="flex items-center gap-1 text-xs text-zinc-500">
            <Clock className="h-3 w-3" />
            Processed
          </div>
        </div>
        <div className="rounded-lg bg-green-50 p-3 dark:bg-green-950">
          <div className="text-2xl font-bold text-green-600 dark:text-green-400">
            {status.tierA}
          </div>
          <div className="flex items-center gap-1 text-xs text-green-600 dark:text-green-400">
            <CheckCircle2 className="h-3 w-3" />
            Tier A
          </div>
        </div>
        <div className="rounded-lg bg-yellow-50 p-3 dark:bg-yellow-950">
          <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
            {status.tierB}
          </div>
          <div className="flex items-center gap-1 text-xs text-yellow-600 dark:text-yellow-400">
            Tier B
          </div>
        </div>
        <div className="rounded-lg bg-zinc-100 p-3 dark:bg-zinc-700">
          <div className="text-2xl font-bold text-zinc-600 dark:text-zinc-300">
            {status.tierC}
          </div>
          <div className="flex items-center gap-1 text-xs text-zinc-600 dark:text-zinc-400">
            <XCircle className="h-3 w-3" />
            Tier C
          </div>
        </div>
      </div>

      <div className="max-h-[400px] overflow-auto">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-zinc-100 text-xs dark:bg-zinc-800">
            <tr>
              <th className="px-3 py-2 text-left font-medium text-zinc-700 dark:text-zinc-300">
                Company
              </th>
              <th className="px-3 py-2 text-left font-medium text-zinc-700 dark:text-zinc-300">
                City
              </th>
              <th className="px-3 py-2 text-left font-medium text-zinc-700 dark:text-zinc-300">
                State
              </th>
              <th className="px-3 py-2 text-left font-medium text-zinc-700 dark:text-zinc-300">
                Tier
              </th>
              <th className="px-3 py-2 text-right font-medium text-zinc-700 dark:text-zinc-300">
                Renter %
              </th>
              <th className="px-3 py-2 text-right font-medium text-zinc-700 dark:text-zinc-300">
                Vacancy
              </th>
              <th className="px-3 py-2 text-right font-medium text-zinc-700 dark:text-zinc-300">
                Growth
              </th>
              <th className="px-3 py-2 text-center font-medium text-zinc-700 dark:text-zinc-300">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
            {results.map((result, i) => {
              const lead = result._lead || { name: "", email: "", company: "", city: "", state: "" };
              const kdp = result.key_data_points || {};
              const needsReview = result._needs_manual_review;

              return (
                <tr
                  key={i}
                  className={`cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-800 ${
                    needsReview ? "bg-amber-50/50 dark:bg-amber-950/20" : ""
                  }`}
                  onClick={() => onSelectResult?.(result)}
                >
                  <td className="px-3 py-2 font-medium text-zinc-900 dark:text-zinc-50">
                    {lead.company || "Unknown"}
                    {needsReview && (
                      <AlertTriangle className="ml-1 inline h-3 w-3 text-amber-500" />
                    )}
                  </td>
                  <td className="px-3 py-2 text-zinc-600 dark:text-zinc-400">
                    {lead.city || "-"}
                  </td>
                  <td className="px-3 py-2 text-zinc-600 dark:text-zinc-400">
                    {lead.state || "-"}
                  </td>
                  <td className="px-3 py-2">
                    {result.tier && <TierBadge tier={result.tier} />}
                  </td>
                  <td className="px-3 py-2 text-right text-zinc-600 dark:text-zinc-400">
                    {kdp.renter_pct != null ? `${kdp.renter_pct}%` : "—"}
                  </td>
                  <td className="px-3 py-2 text-right text-zinc-600 dark:text-zinc-400">
                    {kdp.vacancy_rate != null ? `${kdp.vacancy_rate}%` : "—"}
                  </td>
                  <td className="px-3 py-2 text-right text-zinc-600 dark:text-zinc-400">
                    {kdp.rent_growth_pct != null ? `${kdp.rent_growth_pct}%` : "—"}
                  </td>
                  <td className="px-3 py-2 text-center">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setInspectingResult(result);
                        onInspectResult?.(result);
                      }}
                      className="rounded p-1 text-zinc-500 hover:bg-zinc-200 dark:hover:bg-zinc-700"
                      title="Inspect API Data"
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {results.length === 0 && (
          <div className="p-8 text-center text-zinc-500">
            No results yet. Upload a CSV to begin.
          </div>
        )}
      </div>

      {status.errors > 0 && (
        <div className="mt-4 rounded-lg border border-amber-200 bg-amber-50 p-3 dark:border-amber-900 dark:bg-amber-950">
          <div className="flex items-center gap-2 text-sm text-amber-800 dark:text-amber-200">
            <AlertTriangle className="h-4 w-4" />
            {status.errors} lead(s) require manual review due to missing data.
          </div>
        </div>
      )}
    </div>
  );
}