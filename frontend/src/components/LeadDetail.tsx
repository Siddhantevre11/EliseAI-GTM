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
import { Building2, MapPin, Mail, ExternalLink } from "lucide-react";

interface LeadDetailProps {
  lead: Lead;
  result: EnrichmentResult;
}

export function LeadDetail({ lead, result }: LeadDetailProps) {
  const emailDraft = typeof result.email_draft === "string"
    ? { subject: "", body: result.email_draft }
    : result.email_draft;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="rounded-xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
        <div className="flex items-start justify-between">
          <div>
            <div className="mb-2 flex items-center gap-3">
              <h2 className="text-xl font-bold text-zinc-900 dark:text-zinc-50">
                {lead.company}
              </h2>
              <TierBadge tier={result.tier} />
            </div>
            <div className="flex flex-wrap gap-4 text-sm text-zinc-600 dark:text-zinc-400">
              <span className="flex items-center gap-1">
                <Building2 className="h-4 w-4" />
                {lead.name || "Unknown Contact"}
              </span>
              <span className="flex items-center gap-1">
                <MapPin className="h-4 w-4" />
                {lead.city}, {lead.state}
              </span>
              <span className="flex items-center gap-1">
                <Mail className="h-4 w-4" />
                {lead.email}
              </span>
            </div>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-indigo-600">
              {result.priority_score ?? "—"}
            </div>
            <div className="text-xs text-zinc-500">Priority Score</div>
            {result._needs_manual_review && (
              <span className="mt-1 inline-block rounded bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700">
                Needs Review
              </span>
            )}
          </div>
        </div>

        {result.score_rationale && (
          <div className="mt-4 rounded-lg bg-zinc-50 p-4 dark:bg-zinc-800">
            <p className="text-sm text-zinc-700 dark:text-zinc-300">
              {result.score_rationale}
            </p>
          </div>
        )}
      </div>

      {/* Quick Stats */}
      {result.key_data_points && (
        <MetricGrid dataPoints={result.key_data_points} />
      )}

      {/* Sales Signal */}
      {result.sales_signal && (
        <SalesSignal
          signal={result.sales_signal}
          priorityScore={result.priority_score}
        />
      )}

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Left Column */}
        <div className="space-y-6">
          {/* Talking Points */}
          {result.talking_points && result.talking_points.length > 0 && (
            <TalkingPoints points={result.talking_points} />
          )}

          {/* Buying Signals */}
          {result.buying_signals && (
            <BuyingSignals signals={result.buying_signals} />
          )}

          {/* Case Study */}
          {result.peer_case_study && (
            <CaseStudy caseStudy={result.peer_case_study} />
          )}
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Email Draft */}
          <EmailPreview email={emailDraft} />

          {/* Objection Handling */}
          {result.objection_handling && (
            <ObjectionPrep objections={result.objection_handling} />
          )}

          {/* ROI Calculator */}
          {result.roi_estimate && (
            <ROICalculator roi={result.roi_estimate} />
          )}

          {/* Industry Benchmark */}
          {result.industry_benchmark && (
            <IndustryBenchmark benchmark={result.industry_benchmark} />
          )}
        </div>
      </div>

      {/* Decision Maker Context */}
      {result.decision_maker_context && (
        <div className="rounded-lg border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
          <h3 className="mb-4 text-sm font-medium text-zinc-900 dark:text-zinc-50">
            Decision-Maker Context
          </h3>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <p className="text-xs text-zinc-500">Company Size</p>
              <p className="font-medium text-zinc-900 dark:text-zinc-50">
                {result.decision_maker_context.company_size_tier}
              </p>
            </div>
            <div>
              <p className="text-xs text-zinc-500">Typical Buyer</p>
              <p className="font-medium text-zinc-900 dark:text-zinc-50">
                {result.decision_maker_context.typical_buyer}
              </p>
            </div>
            <div>
              <p className="text-xs text-zinc-500">Primary Pain Point</p>
              <p className="font-medium text-zinc-900 dark:text-zinc-50">
                {result.decision_maker_context.primary_pain_point}
              </p>
            </div>
            <div>
              <p className="text-xs text-zinc-500">What They Google</p>
              <p className="font-medium text-zinc-900 dark:text-zinc-50">
                {result.decision_maker_context.what_they_google}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Raw Data Toggle */}
      {result._raw_data && (
        <details className="rounded-lg border border-zinc-200">
          <summary className="cursor-pointer px-4 py-2 text-sm text-zinc-500 hover:bg-zinc-50">
            API Response Data (for debugging)
          </summary>
          <pre className="whitespace-pre-wrap bg-zinc-50 p-4 text-xs">
            {JSON.stringify(result._raw_data, null, 2)}
          </pre>
        </details>
      )}
    </div>
  );
}