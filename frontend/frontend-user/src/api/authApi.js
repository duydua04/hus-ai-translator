import axiosUser from "./axiosUser";

// Register
export const register = async (payload) => {
  const res = await axiosUser.post("/auth/register", payload);
  return res.data;
};

//Login
export const login = async (payload) => {
  const res = await axiosUser.post("/auth/login", payload);
  return res.data;
};

//Get user's information
export const getMe = async () => {
  const res = await axiosUser.get("/auth/me");
  return res.data;
};

//Logout
export const logout = async () => {
  const res = await axiosUser.post("/auth/logout");
  return res.data;
};

//Refresh token
export const refreshToken = async () => {
  const res = await axiosUser.post("/auth/refresh");
  return res.data;
};

// Forgot password - stage 1 - enter email
export const forgotPassword = async (email) => {
  const res = await axiosUser.post("/auth/forgot-password", { email });
  return res.data;
};

//Verify otp
export const verifyOtp = async (otp) => {
  const res = await axiosUser.post("/auth/verify-otp", { otp });
  return res.data;
};

//Reset password
export const resetPassword = async (payload) => {
  const res = await axiosUser.post("/auth/reset-password", payload);
  return res.data;
};
