import { useState, useEffect, useCallback } from "react";
import { userApi } from "../api/UserApi";

const MOCK_USERS = [
  {
    id: 1,
    initials: "NH",
    name: "Nguyễn Hải",
    email: "nguyenhai@email.com",
    avatarBg: "#c8edd0",
    avatarColor: "#163d1a",
    plan: "pro",
    status: "active",
    joinDate: "12/03/2025",
    translations: "1.240",
  },
  {
    id: 2,
    initials: "TL",
    name: "Trần Lan",
    email: "tran.lan@gmail.com",
    avatarBg: "#fef3e2",
    avatarColor: "#b7640a",
    plan: "free",
    status: "active",
    joinDate: "05/07/2025",
    translations: "87",
  },
  {
    id: 3,
    initials: "PD",
    name: "Phạm Đức",
    email: "pham.duc@work.vn",
    avatarBg: "#e6f0fb",
    avatarColor: "#1a5fa8",
    plan: "enterprise",
    status: "locked",
    joinDate: "22/01/2025",
    translations: "3.871",
  },
  {
    id: 4,
    initials: "LM",
    name: "Lê Minh",
    email: "leminh99@yahoo.com",
    avatarBg: "#f5eef8",
    avatarColor: "#6c3483",
    plan: "free",
    status: "active",
    joinDate: "30/09/2025",
    translations: "34",
  },
  {
    id: 5,
    initials: "VT",
    name: "Vũ Thảo",
    email: "vuthao@company.com",
    avatarBg: "#fdecea",
    avatarColor: "#c0392b",
    plan: "pro",
    status: "pending",
    joinDate: "14/11/2025",
    translations: "12",
  },
  {
    id: 6,
    initials: "BK",
    name: "Bùi Khoa",
    email: "buikhoa@edu.vn",
    avatarBg: "#c8edd0",
    avatarColor: "#0d2d12",
    plan: "enterprise",
    status: "active",
    joinDate: "18/08/2024",
    translations: "9.102",
  },
];

export function useUsers() {
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    page: 1,
    limit: 6,
    status: "",
    plan: "",
    sort: "",
  });

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // TODO: Thay bằng userApi.getAll(filters) khi có backend
      await new Promise((r) => setTimeout(r, 300));
      setUsers(MOCK_USERS);
      setTotal(156);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const lockUser = async (userId) => {
    // await userApi.lockUser(userId);
    setUsers((prev) =>
      prev.map((u) => (u.id === userId ? { ...u, status: "locked" } : u))
    );
  };

  const unlockUser = async (userId) => {
    // await userApi.unlockUser(userId);
    setUsers((prev) =>
      prev.map((u) => (u.id === userId ? { ...u, status: "active" } : u))
    );
  };

  return {
    users,
    total,
    loading,
    error,
    filters,
    setFilters,
    lockUser,
    unlockUser,
  };
}
