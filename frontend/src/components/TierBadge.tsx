"use client";

import { cva, type VariantProps } from "class-variance-authority";
import { clsx } from "clsx";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors",
  {
    variants: {
      tier: {
        A: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
        B: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
        C: "bg-zinc-100 text-zinc-800 dark:bg-zinc-800 dark:text-zinc-200",
        default: "bg-zinc-100 text-zinc-800",
      },
    },
    defaultVariants: {
      tier: "default",
    },
  }
);

interface TierBadgeProps extends VariantProps<typeof badgeVariants> {
  tier: "A" | "B" | "C" | null;
  showLabel?: boolean;
}

export function TierBadge({ tier, showLabel = true }: TierBadgeProps) {
  if (!tier) return null;

  const labels = {
    A: "Priority",
    B: "Follow Up",
    C: "Nurture",
  };

  return (
    <span className={clsx(badgeVariants({ tier }))}>
      {showLabel ? `Tier ${tier} — ${labels[tier]}` : `Tier ${tier}`}
    </span>
  );
}