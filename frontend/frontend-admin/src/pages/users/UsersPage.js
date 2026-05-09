import React from "react";
import UserRow from "./UserRow";
import Pagination from "../../components/common/Pagination";
import { useUsers } from "../../hooks/useUsers";
import "./UsersPage.scss";

export default function UsersPage() {
  const { users, total, loading, filters, setFilters, lockUser, unlockUser } =
    useUsers();

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
            <option value="pending">Chờ xác thực</option>
          </select>
          <select
            className="filter-select"
            onChange={(e) =>
              setFilters((f) => ({ ...f, plan: e.target.value, page: 1 }))
            }
          >
            <option value="">Tất cả gói</option>
            <option value="free">Miễn phí</option>
            <option value="pro">Pro</option>
            <option value="enterprise">Doanh nghiệp</option>
          </select>
          <select
            className="filter-select"
            onChange={(e) =>
              setFilters((f) => ({ ...f, sort: e.target.value }))
            }
          >
            <option value="newest">Mới nhất trước</option>
            <option value="oldest">Cũ nhất trước</option>
            <option value="most_active">Hoạt động nhiều</option>
          </select>
        </div>
      </div>

      <div className="data-table">
        <table>
          <colgroup>
            <col style={{ width: "24%" }} />
            <col style={{ width: "10%" }} />
            <col style={{ width: "13%" }} />
            <col style={{ width: "13%" }} />
            <col style={{ width: "12%" }} />
            <col style={{ width: "14%" }} />
          </colgroup>
          <thead>
            <tr>
              <th>Người dùng</th>
              <th>Gói</th>
              <th>Trạng thái</th>
              <th>Ngày đăng ký</th>
              <th>Bản dịch</th>
              <th>Hành động</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="data-table__empty">
                  Đang tải...
                </td>
              </tr>
            ) : users.length === 0 ? (
              <tr>
                <td colSpan={6} className="data-table__empty">
                  Không có dữ liệu
                </td>
              </tr>
            ) : (
              users.map((user) => (
                <UserRow
                  key={user.id}
                  user={user}
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
    </div>
  );
}
