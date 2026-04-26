"use client";

import { useState } from "react";
import { EnrichmentResult, Lead } from "@/types";
import { ChevronDown, ChevronRight, Check, X } from "lucide-react";

interface ClayGridProps {
  results: EnrichmentResult[];
  selectedResult: EnrichmentResult | null;
  onSelectResult: (result: EnrichmentResult) => void;
  onUpdateLead: (index: number, updates: Partial<EnrichmentResult>) => void;
}

export function ClayGrid({
  results,
  selectedResult,
  onSelectResult,
  onUpdateLead,
}: ClayGridProps) {
  const [editingCell, setEditingCell] = useState<{ index: number; field: string } | null>(null);
  const [editValue, setEditValue] = useState("");

  const handleDoubleClick = (index: number, field: string, value: string) => {
    setEditingCell({ index, field });
    setEditValue(value);
  };

  const handleSaveEdit = (index: number) => {
    if (!editingCell) return;

    const globalIndex = results.findIndex(
      (r) => results[index]?._lead?.company === r._lead?.company
    );

    if (globalIndex !== -1) {
      onUpdateLead(globalIndex, { _lead: { ...results[globalIndex]._lead, [editingCell.field]: editValue } } as any);
    }

    setEditingCell(null);
    setEditValue("");
  };

  const handleCancelEdit = () => {
    setEditingCell(null);
    setEditValue("");
  };

  const handleTierChange = (index: number, newTier: string) => {
    const globalIndex = results.findIndex(
      (r) => results[index]?._lead?.company === r._lead?.company
    );

    if (globalIndex !== -1) {
      onUpdateLead(globalIndex, { tier: newTier as any });
    }
  };

  if (results.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center text-sm text-zinc-500">
        No leads match the current filter
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-auto rounded-lg border border-zinc-800">
      <table className="w-full text-xs">
        <thead className="sticky top-0 bg-zinc-900 text-xs font-medium uppercase tracking-wide text-zinc-500">
          <tr>
            <th className="w-8 px-4 py-3 text-left"></th>
            <th className="px-4 py-3 text-left">Company</th>
            <th className="px-4 py-3 text-center">Tier</th>
            <th className="px-4 py-3 text-left">Market</th>
            <th className="px-4 py-3 text-right">Renter %</th>
            <th className="px-4 py-3 text-right">Rent Growth</th>
            <th className="px-4 py-3 text-right">Vacancy</th>
            <th className="px-4 py-3 text-center">Slack</th>
            <th className="px-4 py-3 text-center">Sheets</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-zinc-800 bg-zinc-950">
          {results.map((result, index) => {
            const lead = result._lead as Lead || ({} as Lead);
            const kdp = result.key_data_points || {};
            const isSelected = selectedResult?._lead?.company === lead.company;
            const isEditing = editingCell?.index === index;

            return (
              <tr
                key={index}
                onClick={() => onSelectResult(result)}
                className={`cursor-pointer transition-colors ${
                  isSelected
                    ? "bg-indigo-950/30"
                    : "hover:bg-zinc-900/50"
                }`}
              >
                <td className="px-4 py-2 text-zinc-500">
                  {isSelected ? (
                    <ChevronDown className="h-4 w-4" />
                  ) : (
                    <ChevronRight className="h-4 w-4" />
                  )}
                </td>

                <td
                  className="px-4 py-2"
                  onDoubleClick={(e) => {
                    e.stopPropagation();
                    handleDoubleClick(index, "company", lead.company || "");
                  }}
                >
                  {isEditing && editingCell?.field === "company" ? (
                    <InlineEdit
                      value={editValue}
                      onChange={setEditValue}
                      onSave={() => handleSaveEdit(index)}
                      onCancel={handleCancelEdit}
                    />
                  ) : (
                    <span className="font-medium text-zinc-100">
                      {lead.company || "Unknown"}
                    </span>
                  )}
                </td>

                <td className="px-4 py-2 text-center">
                  <TierDropdown
                    tier={(result.tier as string) || "C"}
                    onChange={(tier) => handleTierChange(index, tier)}
                  />
                </td>

                <td
                  className="px-4 py-2"
                  onDoubleClick={(e) => {
                    e.stopPropagation();
                    handleDoubleClick(index, "city", `${lead.city}, ${lead.state}`);
                  }}
                >
                  {isEditing && editingCell?.field === "city" ? (
                    <InlineEdit
                      value={editValue}
                      onChange={setEditValue}
                      onSave={() => handleSaveEdit(index)}
                      onCancel={handleCancelEdit}
                    />
                  ) : (
                    <span className="text-zinc-400">
                      {lead.city}, {lead.state}
                    </span>
                  )}
                </td>

                <td className="px-4 py-2 text-right font-mono text-zinc-400">
                  {kdp.renter_pct != null ? `${kdp.renter_pct}%` : "—"}
                </td>

                <td className="px-4 py-2 text-right font-mono text-zinc-400">
                  {kdp.rent_growth_pct != null ? (
                    <span>
                      {kdp.rent_growth_pct > 0 ? "+" : ""}{kdp.rent_growth_pct}%
                    </span>
                  ) : "—"}
                </td>

                <td className="px-4 py-2 text-right font-mono text-zinc-400">
                  {kdp.vacancy_rate != null ? `${kdp.vacancy_rate}%` : "—"}
                </td>

                <td className="px-4 py-2 text-center">
                  <IntegrationIcon type="slack" status="success" />
                </td>

                <td className="px-4 py-2 text-center">
                  <IntegrationIcon type="sheets" status="success" />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function InlineEdit({
  value,
  onChange,
  onSave,
  onCancel,
}: {
  value: string;
  onChange: (v: string) => void;
  onSave: () => void;
  onCancel: () => void;
}) {
  return (
    <div className="flex items-center gap-1">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") onSave();
          if (e.key === "Escape") onCancel();
        }}
        className="w-full rounded border border-indigo-500 bg-zinc-900 px-2 py-1 text-sm text-zinc-100"
        autoFocus
      />
      <button onClick={onSave} className="rounded p-1 text-emerald-400 hover:bg-zinc-800">
        <Check className="h-4 w-4" />
      </button>
      <button onClick={onCancel} className="rounded p-1 text-red-400 hover:bg-zinc-800">
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}

function TierDropdown({
  tier,
  onChange,
}: {
  tier: string;
  onChange: (tier: string) => void;
}) {
  const [isOpen, setIsOpen] = useState(false);

  const getTierBadge = (t: string) => {
    const styles: Record<string, { bg: string; text: string; label: string }> = {
      A: { bg: "bg-emerald-500/10 border-emerald-500/20", text: "text-emerald-400", label: "Tier A" },
      B: { bg: "bg-amber-500/10 border-amber-500/20", text: "text-amber-400", label: "Tier B" },
      C: { bg: "bg-zinc-500/10 border-zinc-500/20", text: "text-zinc-400", label: "Tier C" },
      NEEDS_REVIEW: { bg: "bg-zinc-500/10 border-zinc-500/20", text: "text-zinc-400", label: "Needs Review" },
    };
    return styles[t] || styles.C;
  };

  const badge = getTierBadge(tier);

  return (
    <div className="relative inline-flex">
      <button
        onClick={(e) => {
          e.stopPropagation();
          setIsOpen(!isOpen);
        }}
        className={`inline-flex items-center gap-1 rounded-md border px-2.5 py-0.5 text-xs font-medium ${badge.bg} ${badge.text}`}
      >
        {badge.label}
        <ChevronDown className="h-3 w-3" />
      </button>

      {isOpen && (
        <div className="absolute left-1/2 top-full z-10 mt-1 -translate-x-1/2 overflow-hidden rounded-lg border border-zinc-800 bg-zinc-900 shadow-lg">
          {["A", "B", "C", "NEEDS_REVIEW"].map((t) => {
            const optBadge = getTierBadge(t);
            return (
              <button
                key={t}
                onClick={(e) => {
                  e.stopPropagation();
                  onChange(t);
                  setIsOpen(false);
                }}
                className={`block w-full px-4 py-2 text-left text-xs transition-colors hover:bg-zinc-800 ${
                  tier === t ? `font-semibold ${optBadge.text}` : "text-zinc-400"
                }`}
              >
                {t === "NEEDS_REVIEW" ? "Needs Review" : `Tier ${t}`}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

function IntegrationIcon({ type, status }: { type: "slack" | "sheets"; status: "pending" | "sending" | "success" }) {
  return (
    <div className="flex items-center justify-center text-zinc-500">
      {type === "slack" ? (
        <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
          <path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zM6.313 15.165a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313zM8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zM8.834 6.313a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312zM18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zM17.688 8.834a2.528 2.528 0 0 1-2.523 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.165 0a2.528 2.528 0 0 1 2.523 2.522v6.312zM15.165 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.165 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52zM15.165 17.688a2.527 2.527 0 0 1-2.52-2.523 2.526 2.526 0 0 1 2.52-2.52h6.313A2.527 2.527 0 0 1 24 15.165a2.528 2.528 0 0 1-2.522 2.523h-6.313z"/>
        </svg>
      ) : (
        <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
          <path d="M3 3h12v12H3V3zm2 2v8h8V5H5zm1 1.5h5.5v.5H6v-.5zM6 14v-3h8v3H6z"/>
        </svg>
      )}
    </div>
  );
}