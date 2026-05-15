import { useState, useEffect, useCallback } from "react";
import FeedbackAPI from "../api/FeedbackApi";

function getInitials(name) {
  if (!name) return "?";
  return name
    .trim()
    .split(" ")
    .slice(-2)
    .map((w) => w[0])
    .join("")
    .toUpperCase();
}

function resolveType(rating) {
  if (rating >= 4) return { type: "positive", typeLabel: "Tích cực" };
  if (rating === 3) return { type: "neutral", typeLabel: "Trung lập" };
  return { type: "negative", typeLabel: "Tiêu cực" };
}

function normalizeFeedbackItem(f) {
  const { type, typeLabel } = resolveType(f.rating);
  return {
    id: f.id,
    translationId: f.translation_id,
    userId: f.user_id,
    name: "—",
    initials: "?",
    avatarBg: "#e0e7ff",
    avatarColor: "#4f46e5",
    rating: f.rating,
    correctedContent: f.corrected_content || "",
    feedbackNote: f.feedback_note || "",
    type,
    typeLabel,
    createdAt: f.created_at
      ? new Date(f.created_at).toLocaleDateString("vi-VN")
      : "—",
  };
}

function normalizeFeedbackDetail({ feedback, translation, user }) {
  const { type, typeLabel } = resolveType(feedback.rating);
  const name = user?.full_name || user?.email || "Ẩn danh";
  return {
    id: feedback.id,
    translationId: feedback.translation_id,
    userId: feedback.user_id,
    name,
    email: user?.email || "—",
    tier: user?.tier || "—",
    initials: getInitials(name),
    avatarBg: "#e0e7ff",
    avatarColor: "#4f46e5",
    rating: feedback.rating,
    correctedContent: feedback.corrected_content || "",
    feedbackNote: feedback.feedback_note || "",
    type,
    typeLabel,
    createdAt: feedback.created_at
      ? new Date(feedback.created_at).toLocaleDateString("vi-VN")
      : "—",
    translation: translation
      ? {
          id: translation.id,
          type: translation.type,
          inputContent: translation.input_content,
          translatedContent: translation.translated_content,
          status: translation.status,
        }
      : null,
  };
}

function normalizeStats(s) {
  return {
    totalFeedbacks: s.total_feedbacks ?? 0,
    averageRating: s.average_rating ?? 0,
    distribution: s.distribution ?? {},
    totalWithCorrection: s.total_with_correction ?? 0,
  };
}

export function useFeedbacks() {
  const [feedbacks, setFeedbacks] = useState([]);
  const [total, setTotal] = useState(0);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [statsLoading, setStatsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    page: 1,
    limit: 5,
    search: "",
    rating: "",
  });

  const [selectedFeedback, setSelectedFeedback] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState(null);

  const fetchFeedbacks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page: filters.page,
        limit: filters.limit,
      };
      if (filters.search) params.search = filters.search;
      if (filters.rating !== "") params.rating = Number(filters.rating);

      const data = await FeedbackAPI.getFeedbacks(params);
      setFeedbacks((data.data ?? []).map(normalizeFeedbackItem));
      setTotal(data.total ?? 0);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Không thể tải danh sách feedback."
      );
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchFeedbacks();
  }, [fetchFeedbacks]);

  const fetchStats = useCallback(async () => {
    setStatsLoading(true);
    try {
      const data = await FeedbackAPI.getStats();
      setStats(normalizeStats(data));
    } catch (err) {
      setError(
        err.response?.data?.detail || "Không thể tải thống kê feedback."
      );
    } finally {
      setStatsLoading(false);
    }
  }, []);

  const openDetail = async (feedbackId) => {
    setSelectedFeedback(null);
    setDetailError(null);
    setDetailLoading(true);
    try {
      const data = await FeedbackAPI.getFeedbackDetail(feedbackId);
      setSelectedFeedback(normalizeFeedbackDetail(data));
    } catch (err) {
      setDetailError(
        err.response?.data?.detail || "Không thể tải chi tiết feedback."
      );
    } finally {
      setDetailLoading(false);
    }
  };

  const closeDetail = () => {
    setSelectedFeedback(null);
    setDetailError(null);
  };

  const deleteFeedback = async (feedbackId) => {
    try {
      await FeedbackAPI.deleteFeedback(feedbackId);
      setFeedbacks((prev) => prev.filter((f) => f.id !== feedbackId));
      setTotal((prev) => prev - 1);
      if (selectedFeedback?.id === feedbackId) closeDetail();
    } catch (err) {
      setError(err.response?.data?.detail || "Không thể xóa feedback.");
    }
  };

  return {
    feedbacks,
    total,
    stats,
    loading,
    statsLoading,
    error,
    filters,
    setFilters,
    fetchStats,
    selectedFeedback,
    detailLoading,
    detailError,
    openDetail,
    closeDetail,
    deleteFeedback,
  };
}
