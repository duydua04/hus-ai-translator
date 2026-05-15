import axiosAdmin from "./axiosAdmin";

const DashboardAPI = {
  // Toàn bộ dashboard (gộp)
  getFullDashboard: async () => {
    const res = await axiosAdmin.get("/admin/dashboard");
    return res.data;
  },

  // Tổng quan
  getOverview: async () => {
    const res = await axiosAdmin.get("/admin/dashboard/overview");
    return res.data;
  },

  // Biểu đồ theo tuần
  getWeeklyChart: async () => {
    const res = await axiosAdmin.get("/admin/dashboard/charts/weekly");
    return res.data;
  },

  // Biểu đồ theo giờ
  getHourlyChart: async () => {
    const res = await axiosAdmin.get("/admin/dashboard/charts/hourly");
    return res.data;
  },

  // Phân phối đánh giá
  getRatingDistribution: async () => {
    const res = await axiosAdmin.get("/admin/dashboard/ratings");
    return res.data;
  },

  // Thống kê hướng dịch
  getDirectionStats: async () => {
    const res = await axiosAdmin.get("/admin/dashboard/directions");
    return res.data;
  },

  // Người dùng hoạt động gần đây
  getRecentUsers: async () => {
    const res = await axiosAdmin.get("/admin/dashboard/recent-users");
    return res.data;
  },

  // Feedback gần đây
  getRecentFeedbacks: async () => {
    const res = await axiosAdmin.get("/admin/dashboard/recent-feedbacks");
    return res.data;
  },
};

export default DashboardAPI;
