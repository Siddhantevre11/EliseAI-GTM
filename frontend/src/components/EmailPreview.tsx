"use client";

import { useState } from "react";
import { EmailDraft } from "@/types";
import { Copy, Edit2, Check, X } from "lucide-react";

interface EmailPreviewProps {
  email: EmailDraft | string;
  onSave?: (email: EmailDraft) => void;
}

export function EmailPreview({ email, onSave }: EmailPreviewProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedEmail, setEditedEmail] = useState<EmailDraft>(() => {
    if (typeof email === "string") {
      return { subject: "", body: email };
    }
    return email;
  });
  const [copied, setCopied] = useState(false);

  // Defensive: handle null email_draft
  const safeEmailObj: EmailDraft = (email && typeof email === "object" && email.body) 
    ? email 
    : { subject: "", body: typeof email === "string" ? email : "" };
  
  const currentEmail = isEditing ? editedEmail : safeEmailObj;

  const bodyText = currentEmail?.body || "";

  const handleCopy = async () => {
    const text = `Subject: ${currentEmail.subject}\n\n${bodyText}`;
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSave = () => {
    if (onSave) {
      onSave(editedEmail);
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedEmail(safeEmailObj);
    setIsEditing(false);
  };

  return (
    <div className="rounded-lg border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex items-center justify-between border-b border-zinc-200 px-4 py-3 dark:border-zinc-800">
        <h3 className="text-sm font-medium text-zinc-900 dark:text-zinc-50">
          Email Draft
        </h3>
        <div className="flex items-center gap-2">
          {isEditing ? (
            <>
              <button
                onClick={handleCancel}
                className="flex h-8 w-8 items-center justify-center rounded-md text-zinc-500 hover:bg-zinc-100 dark:hover:bg-zinc-800"
              >
                <X className="h-4 w-4" />
              </button>
              <button
                onClick={handleSave}
                className="flex h-8 w-8 items-center justify-center rounded-md bg-green-600 text-white hover:bg-green-700"
              >
                <Check className="h-4 w-4" />
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => setIsEditing(true)}
                className="flex h-8 w-8 items-center justify-center rounded-md text-zinc-500 hover:bg-zinc-100 dark:hover:bg-zinc-800"
                title="Edit email"
              >
                <Edit2 className="h-4 w-4" />
              </button>
              <button
                onClick={handleCopy}
                className="flex items-center gap-1.5 rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700"
              >
                {copied ? (
                  <>
                    <Check className="h-4 w-4" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="h-4 w-4" />
                    Copy
                  </>
                )}
              </button>
            </>
          )}
        </div>
      </div>

      <div className="p-4">
        {isEditing ? (
          <div className="space-y-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-zinc-500">
                Subject Line
              </label>
              <input
                type="text"
                value={editedEmail.subject}
                onChange={(e) => setEditedEmail({ ...editedEmail, subject: e.target.value })}
                className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-800"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-zinc-500">
                Email Body
              </label>
              <textarea
                value={editedEmail.body}
                onChange={(e) => setEditedEmail({ ...editedEmail, body: e.target.value })}
                rows={8}
                className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-800"
              />
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {currentEmail.subject && (
              <div>
                <span className="text-xs font-medium text-zinc-500">Subject: </span>
                <span className="text-sm text-zinc-900 dark:text-zinc-50">
                  {currentEmail.subject}
                </span>
              </div>
            )}
            <pre className="whitespace-pre-wrap text-sm text-zinc-600 dark:text-zinc-400 font-sans">
              {bodyText}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}