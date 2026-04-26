"use client";

import { useState, useEffect } from "react";

interface ToastProps {
  message: string;
  type?: "success" | "error" | "syncing" | "info";
  onClose?: () => void;
}

export function Toast({ message, type = "info", onClose }: ToastProps) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    if (type === "syncing") {
      const timer = setTimeout(() => setVisible(false), 2000);
      return () => clearTimeout(timer);
    } else {
      const timer = setTimeout(() => {
        setVisible(false);
        onClose?.();
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [type, onClose]);

  if (!visible) return null;

  const bgColors = {
    success: "bg-green-600",
    error: "bg-red-600",
    syncing: "bg-indigo-600",
    info: "bg-zinc-700",
  };

  return (
    <div className={`fixed bottom-4 right-4 z-50 ${bgColors[type]} px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 text-white text-sm animate-slide-up`}>
      {type === "syncing" && (
        <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
      )}
      {type === "success" && <CheckCircle className="h-4 w-4" />}
      {type === "error" && <XCircle className="h-4 w-4" />}
      <span>{message}</span>
    </div>
  );
}

function CheckCircle({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

function XCircle({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}