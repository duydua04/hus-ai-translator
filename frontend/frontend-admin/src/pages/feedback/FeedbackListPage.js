import React, { useEffect } from "react";
import UserCell from "../../components/common/UserCell";
import Badge from "../../components/common/Badge";
import StarRating from "../../components/common/StarRating";
import Pagination from "../../components/common/Pagination";
import { useFeedbacks } from "../../hooks/useFeedback";
import "./FeedbackListPage.scss";

const TABS = [
  { key: "all", label: "Tất cả" },
  { key: "with_correction", label: "Có chỉnh sửa" },
  { key: "no_correction", label: "Không chỉnh sửa" },
];

const STAR_OPTIONS = [5, 4, 3, 2, 1];

export default function FeedbackListPage() {
  const {
    feedbacks,
    total,
    stats,
    loading,
    statsLoading,
    error,
    filters,
    setFilters,
    fetchStats,
    selectedFeedback,
    detailLoading,
    detailError,
    openDetail,
    closeDetail,
    deleteFeedback,
  } = useFeedbacks();

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  // ─── Handlers ─────────────────────────────────────────────────────────────

  const handleTab = (key) => {
    setFilters((f) => ({ ...f, tab: key, page: 1 }));
  };

  const handleSearch = (e) => {
    setFilters((f) => ({ ...f, search: e.target.value, page: 1 }));
  };

  const handleRatingFilter = (e) => {
    setFilters((f) => ({ ...f, rating: e.target.value, page: 1 }));
  };

  const handleDeleteConfirm = (feedbackId) => {
    if (window.confirm("Bạn có chắc muốn xóa feedback này?")) {
      deleteFeedback(feedbackId);
    }
  };

  // ─── Render ───────────────────────────────────────────────────────────────

  const activeTab = filters.tab || "all";

  return (
    <div className="feedback-page">
      {/* ── Stats strip ─────────────────────────────────────────────── */}
      {!statsLoading && stats && (
        <div className="feedback-stats">
          <div className="feedback-stats__card">
            <span className="feedback-stats__label">Tổng feedback</span>
            <span className="feedback-stats__value">
              {stats.totalFeedbacks.toLocaleString()}
            </span>
          </div>
          <div className="feedback-stats__card">
            <span className="feedback-stats__label">Điểm trung bình</span>
            <span className="feedback-stats__value feedback-stats__value--accent">
              {stats.averageRating.toFixed(1)}
              <i className="bx bxs-star" />
            </span>
          </div>
          <div className="feedback-stats__card">
            <span className="feedback-stats__label">Có chỉnh sửa</span>
            <span className="feedback-stats__value">
              {stats.totalWithCorrection.toLocaleString()}
            </span>
          </div>
          <div className="feedback-stats__card feedback-stats__card--dist">
            <span className="feedback-stats__label">Phân phối sao</span>
            <div className="feedback-stats__dist">
              {Object.entries(stats.distribution)
                .sort(([a], [b]) => b - a)
                .map(([star, count]) => (
                  <span key={star} className="dist-chip">
                    {star}★ <b>{count}</b>
                  </span>
                ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Toolbar ─────────────────────────────────────────────────── */}
      <div className="feedback-toolbar">
        <div className="search">
          <i className="bx bx-search search__icon" />
          <input
            className="search__input"
            placeholder="Tìm feedback note..."
            value={filters.search}
            onChange={handleSearch}
          />
        </div>

        <select
          className="filter-select"
          value={filters.rating}
          onChange={handleRatingFilter}
        >
          <option value="">Tất cả sao</option>
          {STAR_OPTIONS.map((s) => (
            <option key={s} value={s}>
              {s} sao
            </option>
          ))}
        </select>

        <div className="tab-bar">
          {TABS.map(({ key, label }) => (
            <button
              key={key}
              className={`tab-bar__item${
                activeTab === key ? " tab-bar__item--active" : ""
              }`}
              onClick={() => handleTab(key)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* ── Error ───────────────────────────────────────────────────── */}
      {error && (
        <div className="feedback-page__error">
          <i className="bx bx-error-circle" /> {error}
        </div>
      )}

      {/* ── Table ───────────────────────────────────────────────────── */}
      <div className="data-table">
        <table>
          <thead>
            <tr>
              <th>Đánh giá</th>
              <th>Nội dung chỉnh sửa</th>
              <th>Ghi chú</th>
              <th>Loại</th>
              <th>Chỉnh sửa</th>
              <th>Thời gian</th>
              <th>Hành động</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={7} className="data-table__empty">
                  <i className="bx bx-loader-alt bx-spin" /> Đang tải...
                </td>
              </tr>
            ) : feedbacks.length === 0 ? (
              <tr>
                <td colSpan={7} className="data-table__empty">
                  Không có feedback nào.
                </td>
              </tr>
            ) : (
              feedbacks.map((fb) => (
                <tr key={fb.id}>
                  <td>
                    <StarRating value={fb.rating} />
                  </td>
                  <td>
                    <div className="feedback-text" title={fb.correctedContent}>
                      {fb.correctedContent || (
                        <span className="feedback-text--empty">Không có</span>
                      )}
                    </div>
                  </td>
                  <td>
                    <div className="feedback-text" title={fb.feedbackNote}>
                      {fb.feedbackNote || (
                        <span className="feedback-text--empty">Không có</span>
                      )}
                    </div>
                  </td>
                  <td>
                    <Badge variant={fb.type}>{fb.typeLabel}</Badge>
                  </td>
                  <td>
                    <Badge
                      variant={fb.correctedContent ? "positive" : "neutral"}
                    >
                      {fb.correctedContent ? "Có" : "Không"}
                    </Badge>
                  </td>
                  <td>
                    <span className="cell-date">{fb.createdAt}</span>
                  </td>
                  <td>
                    <div className="table-actions">
                      <button
                        className="table-action table-action--view"
                        onClick={() => openDetail(fb.id)}
                        title="Xem chi tiết"
                      >
                        <i className="bx bx-show" />
                      </button>
                      <button
                        className="table-action table-action--delete"
                        onClick={() => handleDeleteConfirm(fb.id)}
                        title="Xóa"
                      >
                        <i className="bx bx-trash" />
                      </button>
                    </div>
                  </td>
                </tr>
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

      {/* ── Detail Modal ────────────────────────────────────────────── */}
      {(selectedFeedback || detailLoading || detailError) && (
        <div className="modal-overlay" onClick={closeDetail}>
          <div className="feedback-modal" onClick={(e) => e.stopPropagation()}>
            <div className="feedback-modal__header">
              <h2 className="feedback-modal__title">Chi tiết Feedback</h2>
              <button className="feedback-modal__close" onClick={closeDetail}>
                <i className="bx bx-x" />
              </button>
            </div>

            {detailLoading ? (
              <div className="feedback-modal__state">
                <i className="bx bx-loader-alt bx-spin" /> Đang tải...
              </div>
            ) : detailError ? (
              <div className="feedback-modal__state feedback-modal__state--error">
                <i className="bx bx-error-circle" /> {detailError}
              </div>
            ) : (
              selectedFeedback && (
                <div className="feedback-modal__body">
                  {/* User + rating */}
                  <div className="feedback-modal__user-row">
                    <UserCell
                      initials={selectedFeedback.initials}
                      name={selectedFeedback.name}
                      sub={selectedFeedback.email}
                      avatarBg={selectedFeedback.avatarBg}
                      avatarColor={selectedFeedback.avatarColor}
                      size={36}
                    />
                    <div className="feedback-modal__badges">
                      <StarRating value={selectedFeedback.rating} />
                      <Badge variant={selectedFeedback.type}>
                        {selectedFeedback.typeLabel}
                      </Badge>
                      <Badge variant="neutral">{selectedFeedback.tier}</Badge>
                    </div>
                  </div>

                  {/* Feedback note */}
                  <div className="feedback-modal__section">
                    <span className="feedback-modal__label">Ghi chú</span>
                    <p className="feedback-modal__content">
                      {selectedFeedback.feedbackNote || "Không có ghi chú"}
                    </p>
                  </div>

                  {/* Corrected content */}
                  {selectedFeedback.correctedContent && (
                    <div className="feedback-modal__section">
                      <span className="feedback-modal__label">
                        Nội dung chỉnh sửa
                      </span>
                      <p className="feedback-modal__content">
                        {selectedFeedback.correctedContent}
                      </p>
                    </div>
                  )}

                  {/* Translation context */}
                  {selectedFeedback.translation && (
                    <div className="feedback-modal__translation">
                      <span className="feedback-modal__label">
                        Bản dịch gốc
                      </span>
                      <div className="translation-pair">
                        <div className="translation-pair__col">
                          <span className="translation-pair__lang">Nguồn</span>
                          <p>{selectedFeedback.translation.inputContent}</p>
                        </div>
                        <div className="translation-pair__col">
                          <span className="translation-pair__lang">
                            Kết quả
                          </span>
                          <p>
                            {selectedFeedback.translation.translatedContent}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="feedback-modal__row">
                    <div className="feedback-modal__field">
                      <span className="feedback-modal__label">Thời gian</span>
                      <span className="cell-date">
                        {selectedFeedback.createdAt}
                      </span>
                    </div>
                  </div>

                  <div className="feedback-modal__footer">
                    <button
                      className="btn btn--danger"
                      onClick={() => handleDeleteConfirm(selectedFeedback.id)}
                    >
                      <i className="bx bx-trash" /> Xóa feedback
                    </button>
                  </div>
                </div>
              )
            )}
          </div>
        </div>
      )}
    </div>
  );
}
