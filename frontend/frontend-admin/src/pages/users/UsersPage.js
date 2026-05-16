import React from "react";
import UserRow from "./UserRow";
import UserDetailModal from "./detail/UserDetail";
import Pagination from "../../components/common/Pagination";
import { useUsers } from "../../hooks/useUsers";
import "./UsersPage.scss";

export default function UsersPage() {
  const {
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
  } = useUsers();

  return (
    <div className="page page--active" id="page-users">
      <div className="filter-bar">
        <div className="search">
          <i className="bx bx-search search__icon" />
          <input
            className="search__input"
            placeholder="Tìm theo tên, email..."
            onChange={(e) =>
              setFilters((f) => ({ ...f, search: e.target.value, page: 1 }))
            }
          />
        </div>
        <div className="filter-bar__actions">
          <select
            className="filter-select"
            onChange={(e) =>
              setFilters((f) => ({ ...f, status: e.target.value, page: 1 }))
            }
          >
            <option value="">Tất cả trạng thái</option>
            <option value="active">Đang hoạt động</option>
            <option value="locked">Bị vô hiệu hóa</option>
          </select>
        </div>
      </div>

      <div className="data-table">
        <table>
          <thead>
            <tr>
              <th>Người dùng</th>
              <th>Gói</th>
              <th>Trạng thái</th>
              <th>Ngày đăng ký</th>
              <th>Hành động</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={5} className="data-table__empty">
                  Đang tải...
                </td>
              </tr>
            ) : users.length === 0 ? (
              <tr>
                <td colSpan={5} className="data-table__empty">
                  Không có dữ liệu
                </td>
              </tr>
            ) : (
              users.map((user) => (
                <UserRow
                  key={user.id}
                  user={user}
                  onDetail={openDetail}
                  onLock={lockUser}
                  onUnlock={unlockUser}
                />
              ))
            )}
          </tbody>
        </table>
        <Pagination
          current={filters.page}
          total={total}
          limit={filters.limit}
          onChange={(p) => setFilters((f) => ({ ...f, page: p }))}
        />
      </div>

      {/* Modal chi tiết */}
      <UserDetailModal
        user={selectedUser}
        loading={detailLoading}
        error={detailError}
        onClose={closeDetail}
        onLock={lockUser}
        onUnlock={unlockUser}
        onDelete={deleteUser}
      />
    </div>
  );
}
