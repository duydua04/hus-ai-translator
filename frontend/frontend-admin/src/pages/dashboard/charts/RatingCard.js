import React from "react";
import Stars from "./Stars";

const fmt = (n) =>
  n == null
    ? "—"
    : n >= 1_000
    ? (n / 1_000).toFixed(1).replace(".0", "") + "k"
    : String(n);

export default function RatingCard({ ratingData }) {
  if (!ratingData || !ratingData.distribution) return null;
  const { avg_rating, total_feedbacks, distribution } = ratingData;

  const dist = [5, 4, 3, 2, 1].map((star) => ({
    star,
    count: distribution[star] ?? distribution[String(star)] ?? 0,
  }));
  const max = Math.max(...dist.map((d) => d.count), 1);

  return (
    <div className="chart-card">
      <div className="chart-card__header">
        <div className="chart-card__title">Phân bổ đánh giá sao</div>
      </div>
      <div className="rating-overview">
        <div className="rating-overview__big">{avg_rating?.toFixed(1)}</div>
        <div>
          <Stars value={avg_rating} />
          <div className="rating-overview__total">
            {fmt(total_feedbacks)} đánh giá
          </div>
        </div>
      </div>
      <div className="bar-chart">
        {dist.map((item, idx) => (
          <div className="bar-chart__row" key={item.star}>
            <span className="bar-chart__label">
              {item.star}
              <i className="bx bxs-star" style={{ color: "#e8d317" }} />
            </span>
            <div className="bar-chart__track">
              <div
                className="bar-chart__fill"
                style={{
                  width: `${(item.count / max) * 100}%`,
                  background: "#e8d317",
                }}
              />
            </div>
            <span className="bar-chart__count">{item.count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
