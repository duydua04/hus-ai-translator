import { useState, useEffect } from "react";
import AuthAPI from "../api/AuthAPI";

function useAuth() {
  const [admin, setAdmin] = useState(undefined);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Kiểm tra session khi reload trang
  useEffect(() => {
    const token = sessionStorage.getItem("access_token");
    if (!token) {
      setAdmin(null);
      return;
    }
    AuthAPI.getAdminMe()
      .then((data) => setAdmin(data))
      .catch(() => {
        sessionStorage.removeItem("access_token");
        setAdmin(null);
      });
  }, []);

  const login = async (email, password) => {
    setLoading(true);
    setError(null);
    try {
      // lấy token
      const tokenData = await AuthAPI.adminLogin({ email, password });
      sessionStorage.setItem("access_token", tokenData.access_token);

      // lấy thông tin admin
      const data = await AuthAPI.getAdminMe();
      setAdmin(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Đăng nhập thất bại.");
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await AuthAPI.adminLogout();
    } catch {
    } finally {
      sessionStorage.removeItem("access_token");
      setAdmin(null);
    }
  };

  return { admin, loading, error, login, logout };
}

export default useAuth;
