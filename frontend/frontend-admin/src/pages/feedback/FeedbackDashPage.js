import React from "react";
import MetricCard from "./MetricCard";
import BarChartCard from "./BarChartCard";
import DonutChartCard from "./DonutChartCard";
import { useFeedbackDashboard } from "../../hooks/useFeedback";
import "./FeedbackDashPage.scss";

export default function FeedbackDashPage() {
  const { data, loading, period, setPeriod } = useFeedbackDashboard();

  if (loading || !data)
    return (
      <div className="page page--active">
        <p style={{ padding: 24, color: "var(--ink4)" }}>Đang tải...</p>
      </div>
    );

  return (
    <div className="page page--active" id="page-feedback-dash">
      <div className="page__header">
        <div>
          <div className="page__title">Dashboard Feedback</div>
          <div className="page__subtitle">Tổng quan đánh giá người dùng</div>
        </div>
        <select
          className="filter-select"
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
        >
          <option value="month">Tháng này</option>
          <option value="last_month">Tháng trước</option>
          <option value="quarter">Quý này</option>
          <option value="year">Năm nay</option>
        </select>
      </div>

      <div className="metrics-grid">
        {data.metrics.map((m) => (
          <MetricCard key={m.id} {...m} />
        ))}
      </div>

      <div className="charts-row">
        <BarChartCard data={data.ratingDistribution} total={1020} />
        <DonutChartCard categories={data.categoryDistribution} avgScore="4.3" />
      </div>
    </div>
  );
}
