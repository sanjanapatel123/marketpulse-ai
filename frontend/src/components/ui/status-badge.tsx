import { Circle } from "lucide-react";

import type { ConnectionState } from "../../features/analysis/types";

interface StatusBadgeProps {
  state: ConnectionState;
}

const stateStyles: Record<ConnectionState, string> = {
  idle: "border-white/10 bg-white/5 text-slate-400",
  connecting: "border-amber-400/20 bg-amber-400/10 text-amber-300",
  connected: "border-emerald-400/20 bg-emerald-400/10 text-emerald-300",
  reconnecting: "border-orange-400/20 bg-orange-400/10 text-orange-300",
  disconnected: "border-slate-400/20 bg-slate-400/10 text-slate-300",
  completed: "border-cyan-400/20 bg-cyan-400/10 text-cyan-300",
  failed: "border-red-400/20 bg-red-400/10 text-red-300",
  interrupted: "border-purple-400/20 bg-purple-400/10 text-purple-300",
};

export function StatusBadge({ state }: StatusBadgeProps) {
  const isActive =
    state === "connected" || state === "connecting" || state === "reconnecting";

  return (
    <div
      className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-medium capitalize ${stateStyles[state]}`}
    >
      <Circle
        className={`h-2.5 w-2.5 fill-current ${
          isActive ? "animate-pulse" : ""
        }`}
      />

      {state}
    </div>
  );
}
