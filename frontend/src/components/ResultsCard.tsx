"use client";

import { useState } from "react";
import { EnrichmentResult, BatchStatus } from "@/types";
import { TierBadge } from "@/components/TierBadge";
import { Download, CheckCircle2, AlertTriangle, Eye, Slack, Sheet } from "lucide-react";

interface ResultsCardProps {
  results: EnrichmentResult[];
  status: BatchStatus;
  onSelectResult?: (result: EnrichmentResult) => void;
  onInspectResult?: (result: EnrichmentResult) => void;
  selectedCompany?: string;
}

export function ResultsCard({ results, status, onSelectResult, onInspectResult, selectedCompany }: ResultsCardProps) {
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
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-zinc-500 uppercase tracking-wide">Processed:</span>
            <span className="font-mono text-lg font-bold text-zinc-900 dark:text-zinc-50">
              {status.processed}
              <span className="text-xs font-normal text-zinc-400">/{status.total}</span>
            </span>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-green-500"></span>
              <span className="font-mono text-sm font-semibold text-green-600">{status.tierA}</span>
              <span className="text-xs text-zinc-500">A</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-yellow-500"></span>
              <span className="font-mono text-sm font-semibold text-yellow-600">{status.tierB}</span>
              <span className="text-xs text-zinc-500">B</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-zinc-400"></span>
              <span className="font-mono text-sm font-semibold text-zinc-500">{status.tierC}</span>
              <span className="text-xs text-zinc-500">C</span>
            </div>
          </div>
          {status.errors > 0 && (
            <div className="flex items-center gap-1.5 text-xs text-amber-600">
              <AlertTriangle className="h-3 w-3" />
              <span>{status.errors} review</span>
            </div>
          )}
        </div>
        <button
          onClick={downloadCSV}
          className="flex items-center gap-2 text-xs text-indigo-600 hover:text-indigo-700"
        >
          <Download className="h-3.5 w-3.5" />
          Export CSV
        </button>
      </div>

      <div className="max-h-[500px] overflow-auto">
        <table className="w-full text-xs">
          <thead className="sticky top-0 bg-zinc-100 text-xs font-medium uppercase tracking-wide text-zinc-500 dark:bg-zinc-800">
            <tr>
              <th className="px-3 py-2 text-left">Company</th>
              <th className="px-3 py-2 text-left">Market</th>
              <th className="px-3 py-2 text-center">Tier</th>
              <th className="px-3 py-2 text-right">Renter %</th>
              <th className="px-3 py-2 text-right">Rent Growth</th>
              <th className="px-3 py-2 text-center">Delivery</th>
              <th className="px-3 py-2 text-center">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
            {results.map((result, i) => {
              const lead = result._lead || { name: "", email: "", company: "", city: "", state: "" };
              const kdp = result.key_data_points || {};
              const needsReview = result._needs_manual_review;
              const isSelected = selectedCompany === lead.company;

              return (
                <tr
                  key={i}
                  className={`cursor-pointer transition-colors ${
                    isSelected 
                      ? "bg-indigo-50 dark:bg-indigo-950/30" 
                      : needsReview 
                        ? "bg-amber-50/30 dark:bg-amber-950/10" 
                        : "hover:bg-zinc-50 dark:hover:bg-zinc-800/50"
                  }`}
                  onClick={() => onSelectResult?.(result)}
                >
                  <td className="px-3 py-2">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-zinc-900 dark:text-zinc-100">
                        {lead.company || "Unknown"}
                      </span>
                      {needsReview && (
                        <AlertTriangle className="h-3 w-3 text-amber-500" />
                      )}
                    </div>
                  </td>
                  <td className="px-3 py-2 text-zinc-600 dark:text-zinc-400">
                    {lead.city}, {lead.state}
                  </td>
                  <td className="px-3 py-2 text-center">
                    {result.tier && <TierBadge tier={result.tier} small />}
                  </td>
                  <td className="px-3 py-2 text-right font-mono text-zinc-600 dark:text-zinc-400">
                    {kdp.renter_pct != null ? `${kdp.renter_pct}%` : "—"}
                  </td>
                  <td className="px-3 py-2 text-right font-mono text-zinc-600 dark:text-zinc-400">
                    {kdp.rent_growth_pct != null ? (
                      <span className={kdp.rent_growth_pct > 0 ? "text-green-600" : kdp.rent_growth_pct < 0 ? "text-red-600" : ""}>
                        {kdp.rent_growth_pct > 0 ? "+" : ""}{kdp.rent_growth_pct}%
                      </span>
                    ) : "—"}
                  </td>
                  <td className="px-3 py-2 text-center">
                    <div className="flex items-center justify-center gap-2">
                      <div className="flex items-center gap-1 text-green-600" title="Sent to Slack">
                        <Slack className="h-3.5 w-3.5" />
                      </div>
                      <div className="flex items-center gap-1 text-green-600" title="Written to Sheets">
                        <Sheet className="h-3.5 w-3.5" />
                      </div>
                    </div>
                  </td>
                  <td className="px-3 py-2 text-center">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setInspectingResult(result);
                        onInspectResult?.(result);
                      }}
                      className="rounded p-1 text-zinc-400 hover:bg-zinc-200 hover:text-zinc-600 dark:hover:bg-zinc-700 dark:hover:text-zinc-300"
                      title="Inspect API Data"
                    >
                      <Eye className="h-3.5 w-3.5" />
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
    </div>
  );
}