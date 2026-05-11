import { useState, useEffect, useCallback } from "react";
import UserAPI from "../api/UserApi";

// Chuyển API field → UI field
function normalizeUser(u) {
  return {
    id: u.id,
    name: u.full_name,
    email: u.email,
    initials: u.full_name
      ? u.full_name
          .trim()
          .split(" ")
          .slice(-2)
          .map((w) => w[0])
          .join("")
          .toUpperCase()
      : "?",
    avatarBg: "#e0e7ff",
    avatarColor: "#4f46e5",
    plan: u.tier,
    status: u.is_active ? "active" : "locked",
    joinDate: u.created_at
      ? new Date(u.created_at).toLocaleDateString("vi-VN")
      : "—",
    updatedAt: u.updated_at
      ? new Date(u.updated_at).toLocaleDateString("vi-VN")
      : "—",
    translations: u.total_translations ?? "—",
    feedbacks: u.total_feedbacks ?? "—",
    is_active: u.is_active,
  };
}

export function useUsers() {
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    page: 1,
    limit: 20,
    search: "",
    status: "",
    plan: "",
  });

  // --- Detail modal ---
  const [selectedUser, setSelectedUser] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState(null);

  const buildParams = (f) => {
    const params = { page: f.page, limit: f.limit };
    if (f.search) params.search = f.search;
    if (f.plan) params.tier = f.plan;
    if (f.status === "active") params.is_active = true;
    else if (f.status === "locked") params.is_active = false;
    return params;
  };

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await UserAPI.getUsers(buildParams(filters));
      setUsers((data.data ?? []).map(normalizeUser));
      setTotal(data.total ?? 0);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Không thể tải danh sách người dùng."
      );
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  // Mở modal chi tiết — fetch riêng để lấy total_translations, total_feedbacks
  const openDetail = async (userId) => {
    setSelectedUser(null);
    setDetailError(null);
    setDetailLoading(true);
    try {
      const data = await UserAPI.getUserDetail(userId);
      setSelectedUser(normalizeUser(data));
    } catch (err) {
      setDetailError(
        err.response?.data?.detail || "Không thể tải thông tin người dùng."
      );
    } finally {
      setDetailLoading(false);
    }
  };

  const closeDetail = () => {
    setSelectedUser(null);
    setDetailError(null);
  };

  // Khóa / mở khóa — cập nhật cả list lẫn modal nếu đang mở
  const lockUser = async (userId) => {
    try {
      await UserAPI.toggleUserStatus(userId, false);
      const patch = { is_active: false, status: "locked" };
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, ...patch } : u))
      );
      if (selectedUser?.id === userId)
        setSelectedUser((prev) => ({ ...prev, ...patch }));
    } catch (err) {
      setError(err.response?.data?.detail || "Không thể khóa người dùng.");
    }
  };

  const unlockUser = async (userId) => {
    try {
      await UserAPI.toggleUserStatus(userId, true);
      const patch = { is_active: true, status: "active" };
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, ...patch } : u))
      );
      if (selectedUser?.id === userId)
        setSelectedUser((prev) => ({ ...prev, ...patch }));
    } catch (err) {
      setError(err.response?.data?.detail || "Không thể mở khóa người dùng.");
    }
  };

  // Xóa — đóng modal nếu đang xem user bị xóa
  const deleteUser = async (userId) => {
    try {
      await UserAPI.deleteUser(userId);
      setUsers((prev) => prev.filter((u) => u.id !== userId));
      setTotal((prev) => prev - 1);
      if (selectedUser?.id === userId) closeDetail();
    } catch (err) {
      setError(err.response?.data?.detail || "Không thể xóa người dùng.");
    }
  };

  return {
    users,
    total,
    loading,
    error,
    filters,
    setFilters,
    selectedUser,
    detailLoading,
    detailError,
    openDetail,
    closeDetail,
    lockUser,
    unlockUser,
    deleteUser,
  };
}
