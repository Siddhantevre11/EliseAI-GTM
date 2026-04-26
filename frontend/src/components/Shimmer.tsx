"use client";

import { useState, useEffect, useRef } from "react";

interface ShimmerProps {
  rows?: number;
  cols?: number;
}

export function LoadingShimmer({ rows = 5, cols = 6 }: ShimmerProps) {
  return (
    <div className="w-full overflow-hidden rounded-lg border border-zinc-200 dark:border-zinc-800">
      <div className="grid divide-x divide-y divide-zinc-200 dark:divide-zinc-800" style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
        {Array.from({ length: rows * cols }).map((_, i) => (
          <div key={i} className="shimmer-cell h-10 px-4 py-2" />
        ))}
      </div>
    </div>
  );
}

export function ShimmerLine({ width = "100%", height = "1rem" }: { width?: string; height?: string }) {
  return <div className="shimmer-cell rounded" style={{ width, height }} />;
}

export function ShimmerCard() {
  return (
    <div className="rounded-xl border border-zinc-200 p-4 dark:border-zinc-800 dark:bg-zinc-900">
      <div className="mb-4 flex items-center gap-3">
        <div className="shimmer-cell h-10 w-10 rounded-lg" />
        <div className="flex-1 space-y-2">
          <div className="shimmer-cell h-4 w-3/4 rounded" />
          <div className="shimmer-cell h-3 w-1/2 rounded" />
        </div>
      </div>
      <div className="space-y-2">
        <div className="shimmer-cell h-3 w-full rounded" />
        <div className="shimmer-cell h-3 w-5/6 rounded" />
        <div className="shimmer-cell h-3 w-4/6 rounded" />
      </div>
    </div>
  );
}