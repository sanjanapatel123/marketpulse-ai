"use client";

import { FormEvent, useState } from "react";
import {
  ArrowUpRight,
  Building2,
  LoaderCircle,
  Sparkles,
} from "lucide-react";

import { STOCK_OPTIONS } from "../constants";

interface AnalysisFormProps {
  disabled: boolean;
  submitting: boolean;
  onSubmit: (
    stockSymbol: string,
    question: string,
  ) => Promise<void>;
}

export function AnalysisForm({
  disabled,
  submitting,
  onSubmit,
}: AnalysisFormProps) {
  const [stockSymbol, setStockSymbol] =
    useState("RELIANCE");

  const [question, setQuestion] = useState(
    "Explain the company fundamentals, valuation and major risks.",
  );

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!stockSymbol || !question.trim()) {
      return;
    }

    await onSubmit(stockSymbol, question.trim());
  }

  return (
    <aside className="rounded-[28px] border border-white/[0.08] bg-[#10141f]/80 p-6 shadow-2xl shadow-black/20 backdrop-blur-xl">
      <div className="flex items-center gap-2 text-emerald-300">
        <Sparkles className="h-4 w-4" />
        <span className="text-xs font-medium uppercase tracking-[0.18em]">
          New analysis
        </span>
      </div>

      <h2 className="mt-4 text-2xl font-semibold tracking-tight text-white">
        Research a company
      </h2>

      <p className="mt-2 text-sm leading-6 text-slate-400">
        Stream a deterministic fundamental analysis with
        interruption recovery.
      </p>

      <form
        onSubmit={handleSubmit}
        className="mt-8 space-y-6"
      >
        <div>
          <label
            htmlFor="symbol"
            className="mb-2 block text-xs font-medium uppercase tracking-[0.14em] text-slate-500"
          >
            Listed company
          </label>

          <div className="relative">
            <Building2 className="pointer-events-none absolute left-3.5 top-3.5 h-4 w-4 text-slate-500" />

            <select
              id="symbol"
              value={stockSymbol}
              onChange={(event) =>
                setStockSymbol(event.target.value)
              }
              disabled={disabled}
              className="h-12 w-full appearance-none rounded-xl border border-white/[0.08] bg-[#090c13] pl-11 pr-4 text-sm text-white outline-none transition focus:border-emerald-400/50 disabled:opacity-50"
            >
              {STOCK_OPTIONS.map((stock) => (
                <option
                  key={stock.value}
                  value={stock.value}
                >
                  {stock.value} · {stock.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label
            htmlFor="question"
            className="mb-2 block text-xs font-medium uppercase tracking-[0.14em] text-slate-500"
          >
            Research prompt
          </label>

          <textarea
            id="question"
            rows={7}
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            disabled={disabled}
            className="w-full resize-none rounded-xl border border-white/[0.08] bg-[#090c13] p-4 text-sm leading-6 text-white outline-none transition placeholder:text-slate-600 focus:border-emerald-400/50 disabled:opacity-50"
          />
        </div>

        <button
          type="submit"
          disabled={disabled || submitting}
          className="group flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-emerald-400 to-cyan-400 font-semibold text-slate-950 shadow-lg shadow-emerald-950/40 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {submitting ? (
            <>
              <LoaderCircle className="h-4 w-4 animate-spin" />
              Starting analysis
            </>
          ) : (
            <>
              Generate analysis
              <ArrowUpRight className="h-4 w-4 transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
            </>
          )}
        </button>
      </form>

      <p className="mt-5 text-center text-xs leading-5 text-slate-600">
        Educational protocol demonstration. Not financial
        advice.
      </p>
    </aside>
  );
}