"use client";

import { FormEvent, useState } from "react";
import { ArrowDownToLine, ArrowUpFromLine, LoaderCircle } from "lucide-react";

import type { TradeInput, TransactionSide } from "../types";

interface TradeTicketProps {
  submitting: boolean;
  onSubmit: (input: TradeInput) => Promise<void>;
}

const symbols = ["RELIANCE", "TCS", "INFY"];

export function TradeTicket({ submitting, onSubmit }: TradeTicketProps) {
  const [symbol, setSymbol] = useState("TCS");
  const [side, setSide] = useState<TransactionSide>("BUY");
  const [quantity, setQuantity] = useState("1");

  const [pendingKey, setPendingKey] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const idempotencyKey = pendingKey ?? crypto.randomUUID();

    setPendingKey(idempotencyKey);

    try {
      await onSubmit({
        idempotency_key: idempotencyKey,
        symbol,
        side,
        quantity,
      });

      setPendingKey(null);
    } catch {
      // Keep the same key so retry cannot duplicate trade.
    }
  }

  function changeTradeInput() {
    setPendingKey(null);
  }

  return (
    <section className="rounded-[28px] border border-white/[0.08] bg-[#10141f]/85 p-6">
      <h2 className="font-semibold text-white">Paper trade</h2>

      <p className="mt-1 text-sm text-slate-500">
        Execute using the simulated market quote.
      </p>

      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        <div className="grid grid-cols-2 gap-2 rounded-xl bg-black/20 p-1">
          {(["BUY", "SELL"] as const).map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => {
                setSide(option);
                changeTradeInput();
              }}
              className={`flex h-10 items-center justify-center gap-2 rounded-lg text-sm font-semibold transition ${
                side === option
                  ? option === "BUY"
                    ? "bg-emerald-400 text-slate-950"
                    : "bg-red-400 text-slate-950"
                  : "text-slate-500"
              }`}
            >
              {option === "BUY" ? (
                <ArrowDownToLine className="h-4 w-4" />
              ) : (
                <ArrowUpFromLine className="h-4 w-4" />
              )}

              {option}
            </button>
          ))}
        </div>

        <select
          value={symbol}
          onChange={(event) => {
            setSymbol(event.target.value);
            changeTradeInput();
          }}
          className="h-11 w-full rounded-xl border border-white/[0.08] bg-[#090c13] px-3 text-sm text-white outline-none"
        >
          {symbols.map((stockSymbol) => (
            <option key={stockSymbol} value={stockSymbol}>
              {stockSymbol}
            </option>
          ))}
        </select>

        <input
          type="number"
          min="0.0001"
          step="0.0001"
          value={quantity}
          onChange={(event) => {
            setQuantity(event.target.value);
            changeTradeInput();
          }}
          className="h-11 w-full rounded-xl border border-white/[0.08] bg-[#090c13] px-3 text-sm text-white outline-none"
          placeholder="Quantity"
        />

        <button
          type="submit"
          disabled={submitting || Number(quantity) <= 0}
          className={`flex h-11 w-full items-center justify-center gap-2 rounded-xl font-semibold text-slate-950 transition disabled:opacity-50 ${
            side === "BUY" ? "bg-emerald-400" : "bg-red-400"
          }`}
        >
          {submitting && <LoaderCircle className="h-4 w-4 animate-spin" />}

          {submitting ? "Executing..." : `${side} ${symbol}`}
        </button>
      </form>
    </section>
  );
}
