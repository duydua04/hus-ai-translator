import React, { useEffect } from "react";
import { useDashboard } from "../../hooks/useDashboard";
import WeeklyLineChart from "./charts/WeeklyLineChart";
import RatingCard from "./charts/RatingCard";
import HourlyBarChart from "./charts/HourlyBarChart";
import DirectionCard from "./charts/DirectionCard";
import RecentUsersCard from "./charts/RecentUserCard";
import FeedbackCard from "./charts/FeedbackCard";
import "./DashPage.scss";

const fmt = (n) =>
  n == null
    ? "—"
    : n >= 1_000_000
    ? (n / 1_000_000).toFixed(1) + "M"
    : n >= 1_000
    ? (n / 1_000).toFixed(1).replace(".0", "") + "k"
    : String(n);

function MetricCard({ label, value, change, change_label, extra, variant }) {
  const trendDir = change < 0 ? "down" : "up";
  return (
    <div className={`metric-card metric-card--${variant}`}>
      <div className="metric-card__label">{label}</div>
      <div className="metric-card__value">{fmt(value)}</div>
      {extra ? (
        <div className="metric-card__trend metric-card__trend--neutral">
          {extra}
        </div>
      ) : change !== 0 ? (
        <div className={`metric-card__trend metric-card__trend--${trendDir}`}>
          {change > 0 ? "↑" : "↓"} {Math.abs(change).toFixed(1)}% {change_label}
        </div>
      ) : (
        <div className="metric-card__trend metric-card__trend--neutral">
          — {change_label}
        </div>
      )}
    </div>
  );
}

export default function DashPage() {
  const {
    overview,
    weeklyChart,
    hourlyChart,
    ratingDistribution,
    directionStats,
    recentUsers,
    recentFeedbacks,
    loading,
    error,
    fetchFullDashboard,
  } = useDashboard();

  useEffect(() => {
    fetchFullDashboard();
  }, [fetchFullDashboard]);

  if (loading) return <div className="dash-loading">Đang tải dữ liệu…</div>;
  if (error) return <div className="dash-error">{error}</div>;

  const METRICS = [
    { label: "Tổng người dùng", variant: "blue", ...overview?.total_users },
    { label: "Đăng ký mới", variant: "green", ...overview?.new_registrations },
    {
      label: "Lượt dịch hôm nay",
      variant: "amber",
      ...overview?.translations_today,
    },
    { label: "Đánh giá mới", variant: "purple", ...overview?.new_feedbacks },
  ];

  return (
    <div className="dash-page">
      <div className="metrics-grid">
        {METRICS.map((m) => (
          <MetricCard key={m.label} {...m} />
        ))}
      </div>

      <div className="charts-row">
        <WeeklyLineChart data={weeklyChart} />
        <RatingCard ratingData={ratingDistribution} />
      </div>

      <div className="charts-row">
        <HourlyBarChart
          data={hourlyChart}
          peakMorning={hourlyChart?.peak_morning}
          peakEvening={hourlyChart?.peak_evening}
        />
        <DirectionCard stats={directionStats} />
      </div>

      <div className="charts-row charts-row--equal">
        <RecentUsersCard users={recentUsers} />
        <FeedbackCard feedbacks={recentFeedbacks} />
      </div>
    </div>
  );
}
