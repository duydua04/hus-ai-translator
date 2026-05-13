import axiosUser from "./axiosUser";

// Lấy thông tin hồ sơ cá nhân
export const getProfile = async () => {
  const res = await axiosUser.get("/user/profile");
  return res.data;
};

// Cập nhật họ tên và / hoặc ngôn ngữ mặc định (partial update)
export const updateProfile = async (payload) => {
  const res = await axiosUser.patch("/user/profile", payload);
  return res.data;
};

// Đổi mật khẩu khi đang đăng nhập
export const changePassword = async (payload) => {
  const res = await axiosUser.patch("/user/password", payload);
  return res.data;
};
