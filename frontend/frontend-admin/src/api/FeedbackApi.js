import axiosAdmin from "./axiosAdmin";

const FeedbackAPI = {
  // Danh sách feedback
  getFeedbacks: async ({
    page = 1,
    limit = 20,
    search,
    rating,
    translation_id,
  } = {}) => {
    const params = {
      limit,
      offset: (page - 1) * limit,
    };
    if (search) params.search = search;
    if (rating !== undefined && rating !== "") params.rating = rating;
    if (translation_id) params.translation_id = translation_id;

    const res = await axiosAdmin.get("/admin/feedback", { params });
    return res.data;
  },

  // Thống kê chất lượng
  getStats: async () => {
    const res = await axiosAdmin.get("/admin/feedback/stats");
    return res.data;
  },

  // Chi tiết feedback
  getFeedbackDetail: async (feedbackId) => {
    const res = await axiosAdmin.get(`/admin/feedback/${feedbackId}`);
    return res.data;
  },

  // Xóa feedback
  deleteFeedback: async (feedbackId) => {
    const res = await axiosAdmin.delete(`/admin/feedback/${feedbackId}`);
    return res.data;
  },
};

export default FeedbackAPI;
