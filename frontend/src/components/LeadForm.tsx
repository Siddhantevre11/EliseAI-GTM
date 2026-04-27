"use client";

import { useState } from "react";
import { Lead } from "@/types";
import { Loader2, Send, User, Building2, MapPin, Mail, Home } from "lucide-react";

interface LeadFormProps {
  onSubmit: (lead: Lead) => void;
  isProcessing: boolean;
}

export function LeadForm({ onSubmit, isProcessing }: LeadFormProps) {
  const [formData, setFormData] = useState<Partial<Lead>>({
    name: "",
    email: "",
    company: "",
    property_address: "",
    city: "",
    state: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData as Lead);
  };

  const handleChange = (field: keyof Lead, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const inputClass = "w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-zinc-100 placeholder:text-zinc-500 focus:border-indigo-500 focus:outline-none";
  const labelClass = "mb-1 block text-xs font-medium text-zinc-400";

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="flex items-center gap-2 text-sm font-medium text-zinc-300">
        <User className="h-4 w-4 text-indigo-400" />
        Single Lead Entry
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="col-span-2">
          <label className={labelClass}>
            <span className="flex items-center gap-1">
              <User className="h-3 w-3" />
              Contact Name
              <span className="text-zinc-600">(optional)</span>
            </span>
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => handleChange("name", e.target.value)}
            className={inputClass}
            placeholder="Sarah Chen, John Smith, etc."
          />
        </div>

        <div>
          <label className={labelClass}>
            <span className="flex items-center gap-1">
              <Building2 className="h-3 w-3" />
              Company
            </span>
          </label>
          <input
            type="text"
            value={formData.company}
            onChange={(e) => handleChange("company", e.target.value)}
            className={inputClass}
            placeholder="Greystar"
            required
          />
        </div>

        <div>
          <label className={labelClass}>
            <span className="flex items-center gap-1">
              <Mail className="h-3 w-3" />
              Email
            </span>
          </label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => handleChange("email", e.target.value)}
            className={inputClass}
            placeholder="contact@company.com"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelClass}>
            <span className="flex items-center gap-1">
              <MapPin className="h-3 w-3" />
              City
            </span>
          </label>
          <input
            type="text"
            value={formData.city}
            onChange={(e) => handleChange("city", e.target.value)}
            className={inputClass}
            placeholder="Austin"
            required
          />
        </div>

        <div>
          <label className={labelClass}>State</label>
          <input
            type="text"
            value={formData.state}
            onChange={(e) => handleChange("state", e.target.value.toUpperCase())}
            className={inputClass}
            placeholder="TX"
            maxLength={2}
            required
          />
        </div>
      </div>

      <div>
        <label className={labelClass}>
          <span className="flex items-center gap-1">
            <Home className="h-3 w-3" />
            Property Address (optional)
          </span>
        </label>
        <input
          type="text"
          value={formData.property_address}
          onChange={(e) => handleChange("property_address", e.target.value)}
          className={inputClass}
          placeholder="123 Main St, Austin, TX"
        />
      </div>

      <button
        type="submit"
        disabled={isProcessing || !formData.company || !formData.city || !formData.state}
        className="flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:opacity-50"
      >
        {isProcessing ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Processing...
          </>
        ) : (
          <>
            <Send className="h-4 w-4" />
            Enrich Lead
          </>
        )}
      </button>
    </form>
  );
}