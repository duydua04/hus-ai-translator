import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Cell,
} from "recharts";

const fmt = (n) =>
  n == null
    ? "—"
    : n >= 1_000
    ? (n / 1_000).toFixed(1).replace(".0", "") + "k"
    : String(n);

export default function HourlyBarChart({ data, peakMorning, peakEvening }) {
  const TIMEZONE_OFFSET = 7;

  const chartData = (data ?? [])
    .map((d) => {
      const localHour = (d.hour + TIMEZONE_OFFSET) % 24;
      return {
        hour: localHour,
        count: (d.text_count ?? 0) + (d.file_count ?? 0),
      };
    })
    .sort((a, b) => a.hour - b.hour);

  const maxCount = Math.max(...chartData.map((d) => d.count), 0);

  return (
    <div className="chart-card">
      <div className="chart-card__header">
        <div className="chart-card__title">Lượt dịch theo giờ trong ngày</div>
      </div>
      <ResponsiveContainer width="100%" height={180}>
        <BarChart
          data={chartData}
          margin={{ top: 4, right: 8, left: -10, bottom: 0 }}
          barCategoryGap="15%"
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="var(--border2)"
            vertical={false}
          />
          <XAxis
            dataKey="hour"
            tick={{ fontSize: 10, fill: "var(--ink4)" }}
            axisLine={false}
            tickLine={false}
            interval={3}
            tickFormatter={(v) => `${v}h`}
          />
          <YAxis
            tick={{ fontSize: 10, fill: "var(--ink4)" }}
            axisLine={false}
            tickLine={false}
            tickFormatter={fmt}
          />
          <Tooltip
            formatter={(v) => [fmt(v), "Tổng lượt dịch"]}
            labelFormatter={(v) => `${v}:00 – ${v}:59`}
            contentStyle={{
              background: "var(--surface)",
              border: "1px solid var(--border2)",
              borderRadius: 8,
              fontSize: 12,
            }}
          />
          <Bar dataKey="count" radius={[3, 3, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell
                key={index}
                fill={
                  entry.count === maxCount && maxCount > 0
                    ? "#27ae60"
                    : "#2980b9"
                }
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="peak-hints">
        {peakMorning && (
          <span className="peak-hint peak-hint--morning">
            Cao điểm sáng: {peakMorning}h
          </span>
        )}
        {peakEvening && (
          <span className="peak-hint peak-hint--evening">
            Cao điểm tối: {peakEvening}h
          </span>
        )}
      </div>
    </div>
  );
}
