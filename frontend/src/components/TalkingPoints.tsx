"use client";

import { TrendingUp, Building2, Clock } from "lucide-react";

interface TalkingPointsProps {
  points: string[];
}

export function TalkingPoints({ points }: TalkingPointsProps) {
  if (!points || points.length === 0) return null;

  const icons = [Building2, TrendingUp, Clock];

  return (
    <div className="rounded-lg border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
      <div className="border-b border-zinc-200 px-4 py-3 dark:border-zinc-800">
        <h3 className="text-sm font-medium text-zinc-900 dark:text-zinc-50">
          SDR Talking Points
        </h3>
      </div>
      <div className="p-4">
        <ul className="space-y-4">
          {points.map((point, index) => (
            <li key={index} className="flex gap-3">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-indigo-100 dark:bg-indigo-900">
                <span className="text-sm font-bold text-indigo-600 dark:text-indigo-400">
                  {index + 1}
                </span>
              </div>
              <div className="flex-1 pt-1">
                <p className="text-sm text-zinc-700 dark:text-zinc-300">
                  {point}
                </p>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}