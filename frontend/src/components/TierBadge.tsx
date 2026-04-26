"use client";

import { cva, type VariantProps } from "class-variance-authority";
import { clsx } from "clsx";

const badgeVariants = cva(
  "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      tier: {
        A: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
        B: "bg-amber-500/10 text-amber-400 border-amber-500/20",
        C: "bg-zinc-500/10 text-zinc-400 border-zinc-500/20",
        NEEDS_REVIEW: "bg-red-500/10 text-red-400 border-red-500/20",
        default: "bg-zinc-500/10 text-zinc-400 border-zinc-500/20",
      },
    },
    defaultVariants: {
      tier: "default",
    },
  }
);

interface TierBadgeProps extends VariantProps<typeof badgeVariants> {
  tier: "A" | "B" | "C" | "NEEDS_REVIEW" | null;
  showLabel?: boolean;
  small?: boolean;
}

export function TierBadge({ tier, showLabel = true, small = false }: TierBadgeProps) {
  if (!tier) return null;

  const labels: Record<string, string> = {
    A: "Priority",
    B: "Follow Up",
    C: "Nurture",
    NEEDS_REVIEW: "Review",
  };

  if (small) {
    return (
      <span className={clsx(badgeVariants({ tier }), "px-2 py-0.5 text-[10px]")}>
        {tier === "NEEDS_REVIEW" ? "Review" : tier}
      </span>
    );
  }

  return (
    <span className={clsx(badgeVariants({ tier }))}>
      {showLabel ? `${tier === "NEEDS_REVIEW" ? "Review" : `Tier ${tier}`} — ${labels[tier] || ""}` : tier === "NEEDS_REVIEW" ? "Review" : `Tier ${tier}`}
    </span>
  );
}