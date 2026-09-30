"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { formatCrores } from "../market-utils";
import type { FinancialStatement } from "../types";

interface FinancialComparisonChartProps {
  latest: FinancialStatement;
  previous: FinancialStatement | null;
}

export function FinancialComparisonChart({
  latest,
  previous,
}: FinancialComparisonChartProps) {
  const data = [
    {
      metric: "Revenue",
      previous: Number(previous?.revenue ?? 0),
      latest: Number(latest.revenue),
    },
    {
      metric: "EBITDA",
      previous: Number(previous?.ebitda ?? 0),
      latest: Number(latest.ebitda),
    },
    {
      metric: "Net income",
      previous: Number(previous?.net_income ?? 0),
      latest: Number(latest.net_income),
    },
  ];

  return (
    <div className="rounded-2xl border border-white/[0.07] bg-black/20 p-5">
      <div>
        <h4 className="font-medium text-white">Financial performance</h4>

        <p className="mt-1 text-xs text-slate-500">
          {previous?.fiscal_year ?? "Previous"} versus {latest.fiscal_year},
          values in INR crore
        </p>
      </div>

      <div className="mt-6 h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{
              top: 10,
              right: 10,
              bottom: 0,
              left: 5,
            }}
          >
            <CartesianGrid stroke="#ffffff0d" vertical={false} />

            <XAxis
              dataKey="metric"
              axisLine={false}
              tickLine={false}
              tick={{
                fill: "#94a3b8",
                fontSize: 11,
              }}
            />

            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{
                fill: "#64748b",
                fontSize: 11,
              }}
              tickFormatter={(value) => `${(Number(value) / 1000).toFixed(0)}K`}
            />

            <Tooltip
              formatter={(value) => formatCrores(Number(value))}
              contentStyle={{
                background: "#0b0f18",
                border: "1px solid #ffffff14",
                borderRadius: "12px",
                color: "#e2e8f0",
              }}
            />

            <Legend
              formatter={(value) =>
                value === "latest"
                  ? latest.fiscal_year
                  : (previous?.fiscal_year ?? "Previous")
              }
            />

            <Bar dataKey="previous" fill="#334155" radius={[5, 5, 0, 0]} />

            <Bar dataKey="latest" fill="#34d399" radius={[5, 5, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
