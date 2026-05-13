import React, { useState } from "react";
import UserCell from "../../components/common/UserCell";
import Badge from "../../components/common/Badge";
import StarRating from "../../components/common/StarRating";
import Pagination from "../../components/common/Pagination";
import { useFeedbackList } from "../../hooks/useFeedback";
import "./FeedbackListPage.scss";

const TABS = [
  { key: "all", label: "Tất cả" },
  { key: "pending", label: "Cần xử lý" },
  { key: "resolved", label: "Đã xử lý" },
];

export default function FeedbackListPage() {
  const { feedbacks, total, loading, filters, setFilters } = useFeedbackList();
  const [activeTab, setActiveTab] = useState("all");

  const handleTab = (key) => {
    setActiveTab(key);
    setFilters((f) => ({ ...f, tab: key, page: 1 }));
  };

  return (
    <div className="page page--active" id="page-feedback-list">
      <div className="page__header">
        <div>
          <div className="page__title">Danh sách Feedback</div>
          <div className="page__subtitle">
            {total.toLocaleString()} đánh giá từ người dùng
          </div>
        </div>
        <button className="btn btn--secondary">Xuất CSV</button>
      </div>

      <div className="filter-bar">
        <div className="search">
          <i className="bx bx-search search__icon" />
          <input
            className="search__input"
            placeholder="Tìm nội dung, người dùng..."
            onChange={(e) =>
              setFilters((f) => ({ ...f, search: e.target.value, page: 1 }))
            }
          />
        </div>
        <div className="filter-bar__actions">
          <select
            className="filter-select"
            onChange={(e) =>
              setFilters((f) => ({ ...f, type: e.target.value, page: 1 }))
            }
          >
            <option value="">Tất cả loại</option>
            <option value="positive">Tích cực</option>
            <option value="negative">Tiêu cực</option>
          </select>
          <select
            className="filter-select"
            onChange={(e) =>
              setFilters((f) => ({ ...f, status: e.target.value, page: 1 }))
            }
          >
            <option value="">Tất cả sao</option>
            {[5, 4, 3, 2, 1].map((s) => (
              <option key={s} value={s}>
                {s} sao
              </option>
            ))}
          </select>
          <select
            className="filter-select"
            onChange={(e) =>
              setFilters((f) => ({ ...f, type: e.target.value, page: 1 }))
            }
          >
            <option value="">Tất cả ngôn ngữ</option>
            <option value="">Anh - Việt</option>
            <option value="">Việt - Anh</option>
          </select>
        </div>
      </div>
      <div className="tab-bar" style={{ marginLeft: "auto" }}>
        {TABS.map(({ key, label }) => (
          <div
            key={key}
            className={`tab-bar__item${
              activeTab === key ? " tab-bar__item--active" : ""
            }`}
            onClick={() => handleTab(key)}
          >
            {label}
          </div>
        ))}
      </div>

      <div className="data-table">
        <table>
          <colgroup>
            <col style={{ width: "17%" }} />
            <col style={{ width: "22%" }} />
            <col style={{ width: "9%" }} />
            <col style={{ width: "11%" }} />
            <col style={{ width: "10%" }} />
            <col style={{ width: "14%" }} />
            <col style={{ width: "10%" }} />
            <col style={{ width: "7%" }} />
          </colgroup>
          <thead>
            <tr>
              <th>Người dùng</th>
              <th>Nội dung</th>
              <th>Đánh giá</th>
              <th>Loại</th>
              <th>Ngôn ngữ</th>
              <th>Thời gian</th>
              <th>Trạng thái</th>
              <th>Xem</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={8} className="data-table__empty">
                  Đang tải...
                </td>
              </tr>
            ) : (
              feedbacks.map((fb) => (
                <tr key={fb.id}>
                  <td>
                    <UserCell
                      initials={fb.initials}
                      name={fb.name}
                      avatarBg={fb.avatarBg}
                      avatarColor={fb.avatarColor}
                      size={26}
                    />
                  </td>
                  <td>
                    <div className="feedback-text">{fb.content}</div>
                  </td>
                  <td>
                    <StarRating value={fb.stars} />
                  </td>
                  <td>
                    <Badge variant={fb.type}>{fb.typeLabel}</Badge>
                  </td>
                  <td>
                    <span className="lang-chip">{fb.lang}</span>
                  </td>
                  <td>
                    <span className="cell-date">{fb.date}</span>
                  </td>
                  <td>
                    <Badge
                      variant={
                        fb.status === "resolved" ? "resolved" : "pending-review"
                      }
                      dot
                    >
                      {fb.status === "resolved" ? "Hoàn tất" : "Cần xử lý"}
                    </Badge>
                  </td>
                  <td>
                    <button className="table-action">Xem</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
        <Pagination
          current={filters.page}
          total={total}
          limit={10}
          onChange={(p) => setFilters((f) => ({ ...f, page: p }))}
        />
      </div>
    </div>
  );
}
