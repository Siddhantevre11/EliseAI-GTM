"use client";

import { EnrichmentResult, Lead } from "@/types";

interface LeadListItemProps {
  result: EnrichmentResult;
  isSelected: boolean;
  onClick: () => void;
}

export function LeadListItem({ result, isSelected, onClick }: LeadListItemProps) {
  const lead = result._lead as Lead || {} as Lead;
  const kdp = result.key_data_points || {};
  const tier = result.tier || "C";

  const tierColors = {
    A: "bg-green-500 text-white",
    B: "bg-yellow-500 text-white",
    C: "bg-zinc-400 text-white",
  };

  const tierBgColors = {
    A: "bg-green-50 dark:bg-green-950/30",
    B: "bg-yellow-50 dark:bg-yellow-950/30",
    C: "bg-zinc-50 dark:bg-zinc-950/30",
  };

  return (
    <button
      onClick={onClick}
      className={`w-full text-left p-3 transition-all ${
        isSelected
          ? "bg-indigo-50 border-l-2 border-indigo-500 dark:bg-indigo-950/30"
          : "hover:bg-zinc-50 border-l-2 border-transparent dark:hover:bg-zinc-800/50"
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className={`shrink-0 rounded px-1.5 py-0.5 text-[10px] font-bold ${tierColors[tier as keyof typeof tierColors]}`}>
              {tier}
            </span>
            <span className="truncate text-sm font-medium text-zinc-900 dark:text-zinc-100">
              {lead.company || "Unknown Company"}
            </span>
          </div>
          <p className="mt-1 truncate text-xs text-zinc-500">
            {lead.city}, {lead.state}
          </p>
        </div>
        <div className="ml-2 shrink-0 text-right">
          <span className={`text-sm font-bold ${tier === 'A' ? 'text-green-600' : tier === 'B' ? 'text-yellow-600' : 'text-zinc-400'}`}>
            {result.priority_score}
          </span>
        </div>
      </div>

      <div className={`mt-2 flex flex-wrap gap-2 rounded p-2 ${tierBgColors[tier as keyof typeof tierBgColors]}`}>
        <StatBadge
          label="Renter"
          value={kdp.renter_pct != null ? `${kdp.renter_pct}%` : "—"}
        />
        <StatBadge
          label="Rent Gr"
          value={kdp.rent_growth_pct != null ? `${kdp.rent_growth_pct > 0 ? '+' : ''}${kdp.rent_growth_pct}%` : "—"}
          highlight={kdp.rent_growth_pct != null && kdp.rent_growth_pct > 0}
        />
        <StatBadge
          label="Vacancy"
          value={kdp.vacancy_rate != null ? `${kdp.vacancy_rate}%` : "—"}
          warning={kdp.vacancy_rate != null && kdp.vacancy_rate > 5}
        />
      </div>
    </button>
  );
}

function StatBadge({ label, value, highlight, warning }: { label: string; value: string; highlight?: boolean; warning?: boolean }) {
  return (
    <span className={`text-[10px] ${highlight ? 'text-green-600' : warning ? 'text-amber-600' : 'text-zinc-500'}`}>
      <span className="font-medium">{label}:</span>{" "}
      <span className={highlight ? 'text-green-700 font-semibold' : ''}>{value}</span>
    </span>
  );
}