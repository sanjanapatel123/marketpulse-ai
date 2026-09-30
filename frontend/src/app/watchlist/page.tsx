import type { Metadata } from "next";

import { WatchlistWorkspace } from "../../features/watchlist/components/watchlist-workspace";

export const metadata: Metadata = {
  title: "Smart Watchlists | MarketPulse AI",
  description: "Monitor equities and automatically evaluate price alerts.",
};

export default function WatchlistPage() {
  return <WatchlistWorkspace />;
}
