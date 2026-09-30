import { TriangleAlert } from "lucide-react";

interface MarketErrorProps {
  message: string;
  onRetry: () => void;
}

export function MarketError({
  message,
  onRetry,
}: MarketErrorProps) {
  return (
    <div className="rounded-2xl border border-red-400/20 bg-red-400/[0.06] p-5">
      <div className="flex gap-3 text-red-200">
        <TriangleAlert className="h-5 w-5 shrink-0" />

        <div>
          <p className="font-medium">
            Market data unavailable
          </p>

          <p className="mt-1 text-sm text-red-300/70">
            {message}
          </p>

          <button
            type="button"
            onClick={onRetry}
            className="mt-4 rounded-lg border border-red-300/20 px-3 py-2 text-xs font-medium hover:bg-red-300/10"
          >
            Try again
          </button>
        </div>
      </div>
    </div>
  );
}