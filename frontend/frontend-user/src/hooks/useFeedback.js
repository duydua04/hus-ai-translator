import { useState, useCallback } from "react";
import {
  createFeedback as apiCreateFeedback,
  getMyFeedbacks as apiGetMyFeedbacks,
  getFeedbackByTranslation as apiGetFeedbackByTranslation,
  getFeedbackDetail as apiGetFeedbackDetail,
  updateFeedback as apiUpdateFeedback,
  deleteFeedback as apiDeleteFeedback,
} from "../api/feedbackApi";

export default function useFeedback() {
  const [feedbacks, setFeedbacks] = useState([]);
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const showError = useCallback((msg) => {
    setError(msg);
    setTimeout(() => setError(null), 3000);
  }, []);

  const showSuccess = useCallback((msg) => {
    setSuccess(msg);
    setTimeout(() => setSuccess(null), 3000);
  }, []);

  const clearMessages = useCallback(() => {
    setError(null);
    setSuccess(null);
  }, []);

  const fetchMyFeedbacks = useCallback(async (params = {}) => {
    setLoading(true);
    try {
      const data = await apiGetMyFeedbacks(params);
      setFeedbacks(data?.data ?? []);
      return { success: true, data };
    } catch (err) {
      const msg =
        err.response?.data?.detail || "Không thể tải danh sách đánh giá.";
      showError(msg);
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchFeedbackByTranslation = useCallback(async (translationId) => {
    setLoading(true);
    try {
      const data = await apiGetFeedbackByTranslation(translationId);
      setDetail(data);
      return { success: true, data };
    } catch (err) {
      const msg = err.response?.data?.detail || "Không thể tải đánh giá.";
      showError(msg);
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchFeedbackDetail = useCallback(async (feedbackId) => {
    setLoading(true);
    try {
      const data = await apiGetFeedbackDetail(feedbackId);
      setDetail(data);
      return { success: true, data };
    } catch (err) {
      const msg =
        err.response?.data?.detail || "Không thể tải chi tiết đánh giá.";
      showError(msg);
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  }, []);

  const submitFeedback = useCallback(async (payload) => {
    setLoading(true);
    clearMessages();
    try {
      const data = await apiCreateFeedback(payload);
      showSuccess("Gửi đánh giá thành công.");
      return { success: true, data };
    } catch (err) {
      const msg = err.response?.data?.detail || "Gửi đánh giá thất bại.";
      showError(msg);
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  }, []);

  const editFeedback = useCallback(async (feedbackId, payload) => {
    setLoading(true);
    clearMessages();
    try {
      const data = await apiUpdateFeedback(feedbackId, payload);
      setFeedbacks((prev) =>
        prev.map((f) => (f.id === feedbackId ? { ...f, ...data } : f))
      );
      showSuccess("Cập nhật đánh giá thành công.");
      return { success: true, data };
    } catch (err) {
      const msg = err.response?.data?.detail || "Cập nhật đánh giá thất bại.";
      showError(msg);
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  }, []);

  const removeFeedback = useCallback(async (feedbackId) => {
    setLoading(true);
    clearMessages();
    try {
      await apiDeleteFeedback(feedbackId);
      setFeedbacks((prev) => prev.filter((f) => f.id !== feedbackId));
      showSuccess("Xóa đánh giá thành công.");
      return { success: true };
    } catch (err) {
      const msg = err.response?.data?.detail || "Xóa đánh giá thất bại.";
      showError(msg);
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    feedbacks,
    detail,
    loading,
    error,
    success,
    clearMessages,
    fetchMyFeedbacks,
    fetchFeedbackByTranslation,
    fetchFeedbackDetail,
    submitFeedback,
    editFeedback,
    removeFeedback,
  };
}
