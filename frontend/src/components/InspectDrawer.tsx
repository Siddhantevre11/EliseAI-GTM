"use client";

import { useState } from "react";
import { X, FileJson, Layout } from "lucide-react";

interface InspectDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  rawData: Record<string, unknown>;
  company?: string;
  city?: string;
}

export function InspectDrawer({ isOpen, onClose, rawData, company, city }: InspectDrawerProps) {
  const [view, setView] = useState<"formatted" | "raw">("formatted");

  if (!isOpen) return null;

  const census = (rawData?.census as Record<string, string | number | null>) || {};
  const fred = (rawData?.fred as Record<string, string | number | null>) || {};
  const news = (rawData?.news as Record<string, unknown>) || {};
  const headlines = (news.company_headlines as Array<{title?: string; source?: string; date?: string}>) || [];

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative w-full max-w-lg overflow-auto bg-white dark:bg-zinc-900 shadow-xl">
        <div className="sticky top-0 border-b border-zinc-200 bg-white px-4 py-3 dark:border-zinc-800 dark:bg-zinc-900">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-semibold text-zinc-900 dark:text-zinc-50">
                API Inspector
              </h2>
              <p className="text-sm text-zinc-500">
                {company} - {city}
              </p>
            </div>
            <button
              onClick={onClose}
              className="rounded-lg p-2 text-zinc-500 hover:bg-zinc-100 dark:hover:bg-zinc-800"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <div className="mt-3 flex gap-2">
            <button
              onClick={() => setView("formatted")}
              className={`flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                view === "formatted"
                  ? "bg-indigo-600 text-white"
                  : "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300"
              }`}
            >
              <Layout className="h-4 w-4" />
              Formatted
            </button>
            <button
              onClick={() => setView("raw")}
              className={`flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                view === "raw"
                  ? "bg-indigo-600 text-white"
                  : "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300"
              }`}
            >
              <FileJson className="h-4 w-4" />
              Raw JSON
            </button>
          </div>
        </div>

        <div className="p-4">
          {view === "formatted" ? (
            <div className="space-y-4">
              <Section title="Census Data" icon="📊">
                <Field label="County" value={census.county_name} />
                <Field label="Renter %" value={census.renter_pct ? `${census.renter_pct}%` : null} />
                <Field label="Vacancy Rate" value={census.vacancy_rate ? `${census.vacancy_rate}%` : null} />
                <Field label="Median Income" value={census.median_income ? `$${census.median_income.toLocaleString()}` : null} />
                <Field label="Total Renter Units" value={census.total_renter_units?.toLocaleString()} />
                <Field label="Owner %" value={census.owner_pct ? `${census.owner_pct}%` : null} />
                {census.error && <ErrorMessage error={census.error as string} />}
              </Section>

              <Section title="FRED Data" icon="📈">
                <Field label="State" value={fred.state} />
                <Field label="Rent Growth YoY" value={fred.rent_growth_pct ? `${fred.rent_growth_pct}%` : null} />
                <Field label="Series Used" value={fred.series_used} />
                {fred.error && <ErrorMessage error={fred.error as string} />}
              </Section>

              <Section title="News Data" icon="📰">
                <Field label="Company Summary" value={news.company_summary as string} multiline />
                <div className="mt-2">
                  <p className="text-xs font-medium text-zinc-500">Headlines</p>
                  {(news.company_headlines as Array<{title?: string; source?: string; date?: string}>)?.map((h, i) => (
                    <div key={i} className="mt-1 rounded bg-zinc-50 p-2 text-sm dark:bg-zinc-800">
                      <p className="font-medium">{h.title}</p>
                      <p className="text-xs text-zinc-500">{h.source} - {h.date}</p>
                    </div>
                  ))}
                </div>
                {news.error ? <ErrorMessage error={String(news.error)} /> : null}
              </Section>
            </div>
          ) : (
            <pre className="whitespace-pre-wrap rounded-lg bg-zinc-900 p-4 text-xs text-zinc-300">
              {JSON.stringify(rawData, null, 2)}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}

function Section({ title, icon, children }: { title: string; icon: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-zinc-200 dark:border-zinc-700">
      <div className="flex items-center gap-2 border-b border-zinc-200 bg-zinc-50 px-4 py-2 dark:border-zinc-700 dark:bg-zinc-800">
        <span>{icon}</span>
        <h3 className="font-medium text-zinc-900 dark:text-zinc-100">{title}</h3>
      </div>
      <div className="space-y-2 p-4">{children}</div>
    </div>
  );
}

function Field({ label, value, multiline }: { label: string; value?: string | number | null; multiline?: boolean }) {
  if (value === null || value === undefined) {
    return (
      <div className="flex justify-between text-sm">
        <span className="text-zinc-500">{label}</span>
        <span className="text-zinc-400">N/A</span>
      </div>
    );
  }

  if (multiline) {
    return (
      <div>
        <p className="text-sm text-zinc-500">{label}</p>
        <p className="mt-1 text-sm text-zinc-700 dark:text-zinc-300">{value}</p>
      </div>
    );
  }

  return (
    <div className="flex justify-between text-sm">
      <span className="text-zinc-500">{label}</span>
      <span className="font-medium text-zinc-900 dark:text-zinc-100">{value}</span>
    </div>
  );
}

function ErrorMessage({ error }: { error: string }) {
  return (
    <div className="mt-2 rounded bg-red-50 p-2 text-sm text-red-700 dark:bg-red-900/30 dark:text-red-400">
      Error: {error}
    </div>
  );
}