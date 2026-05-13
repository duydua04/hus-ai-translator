import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const axiosUser = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

axiosUser.interceptors.request.use((config) => {
  if (!(config.data instanceof FormData)) {
    config.headers["Content-Type"] = "application/json";
  }

  const token = sessionStorage.getItem("access_token_user");
  if (token) {
    config.headers["Authorization"] = `Bearer ${token}`;
  }

  return config;
});

axiosUser.interceptors.response.use(
  (response) => response,

  async (error) => {
    const original = error.config;

    if (original.url?.endsWith("/auth/refresh")) {
      sessionStorage.removeItem("access_token_user");
      window.location.replace("/login");
      return Promise.reject(error);
    }

    if (original.url?.endsWith("/auth/logout")) {
      return Promise.reject(error);
    }

    if (original.url?.endsWith("/auth/me")) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        const res = await axiosUser.post("/auth/refresh");
        if (res.data?.access_token) {
          sessionStorage.setItem("access_token_user", res.data.access_token);
        }

        return axiosUser(original);
      } catch {
        sessionStorage.removeItem("access_token_user");
        window.location.replace("/login");
      }
    }

    return Promise.reject(error);
  }
);

export default axiosUser;
