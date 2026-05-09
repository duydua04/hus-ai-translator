import axiosAdmin from "./axiosAdmin";

const AuthAPI = {
  // Login
  adminLogin: async (payload) => {
    const res = await axiosAdmin.post("/auth/admin/login", payload);
    return res.data;
  },

  // Logout
  adminLogout: async () => {
    const res = await axiosAdmin.post("/auth/admin/logout");
    return res.data;
  },

  // Infomation
  getAdminMe: async () => {
    const res = await axiosAdmin.get("/auth/admin/me");
    return res.data;
  },
};

export default AuthAPI;
