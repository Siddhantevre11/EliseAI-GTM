"use client";

import { useState } from "react";
import { Slack, Sheet, Webhook, CheckCircle2, XCircle, Settings, Key, Bell } from "lucide-react";

export function IntegrationsPage() {
  const [slackEnabled, setSlackEnabled] = useState(true);
  const [sheetsEnabled, setSheetsEnabled] = useState(true);
  const [webhookEnabled, setWebhookEnabled] = useState(false);

  return (
    <div className="rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
      <div className="border-b border-zinc-200 px-6 py-4 dark:border-zinc-800">
        <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
          Integrations Configuration
        </h2>
        <p className="mt-1 text-sm text-zinc-500">
          Configure external services for lead routing and notifications
        </p>
      </div>

      <div className="divide-y divide-zinc-200 dark:divide-zinc-800">
        {/* Slack Integration */}
        <div className="flex items-center justify-between px-6 py-5">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-purple-100 dark:bg-purple-900/30">
              <Slack className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <h3 className="font-medium text-zinc-900 dark:text-zinc-100">Slack</h3>
              <p className="text-sm text-zinc-500">
                Send tier A leads and alerts to your team channel
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-green-500"></div>
              <span className="text-sm text-green-600">Connected</span>
            </div>
            <button className="rounded-lg border border-zinc-300 px-3 py-1.5 text-sm font-medium text-zinc-700 hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800">
              Configure
            </button>
          </div>
        </div>

        {/* Google Sheets Integration */}
        <div className="flex items-center justify-between px-6 py-5">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-green-100 dark:bg-green-900/30">
              <Sheet className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <h3 className="font-medium text-zinc-900 dark:text-zinc-100">Google Sheets</h3>
              <p className="text-sm text-zinc-500">
                Export enriched leads to your spreadsheet
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-green-500"></div>
              <span className="text-sm text-green-600">Connected</span>
            </div>
            <button className="rounded-lg border border-zinc-300 px-3 py-1.5 text-sm font-medium text-zinc-700 hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800">
              Configure
            </button>
          </div>
        </div>

        {/* Webhook Integration */}
        <div className="flex items-center justify-between px-6 py-5">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-zinc-100 dark:bg-zinc-800">
              <Webhook className="h-6 w-6 text-zinc-600" />
            </div>
            <div>
              <h3 className="font-medium text-zinc-900 dark:text-zinc-100">Webhook</h3>
              <p className="text-sm text-zinc-500">
                POST enriched lead data to external systems
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-zinc-400"></div>
              <span className="text-sm text-zinc-500">Not configured</span>
            </div>
            <button className="rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700">
              Set Up
            </button>
          </div>
        </div>
      </div>

      <div className="border-t border-zinc-200 px-6 py-5 dark:border-zinc-800">
        <h3 className="mb-4 font-medium text-zinc-900 dark:text-zinc-100">
          API Configuration
        </h3>
        <div className="grid gap-4 lg:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
              Census API Key
            </label>
            <input
              type="password"
              placeholder="Enter API key..."
              className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-50"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
              FRED API Key
            </label>
            <input
              type="password"
              placeholder="Enter API key..."
              className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-50"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
              News API Key
            </label>
            <input
              type="password"
              placeholder="Enter API key..."
              className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-50"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
              LLM Model
            </label>
            <select className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-50">
              <option>llama-3.1-8b-instant</option>
              <option>llama-3.1-70b-versatile</option>
              <option>gpt-4o-mini</option>
            </select>
          </div>
        </div>
        <button className="mt-4 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700">
          Save Configuration
        </button>
      </div>
    </div>
  );
}