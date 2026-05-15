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

  const showError = useCallback((msg) => {
    setError(msg);
    setTimeout(() => setError(null), 3000);
  }, []);

  const showSuccess = useCallback((msg) => {
    setSuccess(msg);
    setTimeout(() => setSuccess(null), 3000);
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
    clearMessages();
    try {
      const data = await apiTranslateText(payload);
      setResult(data);
      showSuccess("Dịch văn bản thành công.");
      return { success: true, data };
    } catch (err) {
      const msg = err.response?.data?.detail || "Dịch văn bản thất bại.";
      showError(msg);
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  }, []);

  // Dịch tài liệu
  const translateDocument = useCallback(async (payload) => {
    setLoading(true);
    clearMessages();
    try {
      const formData = new FormData();

      formData.append("input_file_id", payload.file);
      formData.append("source_lang_id", payload.source_lang_id);
      formData.append("target_lang_id", payload.target_lang_id);
      formData.append("llm_model", payload.llm_model);

      const data = await apiTranslateDocument(formData);

      setResult(data);
      showSuccess("Dịch tài liệu thành công.");
      return { success: true, data };
    } catch (err) {
      console.error("Chi tiết lỗi:", err);

      let errorMsg = "Dịch tài liệu thất bại.";

      if (err.response) {
        errorMsg =
          err.response.data?.detail || JSON.stringify(err.response.data);
      } else if (err.request) {
        errorMsg =
          "Không thể kết nối đến máy chủ. Vui lòng kiểm tra CORS hoặc Server.";
      } else {
        errorMsg = err.message;
      }

      showError(errorMsg);
      return { success: false, message: errorMsg };
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
      showError(msg);
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
      showError(msg);
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  }, []);

  // Xóa một bản dịch
  const removeTranslation = useCallback(async (translationId) => {
    setLoading(true);
    clearMessages();
    try {
      const data = await apiDeleteTranslation(translationId);
      setHistory((prev) => prev.filter((t) => t.id !== translationId));
      setTotal((prev) => prev - 1);
      showSuccess(data.message || "Đã xóa bản dịch khỏi lịch sử.");
      return { success: true };
    } catch (err) {
      const msg = err.response?.data?.detail || "Xóa bản dịch thất bại.";
      showError(msg);
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
