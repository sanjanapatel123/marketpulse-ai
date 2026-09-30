"use client";

import { type FormEvent, useEffect, useState } from "react";

import type { CreateWatchlistInput } from "../types/watchlist";

import { ModalShell } from "./modal-shell";

interface CreateWatchlistDialogProps {
  isOpen: boolean;
  isSubmitting: boolean;
  onClose: () => void;
  onSubmit: (payload: CreateWatchlistInput) => Promise<unknown>;
}

export function CreateWatchlistDialog({
  isOpen,
  isSubmitting,
  onClose,
  onSubmit,
}: CreateWatchlistDialogProps) {
  const [name, setName] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      setName("");
      setFormError(null);
    }
  }, [isOpen]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedName = name.trim();

    if (trimmedName.length < 2) {
      setFormError("Watchlist name must contain at least 2 characters.");
      return;
    }

    try {
      setFormError(null);

      await onSubmit({
        name: trimmedName,
      });

      onClose();
    } catch (error) {
      setFormError(
        error instanceof Error ? error.message : "Unable to create watchlist",
      );
    }
  }

  return (
    <ModalShell
      isOpen={isOpen}
      title="Create a watchlist"
      description="Build a focused collection of equities for research and price monitoring."
      onClose={onClose}
    >
      <form onSubmit={handleSubmit} className="space-y-5">
        <FormField label="Watchlist name" htmlFor="watchlist-name">
          <input
            id="watchlist-name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="Long-term compounders"
            autoFocus
            maxLength={80}
            className={inputClasses}
          />
        </FormField>

        {formError && <FormError message={formError} />}

        <DialogActions
          submitLabel="Create watchlist"
          isSubmitting={isSubmitting}
          onCancel={onClose}
        />
      </form>
    </ModalShell>
  );
}

interface FormFieldProps {
  label: string;
  htmlFor: string;
  children: React.ReactNode;
}

export function FormField({ label, htmlFor, children }: FormFieldProps) {
  return (
    <div>
      <label
        htmlFor={htmlFor}
        className="mb-2 block text-xs font-semibold uppercase tracking-[0.14em] text-slate-500"
      >
        {label}
      </label>

      {children}
    </div>
  );
}

interface FormErrorProps {
  message: string;
}

export function FormError({ message }: FormErrorProps) {
  return (
    <div className="rounded-xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-200">
      {message}
    </div>
  );
}

interface DialogActionsProps {
  submitLabel: string;
  isSubmitting: boolean;
  onCancel: () => void;
}

export function DialogActions({
  submitLabel,
  isSubmitting,
  onCancel,
}: DialogActionsProps) {
  return (
    <div className="flex justify-end gap-3 pt-2">
      <button
        type="button"
        onClick={onCancel}
        disabled={isSubmitting}
        className="rounded-xl border border-white/10 px-4 py-2.5 text-sm font-medium text-slate-300 transition hover:bg-white/5 disabled:opacity-50"
      >
        Cancel
      </button>

      <button
        type="submit"
        disabled={isSubmitting}
        className="min-w-32 rounded-xl bg-gradient-to-r from-emerald-400 to-cyan-400 px-4 py-2.5 text-sm font-semibold text-slate-950 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isSubmitting ? "Saving..." : submitLabel}
      </button>
    </div>
  );
}

export const inputClasses =
  "h-12 w-full rounded-xl border border-white/10 " +
  "bg-slate-900 px-4 text-sm text-slate-100 outline-none " +
  "placeholder:text-slate-600 transition " +
  "focus:border-emerald-400/60 " +
  "focus:ring-4 focus:ring-emerald-400/10";
