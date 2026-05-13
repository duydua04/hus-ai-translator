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

  // Lấy thông tin hồ sơ khi mount
  useEffect(() => {
    const fetchProfile = async () => {
      setLoading(true);
      try {
        const data = await getProfile();
        setProfile(data);
      } catch (err) {
        setError(
          err.response?.data?.detail || "Không thể tải thông tin hồ sơ."
        );
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  // Cập nhật họ tên / ngôn ngữ
  const updateProfile = useCallback(async (payload) => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const data = await apiUpdateProfile(payload);
      setProfile(data);
      setSuccess("Cập nhật hồ sơ thành công.");
      return { success: true };
    } catch (err) {
      const msg = err.response?.data?.detail || "Cập nhật thất bại.";
      setError(msg);
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  }, []);

  // Đổi mật khẩu
  const changePassword = useCallback(async (payload) => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const data = await apiChangePassword(payload);
      setSuccess(data.message || "Đổi mật khẩu thành công.");
      return { success: true };
    } catch (err) {
      const msg = err.response?.data?.detail || "Đổi mật khẩu thất bại.";
      setError(msg);
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  }, []);

  // Xoá thông báo sau một khoảng thời gian
  const clearMessages = useCallback(() => {
    setError(null);
    setSuccess(null);
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
