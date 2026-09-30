"use client";

import { type FormEvent, useEffect, useState } from "react";

import type {
  CreatePriceAlertInput,
  PriceAlertCondition,
  WatchlistItemQuote,
} from "../types/watchlist";

import {
  DialogActions,
  FormError,
  FormField,
  inputClasses,
} from "./create-watchlist-dialog";

import { ModalShell } from "./modal-shell";
import { formatCurrency } from "../utils/watchlist-formatters";

interface CreateAlertDialogProps {
  isOpen: boolean;
  selectedItem: WatchlistItemQuote | null;
  isSubmitting: boolean;
  onClose: () => void;
  onSubmit: (payload: CreatePriceAlertInput) => Promise<unknown>;
}

export function CreateAlertDialog({
  isOpen,
  selectedItem,
  isSubmitting,
  onClose,
  onSubmit,
}: CreateAlertDialogProps) {
  const [condition, setCondition] =
    useState<PriceAlertCondition>("PRICE_ABOVE");

  const [threshold, setThreshold] = useState("");

  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    setCondition("PRICE_ABOVE");
    setThreshold(selectedItem?.price ?? "");
    setFormError(null);
  }, [isOpen, selectedItem]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!selectedItem) {
      setFormError("No equity selected.");
      return;
    }

    const thresholdNumber = Number(threshold);

    if (!Number.isFinite(thresholdNumber) || thresholdNumber <= 0) {
      setFormError("Threshold must be greater than zero.");
      return;
    }

    try {
      setFormError(null);

      await onSubmit({
        symbol: selectedItem.item.symbol,
        exchange: selectedItem.item.exchange,
        condition,
        threshold: thresholdNumber.toFixed(2),
      });

      onClose();
    } catch (error) {
      setFormError(
        error instanceof Error ? error.message : "Unable to create price alert",
      );
    }
  }

  return (
    <ModalShell
      isOpen={isOpen}
      title="Create price alert"
      description={
        selectedItem
          ? `Configure an automatic threshold for ${selectedItem.item.symbol}.`
          : undefined
      }
      onClose={onClose}
    >
      <form onSubmit={handleSubmit} className="space-y-5">
        {selectedItem && (
          <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-slate-900/70 p-4">
            <div>
              <p className="font-semibold text-white">
                {selectedItem.item.symbol}
              </p>

              <p className="mt-1 text-xs text-slate-500">
                {selectedItem.company_name}
              </p>
            </div>

            <div className="text-right">
              <p className="text-xs text-slate-500">Current price</p>

              <p className="mt-1 font-mono font-semibold text-emerald-300">
                {formatCurrency(selectedItem.price, selectedItem.currency)}
              </p>
            </div>
          </div>
        )}

        <FormField label="Trigger condition" htmlFor="alert-condition">
          <select
            id="alert-condition"
            value={condition}
            onChange={(event) =>
              setCondition(event.target.value as PriceAlertCondition)
            }
            className={inputClasses}
          >
            <option value="PRICE_ABOVE">Price moves above</option>

            <option value="PRICE_BELOW">Price moves below</option>
          </select>
        </FormField>

        <FormField label="Threshold price" htmlFor="alert-threshold">
          <div className="relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-sm text-slate-500">
              ₹
            </span>

            <input
              id="alert-threshold"
              type="number"
              min="0.01"
              step="0.01"
              value={threshold}
              onChange={(event) => setThreshold(event.target.value)}
              className={`${inputClasses} pl-9`}
            />
          </div>
        </FormField>

        <div className="rounded-xl border border-amber-400/15 bg-amber-400/5 px-4 py-3">
          <p className="text-xs leading-5 text-amber-100/70">
            Active alerts are evaluated automatically by the backend monitoring
            worker.
          </p>
        </div>

        {formError && <FormError message={formError} />}

        <DialogActions
          submitLabel="Create alert"
          isSubmitting={isSubmitting}
          onCancel={onClose}
        />
      </form>
    </ModalShell>
  );
}
