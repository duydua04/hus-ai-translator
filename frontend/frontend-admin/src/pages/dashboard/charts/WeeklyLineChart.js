import React from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

const DAY_LABELS = ["CN", "T2", "T3", "T4", "T5", "T6", "T7"];
const dayLabel = (dateStr) => DAY_LABELS[new Date(dateStr).getDay()];
const fmt = (n) =>
  n == null
    ? "—"
    : n >= 1_000_000
    ? (n / 1_000_000).toFixed(1) + "M"
    : n >= 1_000
    ? (n / 1_000).toFixed(1).replace(".0", "") + "k"
    : String(n);

export default function WeeklyLineChart({ data }) {
  const chartData = (data ?? []).map((d) => ({
    day: dayLabel(d.date),
    count: d.count,
  }));

  return (
    <div className="chart-card">
      <div className="chart-card__header">
        <div className="chart-card__title">Lượt dịch 7 ngày qua</div>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart
          data={chartData}
          margin={{ top: 4, right: 8, left: -10, bottom: 0 }}
        >
          <defs>
            <linearGradient id="weeklyGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#2980b9" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#2980b9" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="var(--border2)"
            vertical={false}
          />
          <XAxis
            dataKey="day"
            tick={{ fontSize: 11, fill: "var(--ink4)" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "var(--ink4)" }}
            axisLine={false}
            tickLine={false}
            tickFormatter={fmt}
          />
          <Tooltip
            formatter={(v) => [fmt(v), "Lượt dịch"]}
            contentStyle={{
              background: "var(--surface)",
              border: "1px solid var(--border2)",
              borderRadius: 8,
              fontSize: 12,
            }}
          />
          <Area
            type="monotone"
            dataKey="count"
            stroke="#2980b9"
            strokeWidth={2.5}
            fill="url(#weeklyGradient)"
            dot={{ r: 3, fill: "#2980b9", strokeWidth: 0 }}
            activeDot={{ r: 5, fill: "#2980b9" }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
