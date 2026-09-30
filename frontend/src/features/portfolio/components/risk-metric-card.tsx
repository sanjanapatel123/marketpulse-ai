import type { LucideIcon } from "lucide-react";

interface RiskMetricCardProps {
  label: string;
  value: string;
  description: string;
  icon: LucideIcon;
  tone?: "neutral" | "positive" | "warning" | "negative";
}

const toneStyles = {
  neutral: "border-white/[0.07] bg-black/20 text-slate-200",
  positive: "border-emerald-400/15 bg-emerald-400/[0.05] text-emerald-300",
  warning: "border-amber-400/15 bg-amber-400/[0.05] text-amber-300",
  negative: "border-red-400/15 bg-red-400/[0.05] text-red-300",
};

export function RiskMetricCard({
  label,
  value,
  description,
  icon: Icon,
  tone = "neutral",
}: RiskMetricCardProps) {
  return (
    <article className={`rounded-2xl border p-5 ${toneStyles[tone]}`}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/[0.05]">
          <Icon className="h-5 w-5" />
        </div>

        <p className="text-2xl font-semibold tracking-tight">{value}</p>
      </div>

      <h3 className="mt-5 text-sm font-medium text-slate-200">{label}</h3>

      <p className="mt-2 text-xs leading-5 text-slate-500">{description}</p>
    </article>
  );
}
