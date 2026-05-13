import { useState, useEffect, useCallback } from "react";
import LanguageAPI from "../api/LaguageApi";

function useLanguage() {
  const [languages, setLanguages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Lấy toàn bộ ngôn ngữ
  const fetchLanguages = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await LanguageAPI.getAllLanguages();
      setLanguages(data);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Không thể tải danh sách ngôn ngữ."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLanguages();
  }, [fetchLanguages]);

  // payload: { language_code: "en", language_name: "English" }
  const createLanguage = async (payload) => {
    setLoading(true);
    setError(null);
    try {
      const newLang = await LanguageAPI.createLanguage(payload);
      setLanguages((prev) => [...prev, newLang]);
      return newLang;
    } catch (err) {
      setError(err.response?.data?.detail || "Thêm ngôn ngữ thất bại.");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Bật ngôn ngữ theo id
  const activateLanguage = async (languageId) => {
    setError(null);
    try {
      const updated = await LanguageAPI.activateLanguage(languageId);
      setLanguages((prev) =>
        prev.map((lang) => (lang.language_code === languageId ? updated : lang))
      );
      return updated;
    } catch (err) {
      setError(err.response?.data?.detail || "Bật ngôn ngữ thất bại.");
      throw err;
    }
  };

  // Tắt ngôn ngữ theo id
  const deactivateLanguage = async (languageId) => {
    setError(null);
    try {
      const updated = await LanguageAPI.deactivateLanguage(languageId);
      setLanguages((prev) =>
        prev.map((lang) => (lang.language_code === languageId ? updated : lang))
      );
      return updated;
    } catch (err) {
      setError(err.response?.data?.detail || "Tắt ngôn ngữ thất bại.");
      throw err;
    }
  };

  // Toggle tiện lợi - tự xác định bật hay tắt dựa vào trạng thái hiện tại
  const toggleLanguage = async (languageId, currentIsActive) => {
    return currentIsActive
      ? await deactivateLanguage(languageId)
      : await activateLanguage(languageId);
  };

  return {
    languages,
    loading,
    error,
    fetchLanguages,
    createLanguage,
    activateLanguage,
    deactivateLanguage,
    toggleLanguage,
  };
}

export default useLanguage;
