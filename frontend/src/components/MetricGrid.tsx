"use client";

import { KeyDataPoints } from "@/types";
import { Users, Home, TrendingUp, DollarSign } from "lucide-react";

interface MetricGridProps {
  dataPoints: KeyDataPoints;
}

export function MetricGrid({ dataPoints }: MetricGridProps) {
  const metrics = [
    {
      label: "Renter %",
      value: dataPoints.renter_pct != null ? `${dataPoints.renter_pct}%` : "—",
      icon: Users,
      color: "text-blue-600",
    },
    {
      label: "Vacancy Rate",
      value: dataPoints.vacancy_rate != null ? `${dataPoints.vacancy_rate}%` : "—",
      icon: Home,
      color: "text-orange-600",
    },
    {
      label: "Rent Growth YoY",
      value: dataPoints.rent_growth_pct != null ? `${dataPoints.rent_growth_pct}%` : "—",
      icon: TrendingUp,
      color: "text-green-600",
    },
    {
      label: "Median Income",
      value: dataPoints.median_income != null ? `$${(dataPoints.median_income / 1000).toFixed(0)}k` : "—",
      icon: DollarSign,
      color: "text-purple-600",
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
      {metrics.map((metric) => (
        <div
          key={metric.label}
          className="rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900"
        >
          <div className="mb-2 flex items-center gap-2">
            <metric.icon className={`h-4 w-4 ${metric.color}`} />
            <span className="text-xs font-medium text-zinc-500">
              {metric.label}
            </span>
          </div>
          <p className="text-2xl font-bold text-zinc-900 dark:text-zinc-50">
            {metric.value}
          </p>
        </div>
      ))}
    </div>
  );
}