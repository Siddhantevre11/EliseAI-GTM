"use client";

import { useState } from "react";
import { ROIEstimate } from "@/types";
import { Calculator, DollarSign, Clock, TrendingUp, TrendingDown } from "lucide-react";

interface ROICalculatorProps {
  roi: ROIEstimate;
  editable?: boolean;
  onUpdate?: (roi: ROIEstimate) => void;
}

export function ROICalculator({ roi, editable = false, onUpdate }: ROICalculatorProps) {
  const [localUnits, setLocalUnits] = useState(roi.prospect_units);

  const calculateROI = (units: number) => {
    const inquiries = Math.round(units / 10);
    const timeSaved = Math.round((inquiries * 5) / 60);
    const savings = timeSaved * 25;
    const cost = units;
    const net = savings - cost;

    return {
      prospect_units: units,
      inquiries_per_month_est: inquiries,
      avg_inquiry_handling_min: 5,
      time_saved_hours_month: timeSaved,
      staff_cost_per_hour: 25,
      monthly_savings: savings,
      eliseai_cost_monthly: cost,
      net_monthly_roi: net,
      annual_savings: net * 12,
    };
  };

  const displayROI = editable ? calculateROI(localUnits) : roi;

  return (
    <div className="rounded-lg border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex items-center gap-2 border-b border-zinc-200 px-4 py-3 dark:border-zinc-800">
        <Calculator className="h-4 w-4 text-indigo-600" />
        <h3 className="text-sm font-medium text-zinc-900 dark:text-zinc-50">
          ROI Estimate
        </h3>
      </div>
      <div className="p-4">
        {editable && (
          <div className="mb-4">
            <label className="mb-1 block text-xs font-medium text-zinc-500">
              Prospect Unit Count
            </label>
            <div className="flex items-center gap-2">
              <input
                type="number"
                value={localUnits}
                onChange={(e) => setLocalUnits(Number(e.target.value))}
                className="w-32 rounded-md border border-zinc-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-800"
              />
              <span className="text-sm text-zinc-500">units</span>
            </div>
          </div>
        )}

        <div className="mb-4 grid grid-cols-2 gap-3">
          <div className="rounded-lg bg-zinc-50 p-3 dark:bg-zinc-800">
            <div className="flex items-center gap-1 text-xs text-zinc-500">
              <Clock className="h-3 w-3" />
              Time Saved/Month
            </div>
            <p className="text-xl font-bold text-zinc-900 dark:text-zinc-50">
              {displayROI.time_saved_hours_month}h
            </p>
          </div>

          <div className="rounded-lg bg-zinc-50 p-3 dark:bg-zinc-800">
            <div className="flex items-center gap-1 text-xs text-zinc-500">
              <DollarSign className="h-3 w-3" />
              Monthly Savings
            </div>
            <p className="text-xl font-bold text-zinc-900 dark:text-zinc-50">
              ${displayROI.monthly_savings.toLocaleString()}
            </p>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-zinc-500">Inquiries/month (est.)</span>
            <span className="text-zinc-700 dark:text-zinc-300">{displayROI.inquiries_per_month_est}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-zinc-500">Staff cost (@ $25/hr)</span>
            <span className="text-zinc-700 dark:text-zinc-300">${displayROI.staff_cost_per_hour}/hr</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-zinc-500">EliseAI cost</span>
            <span className="text-zinc-700 dark:text-zinc-300">${displayROI.eliseai_cost_monthly.toLocaleString()}/mo</span>
          </div>
          <div className="border-t border-zinc-200 pt-2 dark:border-zinc-700">
            <div className="flex justify-between text-sm">
              <span className="text-zinc-500">Net ROI/month</span>
              <span className={`font-medium ${displayROI.net_monthly_roi >= 0 ? "text-green-600" : "text-red-600"}`}>
                {displayROI.net_monthly_roi >= 0 ? "+" : ""}${displayROI.net_monthly_roi.toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-zinc-500">Annual savings</span>
              <span className={`font-medium ${displayROI.annual_savings >= 0 ? "text-green-600" : "text-red-600"}`}>
                {displayROI.annual_savings >= 0 ? "+" : ""}${displayROI.annual_savings.toLocaleString()}
              </span>
            </div>
          </div>
        </div>

        {displayROI.net_monthly_roi >= 0 ? (
          <div className="mt-4 flex items-center gap-2 rounded-lg bg-green-50 p-3 dark:bg-green-900/30">
            <TrendingUp className="h-4 w-4 text-green-600" />
            <p className="text-sm text-green-800 dark:text-green-200">
              Positive ROI — EliseAI pays for itself
            </p>
          </div>
        ) : (
          <div className="mt-4 flex items-center gap-2 rounded-lg bg-amber-50 p-3 dark:bg-amber-900/30">
            <TrendingDown className="h-4 w-4 text-amber-600" />
            <p className="text-sm text-amber-800 dark:text-amber-200">
              Scale-dependent ROI — consider larger portfolio or higher inquiry volume
            </p>
          </div>
        )}
      </div>
    </div>
  );
}