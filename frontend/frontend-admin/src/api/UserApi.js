import axiosAdmin from "./axiosAdmin";

const UserAPI = {
  // Danh sách người dùng
  getUsers: async ({ page = 1, limit = 20, search, is_active, tier } = {}) => {
    const params = { page, limit };
    if (search !== undefined && search !== "") params.search = search;
    if (is_active !== undefined && is_active !== null)
      params.is_active = is_active;
    if (tier !== undefined && tier !== "") params.tier = tier;

    const res = await axiosAdmin.get("/api/admin/users/", { params });
    return res.data;
  },

  // Chi tiết người dùng
  getUserDetail: async (userId) => {
    const res = await axiosAdmin.get(`/api/admin/users/${userId}`);
    return res.data;
  },

  // Khóa mở khóa tài khoản
  toggleUserStatus: async (userId, is_active) => {
    const res = await axiosAdmin.patch(
      `/api/admin/users/${userId}/status`,
      null,
      {
        params: { is_active },
      }
    );
    return res.data;
  },

  // Xóa người dùng
  deleteUser: async (userId) => {
    const res = await axiosAdmin.delete(`/api/admin/users/${userId}`);
    return res.data;
  },
};

export default UserAPI;
