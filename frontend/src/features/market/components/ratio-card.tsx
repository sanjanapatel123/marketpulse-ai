import type { LucideIcon } from "lucide-react";

interface RatioCardProps {
  title: string;
  value: string;
  description: string;
  icon: LucideIcon;
  accent?: "emerald" | "cyan" | "amber" | "purple";
}

const accentStyles = {
  emerald: "bg-emerald-400/10 text-emerald-300",
  cyan: "bg-cyan-400/10 text-cyan-300",
  amber: "bg-amber-400/10 text-amber-300",
  purple: "bg-purple-400/10 text-purple-300",
};

export function RatioCard({
  title,
  value,
  description,
  icon: Icon,
  accent = "emerald",
}: RatioCardProps) {
  return (
    <article className="rounded-2xl border border-white/[0.07] bg-black/20 p-5 transition hover:border-white/[0.12] hover:bg-white/[0.035]">
      <div className="flex items-start justify-between gap-4">
        <div
          className={`flex h-10 w-10 items-center justify-center rounded-xl ${accentStyles[accent]}`}
        >
          <Icon className="h-5 w-5" />
        </div>

        <span className="text-2xl font-semibold tracking-tight text-white">
          {value}
        </span>
      </div>

      <h4 className="mt-5 text-sm font-medium text-slate-200">{title}</h4>

      <p className="mt-2 text-xs leading-5 text-slate-500">{description}</p>
    </article>
  );
}
