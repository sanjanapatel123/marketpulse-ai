import { PlugZap, RotateCcw, Unplug } from "lucide-react";

import type { ConnectionState } from "../types";

interface StreamControlsProps {
  state: ConnectionState;
  onDisconnect: () => void;
  onReconnect: () => void;
}

export function StreamControls({
  state,
  onDisconnect,
  onReconnect,
}: StreamControlsProps) {
  const canDisconnect = ["connecting", "connected", "reconnecting"].includes(
    state,
  );

  const canReconnect = state === "disconnected";

  return (
    <div className="flex items-center gap-2">
      <button
        type="button"
        onClick={onDisconnect}
        disabled={!canDisconnect}
        className="inline-flex h-10 items-center gap-2 rounded-xl border border-red-400/20 bg-red-400/[0.06] px-3 text-xs font-medium text-red-300 transition hover:bg-red-400/10 disabled:cursor-not-allowed disabled:opacity-30"
      >
        <Unplug className="h-4 w-4" />
        Disconnect
      </button>

      <button
        type="button"
        onClick={onReconnect}
        disabled={!canReconnect}
        className="inline-flex h-10 items-center gap-2 rounded-xl border border-emerald-400/20 bg-emerald-400/[0.06] px-3 text-xs font-medium text-emerald-300 transition hover:bg-emerald-400/10 disabled:cursor-not-allowed disabled:opacity-30"
      >
        {canReconnect ? (
          <RotateCcw className="h-4 w-4" />
        ) : (
          <PlugZap className="h-4 w-4" />
        )}
        Reconnect
      </button>
    </div>
  );
}
