import React from "react";

const DONUT_SEGMENTS = [
  { stroke: "#33823C", dasharray: "51 49", dashoffset: "25" },
  { stroke: "#EF9F27", dasharray: "20 80", dashoffset: "-26" },
  { stroke: "#E24B4A", dasharray: "11 89", dashoffset: "-46" },
  { stroke: "#C0D0CC", dasharray: "7 93", dashoffset: "-57" },
];

export default function DonutChartCard({ categories, avgScore }) {
  return (
    <div className="chart-card">
      <div className="chart-card__header">
        <div>
          <div className="chart-card__title">Phân loại feedback</div>
          <div className="chart-card__subtitle">Theo danh mục</div>
        </div>
      </div>
      <div className="donut-chart">
        <svg width="110" height="110" viewBox="0 0 36 36">
          <circle
            cx="18"
            cy="18"
            r="14"
            fill="none"
            stroke="#EAF7ED"
            strokeWidth="4"
          />
          {DONUT_SEGMENTS.map((seg, i) => (
            <circle
              key={i}
              cx="18"
              cy="18"
              r="14"
              fill="none"
              stroke={seg.stroke}
              strokeWidth="4"
              strokeDasharray={seg.dasharray}
              strokeDashoffset={seg.dashoffset}
              transform="rotate(-90 18 18)"
            />
          ))}
          <text
            x="18"
            y="17"
            textAnchor="middle"
            fontSize="5"
            fontWeight="700"
            fill="#0D2D12"
          >
            {avgScore}
          </text>
          <text x="18" y="22" textAnchor="middle" fontSize="3" fill="#567060">
            avg
          </text>
        </svg>
        <div className="donut-chart__legend">
          {categories.map(({ label, pct, color }) => (
            <div className="donut-chart__legend-item" key={label}>
              <div
                className="donut-chart__swatch"
                style={{ background: color }}
              />
              {label}
              <span className="donut-chart__pct">{pct}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
