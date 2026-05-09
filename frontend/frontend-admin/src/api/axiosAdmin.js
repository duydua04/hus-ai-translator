import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const axiosAdmin = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});


axiosAdmin.interceptors.request.use((config) => {
  if (!(config.data instanceof FormData)) {
    config.headers["Content-Type"] = "application/json";
  }

  const token = sessionStorage.getItem("access_token");
  if (token) {
    config.headers["Authorization"] = `Bearer ${token}`;
  }

  return config;
});

axiosAdmin.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;

    if (original.url?.endsWith("/auth/admin/refresh")) {
      sessionStorage.removeItem("access_token");
      window.location.replace("/login");
      return Promise.reject(error);
    }

    if (original.url?.endsWith("/auth/admin/logout")) {
      return Promise.reject(error);
    }

    if (original.url?.endsWith("/auth/admin/me")) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        const res = await axiosAdmin.post("/auth/admin/refresh");
        if (res.data?.access_token) {
          sessionStorage.setItem("access_token", res.data.access_token);
        }
        return axiosAdmin(original);
      } catch {
        sessionStorage.removeItem("access_token");
        window.location.replace("/login");
      }
    }

    return Promise.reject(error);
  }
);

export default axiosAdmin;
