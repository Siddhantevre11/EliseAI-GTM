"use client";

import { EnrichmentResult, Lead } from "@/types";
import { TierBadge } from "@/components/TierBadge";
import { MetricGrid } from "@/components/MetricGrid";
import { TalkingPoints } from "@/components/TalkingPoints";
import { EmailPreview } from "@/components/EmailPreview";
import { BuyingSignals } from "@/components/BuyingSignals";
import { ObjectionPrep } from "@/components/ObjectionPrep";
import { CaseStudy } from "@/components/CaseStudy";
import { ROICalculator } from "@/components/ROICalculator";
import { IndustryBenchmark } from "@/components/IndustryBenchmark";
import { SalesSignal } from "@/components/SalesSignal";
import { Building2, MapPin, Mail, AlertTriangle, Eye } from "lucide-react";

interface LeadDetailProps {
  lead: Lead;
  result: EnrichmentResult;
  onInspect?: () => void;
}

export function LeadDetail({ lead, result, onInspect }: LeadDetailProps) {
  const emailDraft = typeof result.email_draft === "string"
    ? { subject: "", body: result.email_draft }
    : result.email_draft;

  const displayName = lead?.name || "Unknown Contact";
  const displayCompany = lead?.company || "Unknown Company";
  const displayCity = lead?.city || "Unknown";
  const displayState = lead?.state || "";
  const displayEmail = lead?.email || "";

  const tierColors = {
    A: "border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950/30",
    B: "border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-950/30",
    C: "border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-900",
    default: "border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900"
  };

  const borderClass = tierColors[result.tier as keyof typeof tierColors] || tierColors.default;

  return (
    <div className="space-y-4">
      <div className={`rounded-xl border p-4 ${borderClass}`}>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="mb-2 flex items-center gap-3">
              <h2 className="text-xl font-bold text-zinc-900 dark:text-zinc-50">
                {displayCompany}
              </h2>
              <TierBadge tier={result.tier} />
              {result._needs_manual_review && (
                <span className="flex items-center gap-1 rounded bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700 dark:bg-amber-900 dark:text-amber-300">
                  <AlertTriangle className="h-3 w-3" />
                  Needs Review
                </span>
              )}
              {onInspect && (
                <button
                  onClick={onInspect}
                  className="flex items-center gap-1 rounded bg-zinc-100 px-2 py-1 text-xs text-zinc-600 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-400 dark:hover:bg-zinc-700"
                >
                  <Eye className="h-3 w-3" />
                  API Data
                </button>
              )}
            </div>
            <div className="flex flex-wrap gap-4 text-sm text-zinc-600 dark:text-zinc-400">
              <span className="flex items-center gap-1">
                <Building2 className="h-4 w-4" />
                {displayName}
              </span>
              <span className="flex items-center gap-1">
                <MapPin className="h-4 w-4" />
                {displayCity}{displayState ? `, ${displayState}` : ""}
              </span>
              {displayEmail && (
                <span className="flex items-center gap-1">
                  <Mail className="h-4 w-4" />
                  {displayEmail}
                </span>
              )}
            </div>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-indigo-600">
              {result.priority_score ?? "—"}
            </div>
            <div className="text-xs text-zinc-500">Priority Score</div>
          </div>
        </div>

        {result.score_rationale && (
          <div className="mt-3 rounded-lg bg-white/50 p-3 dark:bg-zinc-900/50">
            <p className="text-sm text-zinc-700 dark:text-zinc-300">
              {result.score_rationale}
            </p>
          </div>
        )}
      </div>

      {result.key_data_points && (
        <MetricGrid dataPoints={result.key_data_points} />
      )}

      {result.sales_signal && (
        <SalesSignal
          signal={result.sales_signal}
          priorityScore={result.priority_score}
        />
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="space-y-4">
          {result.talking_points && result.talking_points.length > 0 && (
            <TalkingPoints points={result.talking_points} />
          )}

          {result.buying_signals && (
            <BuyingSignals signals={result.buying_signals} />
          )}

          {result.peer_case_study && (
            <CaseStudy caseStudy={result.peer_case_study} />
          )}
        </div>

        <div className="space-y-4">
          <EmailPreview email={emailDraft} />

          {result.objection_handling && Object.keys(result.objection_handling).length > 0 && (
            <ObjectionPrep objections={result.objection_handling} />
          )}

          {result.roi_estimate && (
            <ROICalculator roi={result.roi_estimate} />
          )}

          {result.industry_benchmark && (
            <IndustryBenchmark benchmark={result.industry_benchmark} />
          )}
        </div>
      </div>

      {result.decision_maker_context && (
        <div className="rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
          <h3 className="mb-3 text-sm font-medium text-zinc-900 dark:text-zinc-50">
            Decision-Maker Context
          </h3>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <p className="text-xs text-zinc-500">Company Size</p>
              <p className="font-medium text-zinc-900 dark:text-zinc-100">
                {result.decision_maker_context.company_size_tier}
              </p>
            </div>
            <div>
              <p className="text-xs text-zinc-500">Typical Buyer</p>
              <p className="font-medium text-zinc-900 dark:text-zinc-100">
                {result.decision_maker_context.typical_buyer || "—"}
              </p>
            </div>
            <div>
              <p className="text-xs text-zinc-500">Primary Pain Point</p>
              <p className="font-medium text-zinc-900 dark:text-zinc-100">
                {result.decision_maker_context.primary_pain_point || "—"}
              </p>
            </div>
            <div>
              <p className="text-xs text-zinc-500">What They Google</p>
              <p className="font-medium text-zinc-900 dark:text-zinc-100">
                {result.decision_maker_context.what_they_google || "—"}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}