"use client";

import { BuyingSignals as BuyingSignalsType } from "@/types";
import { TrendingUp, DollarSign, Users, Building2, AlertCircle } from "lucide-react";

interface BuyingSignalsProps {
  signals: BuyingSignalsType;
}

export function BuyingSignals({ signals }: BuyingSignalsProps) {
  const signalItems = [
    {
      detected: signals.expansion_detected,
      icon: TrendingUp,
      label: "Expansion",
      detail: signals.expansion_detail,
      color: "text-green-600 dark:text-green-400",
      bgColor: "bg-green-100 dark:bg-green-900",
    },
    {
      detected: signals.funding_detected,
      icon: DollarSign,
      label: "Funding",
      detail: signals.funding_detail,
      color: "text-blue-600 dark:text-blue-400",
      bgColor: "bg-blue-100 dark:bg-blue-900",
    },
    {
      detected: signals.leadership_change,
      icon: Users,
      label: "Leadership Change",
      detail: signals.leadership_detail,
      color: "text-purple-600 dark:text-purple-400",
      bgColor: "bg-purple-100 dark:bg-purple-900",
    },
    {
      detected: signals.portfolio_growth,
      icon: Building2,
      label: "Portfolio Growth",
      detail: signals.portfolio_detail,
      color: "text-orange-600 dark:text-orange-400",
      bgColor: "bg-orange-100 dark:bg-orange-900",
    },
  ];

  const detectedSignals = signalItems.filter((item) => item.detected);

  return (
    <div className="rounded-lg border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex items-center gap-2 border-b border-zinc-200 px-4 py-3 dark:border-zinc-800">
        <AlertCircle className="h-4 w-4 text-indigo-600" />
        <h3 className="text-sm font-medium text-zinc-900 dark:text-zinc-50">
          Buying Signals
        </h3>
        {detectedSignals.length > 0 && (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900 dark:text-green-300">
            {detectedSignals.length} Active
          </span>
        )}
      </div>
      <div className="p-4">
        {detectedSignals.length === 0 ? (
          <div className="flex items-center gap-2 text-sm text-zinc-500">
            <AlertCircle className="h-4 w-4" />
            No active buying signals detected
          </div>
        ) : (
          <ul className="space-y-3">
            {detectedSignals.map((item, index) => (
              <li key={index} className="flex items-start gap-3">
                <div className={`flex h-6 w-6 shrink-0 items-center justify-center rounded ${item.bgColor}`}>
                  <item.icon className={`h-3 w-3 ${item.color}`} />
                </div>
                <div className="flex-1">
                  <span className="text-xs font-medium text-zinc-500">{item.label}</span>
                  <p className="text-sm text-zinc-700 dark:text-zinc-300">
                    {item.detail}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}