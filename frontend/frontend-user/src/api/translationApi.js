import axiosUser from "./axiosUser";
import axios from "axios";

// Dịch văn bản thuần
export const translateText = async (payload) => {
  const res = await axiosUser.post("/translate/text", payload);
  return res.data;
};

// Dịch tài liệu đã upload
const getCookie = (name) => {
  const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
  if (match) return match[2];
  return null;
};

export const translateFile = async (formData) => {
  const token = getCookie("access_token_user");
  const response = await axios.post(
    "http://localhost:8000/translate/document",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
        Authorization: `Bearer ${token}`,
      },
    }
  );
  return response.data;
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
