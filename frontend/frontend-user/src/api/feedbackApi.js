import axiosUser from "./axiosUser";

// Tạo feedback cho bản dịch
export const createFeedback = async (payload) => {
  const res = await axiosUser.post("/api/user/feedbacks", payload);
  return res.data;
};

// Lấy danh sách feedback
export const getMyFeedbacks = async (params = {}) => {
  const res = await axiosUser.get("/api/user/feedbacks", { params });
  return res.data;
};

// Lấy feedback theo translation_id
export const getFeedbackByTranslation = async (translationId) => {
  const res = await axiosUser.get(
    `/api/user/feedbacks/by-translation/${translationId}`
  );
  return res.data;
};

// Lấy chi tiết một feedback
export const getFeedbackDetail = async (feedbackId) => {
  const res = await axiosUser.get(`/api/user/feedbacks/${feedbackId}`);
  return res.data;
};

// Cập nhật feedback
export const updateFeedback = async (feedbackId, payload) => {
  const res = await axiosUser.put(`/api/user/feedbacks/${feedbackId}`, payload);
  return res.data;
};

// Xóa feedback
export const deleteFeedback = async (feedbackId) => {
  const res = await axiosUser.delete(`/api/user/feedbacks/${feedbackId}`);
  return res.data;
};
