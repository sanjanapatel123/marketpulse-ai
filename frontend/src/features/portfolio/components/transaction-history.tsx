import {
  ArrowDownToLine,
  ArrowUpFromLine,
  History,
} from "lucide-react";

import {
  formatCurrency,
  formatDateTime,
} from "../../../features/market/market-utils";

import type { PortfolioTransaction } from "../types";

interface TransactionHistoryProps {
  transactions: PortfolioTransaction[];
}

export function TransactionHistory({
  transactions,
}: TransactionHistoryProps) {
  return (
    <section className="overflow-hidden rounded-[28px] border border-white/[0.08] bg-[#10141f]/85">
      <div className="flex items-center gap-3 border-b border-white/[0.06] p-6">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-400/10 text-purple-300">
          <History className="h-5 w-5" />
        </div>

        <div>
          <h2 className="font-semibold text-white">
            Transaction history
          </h2>

          <p className="mt-1 text-xs text-slate-500">
            Immutable paper-trading ledger
          </p>
        </div>
      </div>

      {transactions.length === 0 ? (
        <div className="p-10 text-center">
          <p className="text-sm text-slate-500">
            No transactions recorded.
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[950px]">
            <thead className="bg-black/20 text-left text-xs uppercase tracking-wider text-slate-500">
              <tr>
                <th className="px-6 py-4">Trade</th>
                <th className="px-6 py-4">Quantity</th>
                <th className="px-6 py-4">Price</th>
                <th className="px-6 py-4">Gross value</th>
                <th className="px-6 py-4">Fees</th>
                <th className="px-6 py-4">Cash effect</th>
                <th className="px-6 py-4">Executed</th>
              </tr>
            </thead>

            <tbody>
              {transactions.map((transaction) => {
                const buy =
                  transaction.side === "BUY";

                const SideIcon = buy
                  ? ArrowDownToLine
                  : ArrowUpFromLine;

                return (
                  <tr
                    key={transaction.id}
                    className="border-t border-white/[0.05] text-sm"
                  >
                    <td className="px-6 py-5">
                      <div className="flex items-center gap-3">
                        <div
                          className={`flex h-9 w-9 items-center justify-center rounded-lg ${
                            buy
                              ? "bg-emerald-400/10 text-emerald-300"
                              : "bg-red-400/10 text-red-300"
                          }`}
                        >
                          <SideIcon className="h-4 w-4" />
                        </div>

                        <div>
                          <p className="font-semibold text-white">
                            {transaction.symbol}
                          </p>

                          <p
                            className={`text-xs ${
                              buy
                                ? "text-emerald-300"
                                : "text-red-300"
                            }`}
                          >
                            {transaction.side}
                          </p>
                        </div>
                      </div>
                    </td>

                    <td className="px-6 py-5 text-slate-300">
                      {transaction.quantity}
                    </td>

                    <td className="px-6 py-5 text-slate-300">
                      {formatCurrency(
                        transaction.executed_price,
                      )}
                    </td>

                    <td className="px-6 py-5 text-slate-300">
                      {formatCurrency(
                        transaction.gross_amount,
                      )}
                    </td>

                    <td className="px-6 py-5 text-amber-300">
                      {formatCurrency(transaction.fees)}
                    </td>

                    <td
                      className={`px-6 py-5 font-medium ${
                        Number(
                          transaction.net_cash_effect,
                        ) >= 0
                          ? "text-emerald-300"
                          : "text-red-300"
                      }`}
                    >
                      {Number(
                        transaction.net_cash_effect,
                      ) > 0
                        ? "+"
                        : ""}
                      {formatCurrency(
                        transaction.net_cash_effect,
                      )}
                    </td>

                    <td className="px-6 py-5 text-xs text-slate-500">
                      {formatDateTime(
                        transaction.executed_at,
                      )}
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