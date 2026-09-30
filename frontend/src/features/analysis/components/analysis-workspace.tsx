"use client";

import { useState } from "react";

import { createAnalysis } from "../api/create-analysis";
import { useRunStream } from "../hooks/use-run-stream";
import { AnalysisForm } from "./analysis-form";
import { AnalysisHeader } from "./analysis-header";
import { ResponsePanel } from "./response-panel";

export function AnalysisWorkspace() {
  const [submitting, setSubmitting] = useState(false);
  const [requestError, setRequestError] = useState<
    string | null
  >(null);

  const [runId, setRunId] = useState<string | null>(
    null,
  );

  const [conversationId, setConversationId] = useState<
    string | null
  >(null);

  const {
    connectionState,
    responseText,
    events,
    cursor,
    error: streamError,
    startStream,
    disconnect,
    reconnect,
  } = useRunStream();

  async function handleSubmit(
    stockSymbol: string,
    question: string,
  ) {
    setSubmitting(true);
    setRequestError(null);

    try {
      const analysis = await createAnalysis({
        conversation_id: conversationId,
        message_id: crypto.randomUUID(),
        stock_symbol: stockSymbol,
        question,
      });

      setConversationId(analysis.conversation_id);
      setRunId(analysis.run_id);

      startStream(analysis.run_id);
    } catch (error) {
      setRequestError(
        error instanceof Error
          ? error.message
          : "Unable to start analysis",
      );
    } finally {
      setSubmitting(false);
    }
  }

  const streamActive = [
    "connecting",
    "connected",
    "reconnecting",
  ].includes(connectionState);

  return (
    <div className="min-h-screen bg-[#080b12] text-white">
      <AnalysisHeader />

      <main className="relative overflow-hidden px-5 py-8 lg:px-8">
        <div className="pointer-events-none absolute left-1/4 top-0 h-[420px] w-[420px] rounded-full bg-emerald-500/[0.07] blur-[130px]" />
        <div className="pointer-events-none absolute right-0 top-1/3 h-[380px] w-[380px] rounded-full bg-cyan-500/[0.06] blur-[130px]" />

        <div className="relative mx-auto grid max-w-[1440px] gap-6 lg:grid-cols-[370px_minmax(0,1fr)]">
          <div>
            <AnalysisForm
              submitting={submitting}
              disabled={streamActive}
              onSubmit={handleSubmit}
            />

            {requestError && (
              <p className="mt-4 rounded-xl border border-red-400/20 bg-red-400/[0.06] p-4 text-sm text-red-300">
                {requestError}
              </p>
            )}
          </div>

          <ResponsePanel
            runId={runId}
            state={connectionState}
            responseText={responseText}
            cursor={cursor}
            eventCount={events.length}
            error={streamError}
            onDisconnect={disconnect}
            onReconnect={reconnect}
          />
        </div>
      </main>
    </div>
  );
}