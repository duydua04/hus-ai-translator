import { useState, useCallback } from "react";
import DashboardAPI from "../api/DashboardApi";

export function useDashboard() {
  const [overview, setOverview] = useState(null);
  const [weeklyChart, setWeeklyChart] = useState([]);
  const [hourlyChart, setHourlyChart] = useState([]);
  const [ratingDistribution, setRatingDistribution] = useState([null]);
  const [directionStats, setDirectionStats] = useState([null]);
  const [recentUsers, setRecentUsers] = useState([]);
  const [recentFeedbacks, setRecentFeedbacks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch tất cả trong một lần
  const fetchFullDashboard = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await DashboardAPI.getFullDashboard();
      setOverview(data.overview ?? null);
      setWeeklyChart(data.weekly_chart?.data ?? []);
      setHourlyChart(data.hourly_chart?.data ?? []);
      setRatingDistribution(data.rating_distribution ?? null);
      setDirectionStats(data.direction_stats ?? null);
      setRecentUsers(data.recent_users ?? []);
      setRecentFeedbacks(data.recent_feedbacks ?? []);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Không thể tải dữ liệu dashboard."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch riêng từng phần
  const fetchOverview = useCallback(async () => {
    try {
      const data = await DashboardAPI.getOverview();
      setOverview(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Không thể tải tổng quan.");
    }
  }, []);

  const fetchWeeklyChart = useCallback(async () => {
    try {
      const data = await DashboardAPI.getWeeklyChart();
      setWeeklyChart(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Không thể tải biểu đồ tuần.");
    }
  }, []);

  const fetchHourlyChart = useCallback(async () => {
    try {
      const data = await DashboardAPI.getHourlyChart();
      setHourlyChart(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Không thể tải biểu đồ giờ.");
    }
  }, []);

  const fetchRatingDistribution = useCallback(async () => {
    try {
      const data = await DashboardAPI.getRatingDistribution();
      setRatingDistribution(data);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Không thể tải phân phối đánh giá."
      );
    }
  }, []);

  const fetchDirectionStats = useCallback(async () => {
    try {
      const data = await DashboardAPI.getDirectionStats();
      setDirectionStats(data);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Không thể tải thống kê hướng dịch."
      );
    }
  }, []);

  const fetchRecentUsers = useCallback(async () => {
    try {
      const data = await DashboardAPI.getRecentUsers();
      setRecentUsers(data);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Không thể tải người dùng gần đây."
      );
    }
  }, []);

  const fetchRecentFeedbacks = useCallback(async () => {
    try {
      const data = await DashboardAPI.getRecentFeedbacks();
      setRecentFeedbacks(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Không thể tải feedback gần đây.");
    }
  }, []);

  return {
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
    fetchOverview,
    fetchWeeklyChart,
    fetchHourlyChart,
    fetchRatingDistribution,
    fetchDirectionStats,
    fetchRecentUsers,
    fetchRecentFeedbacks,
  };
}
