"use client";

import { Zap, Copy } from "lucide-react";

interface SalesSignalProps {
  signal: string;
  priorityScore?: number;
}

export function SalesSignal({ signal, priorityScore }: SalesSignalProps) {
  const handleCopy = async () => {
    await navigator.clipboard.writeText(signal);
  };

  return (
    <div className="rounded-lg border border-zinc-200 bg-zinc-900 dark:border-zinc-700 dark:bg-zinc-950">
      <div className="flex items-center justify-between border-b border-zinc-700 px-4 py-2">
        <div className="flex items-center gap-2">
          <Zap className="h-3 w-3 text-yellow-500" />
          <span className="text-xs font-medium text-zinc-400">SALES SIGNAL</span>
        </div>
        <div className="flex items-center gap-2">
          {priorityScore !== undefined && (
            <span className="rounded-full bg-yellow-500/20 px-2 py-0.5 text-xs font-bold text-yellow-500">
              {priorityScore}
            </span>
          )}
          <button
            onClick={handleCopy}
            className="flex h-6 w-6 items-center justify-center rounded text-zinc-500 hover:text-zinc-300"
          >
            <Copy className="h-3 w-3" />
          </button>
        </div>
      </div>
      <div className="px-4 py-3">
        <p className="font-mono text-sm text-zinc-300">{signal}</p>
      </div>
    </div>
  );
}