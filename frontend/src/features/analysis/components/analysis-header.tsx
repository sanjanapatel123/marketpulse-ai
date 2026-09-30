import { Activity, ChartNoAxesCombined, ShieldCheck } from "lucide-react";

export function AnalysisHeader() {
  return (
    <header className="border-b border-white/[0.06] bg-[#080b12]/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-[1440px] items-center justify-between px-5 py-4 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-emerald-400/20 bg-emerald-400/10">
            <ChartNoAxesCombined className="h-5 w-5 text-emerald-300" />
          </div>

          <div>
            <h1 className="font-semibold text-white">MarketPulse</h1>

            <p className="text-xs text-slate-500">
              Resumable market intelligence
            </p>
          </div>
        </div>

        <div className="hidden items-center gap-6 text-xs text-slate-400 md:flex">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-emerald-400" />
            Durable SSE
          </div>

          <div className="flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-cyan-400" />
            Deterministic analysis
          </div>
        </div>
      </div>
    </header>
  );
}
