import axiosAdmin from "./axiosAdmin";

const LanguageAPI = {
  // Admin xem toàn bộ ngôn ngữ
  getAllLanguages: async () => {
    const res = await axiosAdmin.get("/languages/all");
    return res.data;
  },

  // Thêm ngôn ngữ mới
  createLanguage: async (payload) => {
    const res = await axiosAdmin.post("/languages", payload);
    return res.data;
  },

  // Bật ngôn ngữ
  activateLanguage: async (languageId) => {
    const res = await axiosAdmin.patch(`/languages/${languageId}/activate`);
    return res.data;
  },

  // Tắt ngôn ngữ
  deactivateLanguage: async (languageId) => {
    const res = await axiosAdmin.patch(`/languages/${languageId}/deactivate`);
    return res.data;
  },
};

export default LanguageAPI;
