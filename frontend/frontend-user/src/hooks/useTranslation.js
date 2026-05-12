import { useState, useCallback } from "react";
import {
  getLanguage as apiGetLanguages,
  translateText as apiTranslateText,
  translateFile as apiTranslateDocument,
  getHistory as apiGetHistory,
  getTranslationDetail as apiGetTranslationDetail,
  deleteTranslation as apiDeleteTranslation,
} from "../api/translationApi";

export default function useTranslation() {
  const [languages, setLanguages] = useState([]);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [total, setTotal] = useState(0);
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const clearMessages = useCallback(() => {
    setError(null);
    setSuccess(null);
  }, []);

  const fetchLanguages = useCallback(async () => {
    try {
      const data = await apiGetLanguages();
      setLanguages(data);
    } catch (err) {
      console.error("Không thể lấy danh sách ngôn ngữ", err);
    }
  }, []);

  // Dịch văn bản thuần
  const translateText = useCallback(async (payload) => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const data = await apiTranslateText(payload);
      setResult(data);
      setSuccess("Dịch văn bản thành công.");
      return { success: true, data };
    } catch (err) {
      const msg = err.response?.data?.detail || "Dịch văn bản thất bại.";
      setError(msg);
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  }, []);

  // Dịch tài liệu
  const translateDocument = useCallback(async (payload) => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const data = await apiTranslateDocument(payload);
      setResult(data);
      setSuccess("Dịch tài liệu thành công.");
      return { success: true, data };
    } catch (err) {
      const msg = err.response?.data?.detail || "Dịch tài liệu thất bại.";
      setError(msg);
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  }, []);

  // Lấy lịch sử dịch thuật
  const fetchHistory = useCallback(async (params = {}) => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiGetHistory(params);
      setHistory(data.data);
      setTotal(data.total);
      return { success: true, data };
    } catch (err) {
      const msg =
        err.response?.data?.detail || "Không thể tải lịch sử dịch thuật.";
      setError(msg);
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  }, []);

  // Xem chi tiết một bản dịch
  const fetchDetail = useCallback(async (translationId) => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiGetTranslationDetail(translationId);
      setDetail(data);
      return { success: true, data };
    } catch (err) {
      const msg =
        err.response?.data?.detail || "Không thể tải chi tiết bản dịch.";
      setError(msg);
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  }, []);

  // Xóa một bản dịch
  const removeTranslation = useCallback(async (translationId) => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const data = await apiDeleteTranslation(translationId);
      setHistory((prev) => prev.filter((t) => t.id !== translationId));
      setTotal((prev) => prev - 1);
      setSuccess(data.message || "Đã xóa bản dịch khỏi lịch sử.");
      return { success: true };
    } catch (err) {
      const msg = err.response?.data?.detail || "Xóa bản dịch thất bại.";
      setError(msg);
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    languages,
    fetchLanguages,
    result,
    history,
    total,
    detail,
    loading,
    error,
    success,
    clearMessages,
    translateText,
    translateDocument,
    fetchHistory,
    fetchDetail,
    removeTranslation,
  };
}
