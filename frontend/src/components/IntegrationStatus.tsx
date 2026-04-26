"use client";

import { Slack as SlackIcon, Sheet as SheetIcon, Webhook as WebhookIcon } from "lucide-react";

interface StatusPillProps {
  label: string;
  status: "online" | "syncing" | "offline" | "active" | "pending";
  type: "slack" | "sheets" | "webhook";
}

export function StatusPill({ label, status, type }: StatusPillProps) {
  const statusColors = {
    online: "bg-emerald-500/50",
    syncing: "bg-amber-500/50",
    active: "bg-emerald-500/50",
    pending: "bg-zinc-600",
    offline: "bg-zinc-600",
  };

  const textColors = {
    online: "text-zinc-400",
    syncing: "text-zinc-400",
    active: "text-zinc-400",
    pending: "text-zinc-600",
    offline: "text-zinc-600",
  };

  const pulseClass = status === "syncing" ? "animate-pulse" : "";

  const Icon = type === "slack" ? SlackIcon : type === "sheets" ? SheetIcon : WebhookIcon;

  return (
    <div className="flex items-center gap-2">
      <span className={`h-1.5 w-1.5 rounded-full ${statusColors[status]} ${pulseClass}`}></span>
      <Icon className="h-3.5 w-3.5 text-zinc-500" />
      <span className={`text-xs ${textColors[status]}`}>
        {label}: <span className="capitalize font-medium">{status}</span>
      </span>
    </div>
  );
}

interface IntegrationStatusBarProps {
  status: {
    slack: string;
    sheets: string;
    webhook: string;
  };
}

export function IntegrationStatusBar({ status }: IntegrationStatusBarProps) {
  return (
    <div className="flex items-center gap-4">
      <StatusPill label="Slack" status={status.slack as any} type="slack" />
      <StatusPill label="Sheets" status={status.sheets as any} type="sheets" />
      <StatusPill label="Webhook" status={status.webhook as any} type="webhook" />
    </div>
  );
}