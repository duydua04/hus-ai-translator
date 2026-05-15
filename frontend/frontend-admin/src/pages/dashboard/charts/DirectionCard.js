import React from "react";
import Stars from "./Stars";

export default function DirectionCard({ stats }) {
  if (!stats) return null;
  const {
    en_to_vi_count,
    vi_to_en_count,
    en_to_vi_pct,
    vi_to_en_pct,
    en_to_vi_avg_rating,
    vi_to_en_avg_rating,
  } = stats;

  const fmt = (n) =>
    n == null
      ? "—"
      : n >= 1_000
      ? (n / 1_000).toFixed(1).replace(".0", "") + "k"
      : String(n);

  return (
    <div className="chart-card">
      <div className="chart-card__header">
        <div className="chart-card__title">Tổng số lượt dịch</div>
      </div>
      <div className="direction-boxes">
        <div className="direction-box direction-box--primary">
          <div className="direction-box__arrow">
            EN <i className="bx bx-right-arrow-alt" /> VI
          </div>
          <div className="direction-box__count">{fmt(en_to_vi_count)}</div>
          <div className="direction-box__sub">{en_to_vi_pct}% tổng lượt</div>
        </div>
        <div className="direction-box direction-box--secondary">
          <div className="direction-box__arrow">
            VI <i className="bx bx-right-arrow-alt" /> EN
          </div>
          <div className="direction-box__count">{fmt(vi_to_en_count)}</div>
          <div className="direction-box__sub">{vi_to_en_pct}% tổng lượt</div>
        </div>
      </div>
      <div className="direction-bar-label">Tỉ lệ chiều dịch</div>
      <div className="direction-bar">
        <div
          className="direction-bar__fill direction-bar__fill--a"
          style={{ width: `${en_to_vi_pct}%` }}
        />
        <div
          className="direction-bar__fill direction-bar__fill--b"
          style={{ width: `${vi_to_en_pct}%` }}
        />
      </div>
      <div className="direction-legend">
        <span className="direction-legend__item direction-legend__item--a">
          EN <i className="bx bx-right-arrow-alt" /> VI {en_to_vi_pct}%
        </span>
        <span className="direction-legend__item direction-legend__item--b">
          VI <i className="bx bx-right-arrow-alt" /> EN {vi_to_en_pct}%
        </span>
      </div>
      <div className="direction-ratings">
        <span>Trung bình đánh giá</span>
        <span>
          EN <i className="bx bx-right-arrow-alt" />
          VI <Stars value={en_to_vi_avg_rating} />{" "}
          {en_to_vi_avg_rating?.toFixed(1)}
        </span>
        <span>
          VI <i className="bx bx-right-arrow-alt" /> EN{" "}
          <Stars value={vi_to_en_avg_rating} />{" "}
          {vi_to_en_avg_rating?.toFixed(1)}
        </span>
      </div>
    </div>
  );
}
