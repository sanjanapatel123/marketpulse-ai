import { BriefcaseBusiness } from "lucide-react";

import type { Portfolio } from "../types";

interface PortfolioSelectorProps {
  portfolios: Portfolio[];
  selectedId: string | null;
  onChange: (portfolioId: string) => void;
}

export function PortfolioSelector({
  portfolios,
  selectedId,
  onChange,
}: PortfolioSelectorProps) {
  return (
    <div className="relative min-w-[260px]">
      <BriefcaseBusiness className="pointer-events-none absolute left-3 top-3 h-4 w-4 text-slate-500" />

      <select
        value={selectedId ?? ""}
        onChange={(event) => onChange(event.target.value)}
        className="h-10 w-full appearance-none rounded-xl border border-white/[0.08] bg-[#090c13] pl-10 pr-4 text-sm text-white outline-none focus:border-emerald-400/50"
      >
        {portfolios.map((portfolio) => (
          <option key={portfolio.id} value={portfolio.id}>
            {portfolio.name}
          </option>
        ))}
      </select>
    </div>
  );
}
