"use client";

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  formatChartDate,
  formatCompactNumber,
  formatCurrency,
} from "../market-utils";

import type { PriceCandle } from "../types";

interface PriceChartProps {
  candles: PriceCandle[];
  currency: string;
}

export function PriceChart({
  candles,
  currency,
}: PriceChartProps) {
  const data = candles.map((candle) => ({
    date: candle.timestamp,
    close: Number(candle.close),
    open: Number(candle.open),
    high: Number(candle.high),
    low: Number(candle.low),
    volume: candle.volume,
    returnPercent: Number(
      candle.return_percent ?? 0,
    ),
  }));

  return (
    <section className="rounded-[28px] border border-white/[0.08] bg-[#10141f]/85 p-6 shadow-2xl shadow-black/20 backdrop-blur-xl">
      <div>
        <p className="text-xs font-medium uppercase tracking-[0.16em] text-emerald-300">
          Historical performance
        </p>

        <h3 className="mt-2 text-xl font-semibold text-white">
          Price movement
        </h3>

        <p className="mt-1 text-sm text-slate-500">
          Daily closing price with traded volume
        </p>
      </div>

      <div className="mt-8 h-[340px] w-full">
        <ResponsiveContainer
          width="100%"
          height="100%"
        >
          <AreaChart
            data={data}
            margin={{
              top: 10,
              right: 10,
              left: 0,
              bottom: 0,
            }}
          >
            <defs>
              <linearGradient
                id="closePriceGradient"
                x1="0"
                y1="0"
                x2="0"
                y2="1"
              >
                <stop
                  offset="0%"
                  stopColor="#34d399"
                  stopOpacity={0.35}
                />
                <stop
                  offset="100%"
                  stopColor="#34d399"
                  stopOpacity={0}
                />
              </linearGradient>
            </defs>

            <CartesianGrid
              stroke="#ffffff0d"
              vertical={false}
            />

            <XAxis
              dataKey="date"
              tickFormatter={formatChartDate}
              tick={{
                fill: "#64748b",
                fontSize: 11,
              }}
              axisLine={false}
              tickLine={false}
              minTickGap={30}
            />

            <YAxis
              domain={["auto", "auto"]}
              tickFormatter={(value) =>
                `₹${Number(value).toFixed(0)}`
              }
              tick={{
                fill: "#64748b",
                fontSize: 11,
              }}
              axisLine={false}
              tickLine={false}
              width={58}
            />

            <Tooltip
              labelFormatter={(label) =>
                formatChartDate(String(label))
              }
              formatter={(value) => [
                formatCurrency(
                  Number(value),
                  currency,
                ),
                "Close",
              ]}
              contentStyle={{
                background: "#0b0f18",
                border: "1px solid #ffffff14",
                borderRadius: "12px",
                color: "#e2e8f0",
              }}
            />

            <Area
              type="monotone"
              dataKey="close"
              stroke="#34d399"
              strokeWidth={2}
              fill="url(#closePriceGradient)"
              dot={false}
              activeDot={{
                r: 5,
                fill: "#34d399",
                stroke: "#080b12",
                strokeWidth: 3,
              }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-6 h-[140px] w-full border-t border-white/[0.06] pt-5">
        <ResponsiveContainer
          width="100%"
          height="100%"
        >
          <BarChart data={data}>
            <XAxis
              dataKey="date"
              hide
            />

            <YAxis hide />

            <Tooltip
              labelFormatter={(label) =>
                formatChartDate(String(label))
              }
              formatter={(value) => [
                formatCompactNumber(Number(value)),
                "Volume",
              ]}
              cursor={{
                fill: "rgba(255,255,255,0.03)",
              }}
              contentStyle={{
                background: "#0b0f18",
                border: "1px solid #ffffff14",
                borderRadius: "12px",
                color: "#e2e8f0",
              }}
            />

            <Bar
              dataKey="volume"
              fill="#22d3ee"
              opacity={0.45}
              radius={[3, 3, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}