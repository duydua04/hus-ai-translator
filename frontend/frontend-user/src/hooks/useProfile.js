import { useState, useEffect, useCallback } from "react";
import {
  getProfile,
  updateProfile as apiUpdateProfile,
  changePassword as apiChangePassword,
} from "../api/profileApi";

export default function useProfile() {
  const [profile, setProfile] = useState(null);
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

  useEffect(() => {
    const fetchProfile = async () => {
      setLoading(true);
      try {
        const data = await getProfile();
        setProfile(data);
      } catch (err) {
        showError(
          err.response?.data?.detail || "Không thể tải thông tin hồ sơ."
        );
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const updateProfile = useCallback(async (payload) => {
    setLoading(true);
    clearMessages();
    try {
      const data = await apiUpdateProfile(payload);
      setProfile(data);
      showSuccess("Cập nhật hồ sơ thành công.");
      return { success: true };
    } catch (err) {
      const msg = err.response?.data?.detail || "Cập nhật thất bại.";
      showError(msg);
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  }, []);

  const changePassword = useCallback(async (payload) => {
    setLoading(true);
    clearMessages();
    try {
      const data = await apiChangePassword(payload);
      showSuccess(data.message || "Đổi mật khẩu thành công.");
      return { success: true };
    } catch (err) {
      const msg = err.response?.data?.detail || "Đổi mật khẩu thất bại.";
      showError(msg);
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    profile,
    loading,
    error,
    success,
    updateProfile,
    changePassword,
    clearMessages,
  };
}
