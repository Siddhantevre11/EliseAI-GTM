"use client";

import { useState } from "react";
import { PeerCaseStudy } from "@/types";
import { Users, TrendingDown, Target } from "lucide-react";

interface CaseStudyProps {
  caseStudy: PeerCaseStudy;
}

export function CaseStudy({ caseStudy }: CaseStudyProps) {
  if (!caseStudy.similar_company) return null;

  return (
    <div className="rounded-lg border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex items-center gap-2 border-b border-zinc-200 px-4 py-3 dark:border-zinc-800">
        <Users className="h-4 w-4 text-indigo-600" />
        <h3 className="text-sm font-medium text-zinc-900 dark:text-zinc-50">
          Peer Case Study
        </h3>
      </div>
      <div className="p-4">
        <div className="mb-3 flex items-center justify-between">
          <span className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
            {caseStudy.similar_company}
          </span>
          <span className="rounded-full bg-indigo-100 px-2 py-1 text-xs font-medium text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300">
            {caseStudy.company_size}
          </span>
        </div>

        <div className="mb-3 rounded-lg bg-zinc-50 p-3 dark:bg-zinc-800">
          <p className="text-xs font-medium text-zinc-500">Market</p>
          <p className="text-sm text-zinc-700 dark:text-zinc-300">{caseStudy.market}</p>
        </div>

        <div className="mb-3">
          <p className="text-xs font-medium text-zinc-500">Challenge</p>
          <p className="text-sm text-zinc-700 dark:text-zinc-300">{caseStudy.challenge}</p>
        </div>

        <div className="rounded-lg bg-green-50 p-3 dark:bg-green-900/30">
          <div className="mb-1 flex items-center gap-1">
            <Target className="h-3 w-3 text-green-600" />
            <span className="text-xs font-medium text-green-700 dark:text-green-400">
              Result
            </span>
          </div>
          <p className="text-sm font-medium text-green-800 dark:text-green-200">
            {caseStudy.result}
          </p>
        </div>
      </div>
    </div>
  );
}