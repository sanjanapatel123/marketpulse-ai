import {
  formatCurrency,
  formatPercent,
} from "../../../features/market/market-utils";

import type { PositionValuation } from "../types";

interface PositionsTableProps {
  positions: PositionValuation[];
}

export function PositionsTable({
  positions,
}: PositionsTableProps) {
  return (
    <section className="overflow-hidden rounded-[28px] border border-white/[0.08] bg-[#10141f]/85">
      <div className="border-b border-white/[0.06] p-6">
        <h2 className="font-semibold text-white">
          Open positions
        </h2>

        <p className="mt-1 text-sm text-slate-500">
          Current holdings and unrealized performance
        </p>
      </div>

      {positions.length === 0 ? (
        <p className="p-8 text-center text-sm text-slate-500">
          No open positions.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[850px]">
            <thead className="bg-black/20 text-left text-xs uppercase tracking-wider text-slate-500">
              <tr>
                <th className="px-6 py-4">Symbol</th>
                <th className="px-6 py-4">Quantity</th>
                <th className="px-6 py-4">Avg. cost</th>
                <th className="px-6 py-4">Price</th>
                <th className="px-6 py-4">Market value</th>
                <th className="px-6 py-4">Unrealized P&L</th>
              </tr>
            </thead>

            <tbody>
              {positions.map((position) => {
                const positive =
                  Number(position.unrealized_pnl) >= 0;

                return (
                  <tr
                    key={position.symbol}
                    className="border-t border-white/[0.05] text-sm"
                  >
                    <td className="px-6 py-5">
                      <p className="font-semibold text-white">
                        {position.symbol}
                      </p>
                      <p className="text-xs text-slate-500">
                        {position.exchange}
                      </p>
                    </td>

                    <td className="px-6 py-5 text-slate-300">
                      {position.quantity}
                    </td>

                    <td className="px-6 py-5 text-slate-300">
                      {formatCurrency(
                        position.average_cost,
                      )}
                    </td>

                    <td className="px-6 py-5 text-slate-300">
                      {formatCurrency(
                        position.current_price,
                      )}
                    </td>

                    <td className="px-6 py-5 text-slate-300">
                      {formatCurrency(
                        position.market_value,
                      )}
                    </td>

                    <td
                      className={`px-6 py-5 font-medium ${
                        positive
                          ? "text-emerald-300"
                          : "text-red-300"
                      }`}
                    >
                      {formatCurrency(
                        position.unrealized_pnl,
                      )}

                      <span className="ml-2 text-xs">
                        (
                        {formatPercent(
                          position.unrealized_return_percent,
                        )}
                        )
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}