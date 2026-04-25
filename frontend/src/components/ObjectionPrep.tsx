"use client";

import { useState } from "react";
import { ObjectionHandling } from "@/types";
import { MessageSquare, ChevronDown, ChevronUp } from "lucide-react";

interface ObjectionPrepProps {
  objections: ObjectionHandling;
  company?: string;
}

export function ObjectionPrep({ objections, company }: ObjectionPrepProps) {
  const [expanded, setExpanded] = useState<string | null>(null);

  const objectionItems = [
    {
      key: "has_yardi",
      label: "We already use Yardi/Entrata",
      icon: "🏢",
      response: objections.has_yardi,
    },
    {
      key: "too_expensive",
      label: "Too expensive",
      icon: "💰",
      response: objections.too_expensive,
    },
    {
      key: "have_team",
      label: "We have a team for this",
      icon: "👥",
      response: objections.have_team,
    },
    {
      key: "not_priority",
      label: "Not a priority right now",
      icon: "⏰",
      response: objections.not_priority,
    },
    {
      key: "current_solution",
      label: "We have another solution",
      icon: "🔄",
      response: objections.current_solution,
    },
  ].filter((item) => item.response);

  if (objectionItems.length === 0) return null;

  const handleCopy = async (response: string) => {
    await navigator.clipboard.writeText(response);
  };

  return (
    <div className="rounded-lg border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex items-center gap-2 border-b border-zinc-200 px-4 py-3 dark:border-zinc-800">
        <MessageSquare className="h-4 w-4 text-indigo-600" />
        <h3 className="text-sm font-medium text-zinc-900 dark:text-zinc-50">
          Objection Handling
        </h3>
        <span className="ml-auto text-xs text-zinc-500">
          {objectionItems.length} prepared
        </span>
      </div>
      <div className="p-2">
        {objectionItems.map((item) => (
          <div key={item.key} className="border-b border-zinc-100 last:border-0 dark:border-zinc-800">
            <button
              onClick={() => setExpanded(expanded === item.key ? null : item.key)}
              className="flex w-full items-center justify-between px-2 py-3 text-left hover:bg-zinc-50 dark:hover:bg-zinc-800"
            >
              <div className="flex items-center gap-2">
                <span>{item.icon}</span>
                <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                  {item.label}
                </span>
              </div>
              {expanded === item.key ? (
                <ChevronUp className="h-4 w-4 text-zinc-400" />
              ) : (
                <ChevronDown className="h-4 w-4 text-zinc-400" />
              )}
            </button>
            {expanded === item.key && (
              <div className="px-2 pb-3">
                <p className="rounded-md bg-indigo-50 p-3 text-sm text-indigo-900 dark:bg-indigo-900 dark:text-indigo-100">
                  {item.response}
                </p>
                <button
                  onClick={() => handleCopy(item.response || "")}
                  className="mt-2 text-xs text-indigo-600 hover:text-indigo-700"
                >
                  Copy response
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}