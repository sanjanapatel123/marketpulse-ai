"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { formatCurrency } from "../../../features/market/market-utils";

import type { PortfolioSummary } from "../types";

interface AllocationChartProps {
  summary: PortfolioSummary;
}

const COLORS = {
  cash: "#22d3ee",
  invested: "#34d399",
};

export function AllocationChart({ summary }: AllocationChartProps) {
  const cash = Number(summary.cash_balance);
  const invested = Number(summary.positions_market_value);

  const data = [
    {
      name: "Cash",
      value: cash,
      color: COLORS.cash,
    },
    {
      name: "Invested",
      value: invested,
      color: COLORS.invested,
    },
  ].filter((item) => item.value > 0);

  const total = cash + invested;

  const cashPercent = total > 0 ? (cash / total) * 100 : 0;

  const investedPercent = total > 0 ? (invested / total) * 100 : 0;

  return (
    <section className="rounded-[28px] border border-white/[0.08] bg-[#10141f]/85 p-6">
      <div>
        <h2 className="font-semibold text-white">Portfolio allocation</h2>

        <p className="mt-1 text-xs text-slate-500">
          Cash versus current invested value
        </p>
      </div>

      <div className="mt-4 grid items-center gap-4 sm:grid-cols-[180px_1fr]">
        <div className="h-[180px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                dataKey="value"
                nameKey="name"
                innerRadius={52}
                outerRadius={76}
                paddingAngle={3}
                stroke="none"
              >
                {data.map((item) => (
                  <Cell key={item.name} fill={item.color} />
                ))}
              </Pie>

              <Tooltip
                formatter={(value) => formatCurrency(Number(value))}
                contentStyle={{
                  background: "#0b0f18",
                  border: "1px solid #ffffff14",
                  borderRadius: "12px",
                  color: "#e2e8f0",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="space-y-4">
          <AllocationItem
            label="Available cash"
            value={cash}
            percentage={cashPercent}
            color="bg-cyan-400"
          />

          <AllocationItem
            label="Invested value"
            value={invested}
            percentage={investedPercent}
            color="bg-emerald-400"
          />
        </div>
      </div>
    </section>
  );
}

interface AllocationItemProps {
  label: string;
  value: number;
  percentage: number;
  color: string;
}

function AllocationItem({
  label,
  value,
  percentage,
  color,
}: AllocationItemProps) {
  return (
    <div>
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <span className={`h-2.5 w-2.5 rounded-full ${color}`} />

          <span className="text-xs text-slate-400">{label}</span>
        </div>

        <span className="text-xs font-medium text-slate-300">
          {percentage.toFixed(1)}%
        </span>
      </div>

      <p className="mt-1 pl-4 text-sm font-semibold text-white">
        {formatCurrency(value)}
      </p>
    </div>
  );
}
