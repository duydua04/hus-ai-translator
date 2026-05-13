import React from "react";

export default function BarChartCard({ data, total }) {
  return (
    <div className="chart-card">
      <div className="chart-card__header">
        <div>
          <div className="chart-card__title">Phân bố đánh giá theo sao</div>
          <div className="chart-card__subtitle">
            Tổng {total.toLocaleString()} lượt đánh giá
          </div>
        </div>
        <span className="count-chip">{total.toLocaleString()}</span>
      </div>
      <div className="bar-chart">
        {data.map(({ star, count, pct, gradient }) => (
          <div className="bar-chart__row" key={star}>
            <div className="bar-chart__label">{star} ★</div>
            <div className="bar-chart__track">
              <div
                className="bar-chart__fill"
                style={{ width: `${pct}%`, background: gradient }}
              />
            </div>
            <div className="bar-chart__count">{count}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
