import { Building2, CalendarDays } from "lucide-react";

import type {
  HistoryRange,
  Stock,
} from "../types";

interface StockSelectorProps {
  stocks: Stock[];
  symbol: string;
  range: HistoryRange;
  onSymbolChange: (symbol: string) => void;
  onRangeChange: (range: HistoryRange) => void;
}

const ranges: HistoryRange[] = [30, 60, 90];

export function StockSelector({
  stocks,
  symbol,
  range,
  onSymbolChange,
  onRangeChange,
}: StockSelectorProps) {
  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-white/[0.07] bg-white/[0.035] p-4 md:flex-row md:items-center md:justify-between">
      <div className="relative min-w-[280px]">
        <Building2 className="pointer-events-none absolute left-3 top-3 h-4 w-4 text-slate-500" />

        <select
          value={symbol}
          onChange={(event) =>
            onSymbolChange(event.target.value)
          }
          className="h-10 w-full appearance-none rounded-xl border border-white/[0.08] bg-[#090c13] pl-10 pr-4 text-sm text-white outline-none focus:border-emerald-400/50"
        >
          {stocks.map((stock) => (
            <option
              key={stock.id}
              value={stock.symbol}
            >
              {stock.symbol} · {stock.company_name}
            </option>
          ))}
        </select>
      </div>

      <div className="flex items-center gap-2">
        <CalendarDays className="mr-1 h-4 w-4 text-slate-500" />

        {ranges.map((rangeOption) => (
          <button
            key={rangeOption}
            type="button"
            onClick={() =>
              onRangeChange(rangeOption)
            }
            className={`h-9 rounded-lg px-3 text-xs font-medium transition ${
              range === rangeOption
                ? "bg-emerald-400 text-slate-950"
                : "bg-white/[0.04] text-slate-400 hover:bg-white/[0.08]"
            }`}
          >
            {rangeOption}D
          </button>
        ))}
      </div>
    </div>
  );
}