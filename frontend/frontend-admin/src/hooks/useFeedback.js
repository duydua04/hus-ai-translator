import { useState, useEffect, useCallback } from "react";
import { feedbackApi } from "../api/FeedbackApi";

const MOCK_DASHBOARD = {
  metrics: [
    {
      id: "total",
      label: "Tổng feedback",
      value: "1.284",
      trend: "↑ 12% so với tháng trước",
      trendType: "up",
      color: "green",
      icon: "bxs-bar-chart-square",
    },
    {
      id: "avg",
      label: "Điểm trung bình",
      value: "4.3",
      trend: "↑ 0.2 điểm cải thiện",
      trendType: "up",
      color: "blue",
      icon: "bx-star",
    },
    {
      id: "negative",
      label: "Phản hồi tiêu cực",
      value: "97",
      trend: "↑ 4% cần xử lý",
      trendType: "down",
      color: "red",
      icon: "bx-sad",
    },
    {
      id: "satisfaction",
      label: "Tỷ lệ hài lòng",
      value: "92%",
      trend: "↑ 3% so với tháng trước",
      trendType: "up",
      color: "amber",
      icon: "bx-smile",
    },
  ],
  ratingDistribution: [
    {
      star: 5,
      count: 687,
      pct: 68,
      gradient: "linear-gradient(90deg,#276830,#4a9e55)",
    },
    {
      star: 4,
      count: 213,
      pct: 21,
      gradient: "linear-gradient(90deg,#4a9e55,#6bbd77)",
    },
    { star: 3, count: 61, pct: 6, gradient: "#b4b2a9" },
    { star: 2, count: 38, pct: 4, gradient: "#ef9f27" },
    { star: 1, count: 21, pct: 2, gradient: "#e24b4a" },
  ],
  categoryDistribution: [
    { label: "Dịch thuật tốt", pct: "58%", color: "#33823c" },
    { label: "Sai nghĩa", pct: "22%", color: "#ef9f27" },
    { label: "Lỗi kỹ thuật", pct: "12%", color: "#e24b4a" },
    { label: "Khác", pct: "8%", color: "#c0d0cc" },
  ],
};

const MOCK_FEEDBACK_LIST = [
  {
    id: 1,
    initials: "NH",
    name: "Nguyễn Hải",
    avatarBg: "#c8edd0",
    avatarColor: "#163d1a",
    content: "Bản dịch rất chính xác, tự nhiên!",
    stars: 5,
    type: "positive",
    typeLabel: "Tốt",
    lang: "VI→EN",
    date: "hôm nay, 09:14",
    status: "resolved",
  },
  {
    id: 2,
    initials: "PT",
    name: "Phan Tuấn",
    avatarBg: "#fdecea",
    avatarColor: "#7b241c",
    content: "Dịch sai nghĩa câu cuối đoạn văn",
    stars: 2,
    type: "negative",
    typeLabel: "Sai nghĩa",
    lang: "EN→VI",
    date: "hôm nay, 07:52",
    status: "pending",
  },
  {
    id: 3,
    initials: "TL",
    name: "Trần Lan",
    avatarBg: "#c8edd0",
    avatarColor: "#0d2d12",
    content: "Giao diện dễ dùng, tốc độ nhanh",
    stars: 4,
    type: "positive",
    typeLabel: "Tốt",
    lang: "VI→ZH",
    date: "hôm qua, 18:33",
    status: "resolved",
  },
  {
    id: 4,
    initials: "BK",
    name: "Bùi Khoa",
    avatarBg: "#ede7f6",
    avatarColor: "#4527a0",
    content: "Bị lỗi timeout khi upload file dài",
    stars: 1,
    type: "negative",
    typeLabel: "Lỗi KT",
    lang: "JA→VI",
    date: "hôm qua, 14:10",
    status: "pending",
  },
  {
    id: 5,
    initials: "VT",
    name: "Vũ Thảo",
    avatarBg: "#fef3e2",
    avatarColor: "#b7640a",
    content: "Rất hài lòng với bản dịch chuyên ngành",
    stars: 5,
    type: "positive",
    typeLabel: "Tốt",
    lang: "EN→VI",
    date: "28/11/2025",
    status: "resolved",
  },
];

export function useFeedbackDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [period, setPeriod] = useState("month");

  useEffect(() => {
    setLoading(true);
    // TODO: feedbackApi.getDashboard(period).then(setData)
    setTimeout(() => {
      setData(MOCK_DASHBOARD);
      setLoading(false);
    }, 300);
  }, [period]);

  return { data, loading, period, setPeriod };
}

export function useFeedbackList() {
  const [feedbacks, setFeedbacks] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    page: 1,
    search: "",
    type: "",
    tab: "all",
  });

  const fetchList = useCallback(async () => {
    setLoading(true);
    // TODO: feedbackApi.getList(filters).then(res => { setFeedbacks(res.data); setTotal(res.total); })
    await new Promise((r) => setTimeout(r, 300));
    setFeedbacks(MOCK_FEEDBACK_LIST);
    setTotal(1284);
    setLoading(false);
  }, [filters]);

  useEffect(() => {
    fetchList();
  }, [fetchList]);

  return { feedbacks, total, loading, filters, setFilters };
}
