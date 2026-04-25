"use client";

import { IndustryBenchmark as IndustryBenchmarkType } from "@/types";
import { BarChart2, Clock, TrendingUp, AlertCircle } from "lucide-react";

interface IndustryBenchmarkProps {
  benchmark: IndustryBenchmarkType;
}

export function IndustryBenchmark({ benchmark }: IndustryBenchmarkProps) {
  const metrics = [
    {
      label: "Response Time",
      prospect: benchmark.prospect_response_time,
      industry: benchmark.avg_response_time_hours,
      format: (v: number) => `${v.toFixed(1)}h`,
      lowerIsBetter: true,
    },
    {
      label: "Vacancy Rate",
      prospect: benchmark.prospect_market_vacancy,
      industry: benchmark.avg_vacancy_rate,
      format: (v: number) => `${v.toFixed(1)}%`,
      lowerIsBetter: false,
    },
    {
      label: "Rent Growth",
      prospect: benchmark.prospect_market_rent_growth,
      industry: benchmark.avg_rent_growth,
      format: (v: number) => `${v.toFixed(2)}%`,
      lowerIsBetter: false,
    },
  ];

  const getComparison = (prospect: number, industry: number, lowerIsBetter: boolean) => {
    if (!prospect) return null;
    const diff = prospect - industry;
    const pctDiff = ((diff / industry) * 100).toFixed(0);

    if (Math.abs(diff) < 0.5) return { label: "On par", color: "text-zinc-500" };
    if (lowerIsBetter) {
      if (diff < 0) {
        return { label: `${Math.abs(Number(pctDiff))}% better`, color: "text-green-600" };
      }
      return { label: `${pctDiff}% slower`, color: "text-amber-600" };
    }
    if (diff > 0) {
      return { label: `${pctDiff}% higher`, color: "text-green-600" };
    }
    return { label: `${Math.abs(Number(pctDiff))}% lower`, color: "text-amber-600" };
  };

  return (
    <div className="rounded-lg border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex items-center gap-2 border-b border-zinc-200 px-4 py-3 dark:border-zinc-800">
        <BarChart2 className="h-4 w-4 text-indigo-600" />
        <h3 className="text-sm font-medium text-zinc-900 dark:text-zinc-50">
          Industry Benchmarks
        </h3>
      </div>
      <div className="p-4">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-xs text-zinc-500">
              <th className="pb-2 text-left font-medium">Metric</th>
              <th className="pb-2 text-right font-medium">Prospect</th>
              <th className="pb-2 text-right font-medium">Industry</th>
              <th className="pb-2 text-right font-medium">vs Avg</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
            {metrics.map((metric) => {
              const comparison = getComparison(
                metric.prospect || 0,
                metric.industry,
                metric.lowerIsBetter
              );

              return (
                <tr key={metric.label}>
                  <td className="py-2 text-zinc-600 dark:text-zinc-400">
                    {metric.label}
                  </td>
                  <td className="py-2 text-right font-medium text-zinc-900 dark:text-zinc-50">
                    {metric.prospect ? metric.format(metric.prospect) : "N/A"}
                  </td>
                  <td className="py-2 text-right text-zinc-500">
                    {metric.format(metric.industry)}
                  </td>
                  <td className="py-2 text-right">
                    {comparison ? (
                      <span className={comparison.color}>
                        {comparison.label}
                      </span>
                    ) : (
                      <span className="text-zinc-400">—</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        <div className="mt-4 rounded-lg bg-indigo-50 p-3 dark:bg-indigo-900/30">
          <div className="flex items-start gap-2">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-indigo-600" />
            <p className="text-xs text-indigo-800 dark:text-indigo-200">
              Use these comparisons to show prospects how their market performs
              vs industry averages. Higher rent growth and lower vacancy are
              selling points for faster leasing.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}