import axiosUser from "./axiosUser";

// Dịch văn bản thuần
export const translateText = async (payload) => {
  const res = await axiosUser.post("/translate/text", payload);
  return res.data;
};

// Dịch tài liệu đã upload
export const translateFile = async (payload) => {
  const res = await axiosUser.post("/translate/document", payload);
  return res.data;
};

// Lấy lịch sử dịch thuật
export const getHistory = async (params = {}) => {
  const res = await axiosUser.get("/translate/history", { params });
  return res.data;
};

// Xem chi tiết một bản dịch
export const getTranslationDetail = async (translationId) => {
  const res = await axiosUser.get(`/translate/${translationId}`);
  return res.data;
};

// Xóa một bản dịch khỏi lịch sử
export const deleteTranslation = async (translationId) => {
  const res = await axiosUser.delete(`/translate/${translationId}`);
  return res.data;
};

// Lấy danh sách ngôn ngữ
export const getLanguage = async () => {
  const response = await axiosUser.get("/languages");
  return response.data;
};

export const submitContact = async (payload) => {
  const res = await axiosUser.post("/contact", payload);
  return res.data;
};
