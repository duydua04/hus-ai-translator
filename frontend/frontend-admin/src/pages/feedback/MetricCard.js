import React from "react";

export default function MetricCard({
  label,
  value,
  trend,
  trendType,
  color,
  icon,
}) {
  return (
    <div className={`metric-card metric-card--${color}`}>
      <div className="metric-card__icon">
        <i className={`bx ${icon}`} />
      </div>
      <div className="metric-card__label">{label}</div>
      <div className="metric-card__value">{value}</div>
      <div className={`metric-card__trend metric-card__trend--${trendType}`}>
        {trend}
      </div>
    </div>
  );
}
