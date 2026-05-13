import { useState, useEffect, useCallback } from "react";
import {
  getMe,
  login as apiLogin,
  logout as apiLogout,
  register as apiRegister,
} from "../api/authApi";

export default function useAuth() {
  const [user, setUser] = useState(undefined);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const checkSession = async () => {
      const token = sessionStorage.getItem("access_token_user");
      if (!token) {
        setUser(null);
        return;
      }
      try {
        const data = await getMe();
        setUser(data);
      } catch {
        setUser(null);
        sessionStorage.removeItem("access_token_user");
      }
    };
    checkSession();
  }, []);

  // Login
  const login = useCallback(async (payload) => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiLogin(payload);
      if (data.access_token) {
        sessionStorage.setItem("access_token_user", data.access_token);
      }
      const me = await getMe();
      setUser(me);
      return { success: true };
    } catch (err) {
      const msg = err.response?.data?.detail || "Đăng nhập thất bại.";
      setError(msg);
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  }, []);

  // Register
  const register = useCallback(async (payload) => {
    setLoading(true);
    setError(null);
    try {
      await apiRegister(payload);
      return { success: true };
    } catch (err) {
      const msg = err.response?.data?.detail || "Đăng ký thất bại.";
      setError(msg);
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  }, []);

  // Logout
  const logout = useCallback(async () => {
    setLoading(true);
    try {
      await apiLogout();
    } finally {
      sessionStorage.removeItem("access_token_user");
      setUser(null);
      setLoading(false);
    }
  }, []);

  return { user, loading, error, login, logout, register };
}
