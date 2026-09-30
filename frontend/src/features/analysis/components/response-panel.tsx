import { Activity, FileText, Hash, Radio, TriangleAlert } from "lucide-react";

import { MetricCard } from "../../../components/ui/metric-card";
import { StatusBadge } from "../../../components/ui/status-badge";

import type { ConnectionState } from "../types";
import { StreamControls } from "./stream-controls";

interface ResponsePanelProps {
  runId: string | null;
  state: ConnectionState;
  responseText: string;
  cursor: number;
  eventCount: number;
  error: string | null;
  onDisconnect: () => void;
  onReconnect: () => void;
}

export function ResponsePanel({
  runId,
  state,
  responseText,
  cursor,
  eventCount,
  error,
  onDisconnect,
  onReconnect,
}: ResponsePanelProps) {
  return (
    <section className="min-w-0 rounded-[28px] border border-white/[0.08] bg-[#10141f]/80 shadow-2xl shadow-black/20 backdrop-blur-xl">
      <div className="flex flex-col gap-5 border-b border-white/[0.06] p-6 xl:flex-row xl:items-center xl:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-400/10">
              <Radio className="h-5 w-5 text-cyan-300" />
            </div>

            <div>
              <h2 className="font-semibold text-white">
                Live intelligence stream
              </h2>

              <p className="mt-1 max-w-[420px] truncate text-xs text-slate-500">
                {runId ? `Run ${runId}` : "Waiting for an analysis run"}
              </p>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <StatusBadge state={state} />

          <StreamControls
            state={state}
            onDisconnect={onDisconnect}
            onReconnect={onReconnect}
          />
        </div>
      </div>

      <div className="grid gap-3 p-6 sm:grid-cols-3">
        <MetricCard label="Cursor" value={cursor} icon={Hash} />

        <MetricCard label="Events" value={eventCount} icon={Activity} />

        <MetricCard label="Transport" value="SSE" icon={Radio} />
      </div>

      {error && (
        <div className="mx-6 flex gap-3 rounded-xl border border-red-400/20 bg-red-400/[0.06] p-4 text-sm text-red-200">
          <TriangleAlert className="mt-0.5 h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      <div className="p-6">
        <div className="relative min-h-[430px] overflow-hidden rounded-2xl border border-white/[0.06] bg-[#080b12]">
          <div className="flex items-center justify-between border-b border-white/[0.06] px-5 py-4">
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <FileText className="h-4 w-4" />
              Analysis output
            </div>

            {state === "connected" && (
              <div className="flex items-center gap-2 text-xs text-emerald-300">
                <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
                Receiving
              </div>
            )}
          </div>

          <article className="p-6 text-[15px] leading-8 text-slate-300">
            {responseText ? (
              <>
                {responseText}

                {state === "connected" && (
                  <span className="ml-1 inline-block h-5 w-1.5 animate-pulse rounded-full bg-emerald-400 align-middle" />
                )}
              </>
            ) : (
              <div className="flex min-h-[300px] flex-col items-center justify-center text-center">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-white/[0.06] bg-white/[0.03]">
                  <Activity className="h-6 w-6 text-slate-600" />
                </div>

                <p className="mt-4 font-medium text-slate-400">
                  No active analysis
                </p>

                <p className="mt-2 max-w-sm text-sm leading-6 text-slate-600">
                  Select a company and start an analysis to see durable events
                  stream in real time.
                </p>
              </div>
            )}
          </article>
        </div>
      </div>
    </section>
  );
}
