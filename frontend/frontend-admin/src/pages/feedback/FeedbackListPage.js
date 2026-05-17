import React, { useEffect, useState } from "react";
import UserCell from "../../components/common/UserCell";
import Badge from "../../components/common/Badge";
import Pagination from "../../components/common/Pagination";
import { useFeedbacks } from "../../hooks/useFeedback";
import "./FeedbackListPage.scss";

const STAR_OPTIONS = [5, 4, 3, 2, 1];

function StarRating({ value }) {
  return (
    <div className="star-rating" aria-label={`${value} sao`}>
      {[1, 2, 3, 4, 5].map((s) => (
        <i key={s} className={`bx ${s <= value ? "bxs-star" : "bx-star"}`} />
      ))}
    </div>
  );
}

function ConfirmModal({ onConfirm, onCancel }) {
  return (
    <div className="modal-overlay modal-overlay--confirm" onClick={onCancel}>
      <div className="confirm-modal" onClick={(e) => e.stopPropagation()}>
        <div className="confirm-modal__icon">
          <i className="bx bx-trash" />
        </div>
        <h3 className="confirm-modal__title">Xóa feedback?</h3>
        <p className="confirm-modal__desc">
          Hành động này không thể hoàn tác. Feedback sẽ bị xóa vĩnh viễn.
        </p>
        <div className="confirm-modal__actions">
          <button className="btn btn--ghost" onClick={onCancel}>
            Hủy
          </button>
          <button className="btn btn--danger" onClick={onConfirm}>
            <i className="bx bx-trash" /> Xóa
          </button>
        </div>
      </div>
    </div>
  );
}

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

  const [pendingDeleteId, setPendingDeleteId] = useState(null);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  const handleDeleteConfirm = (feedbackId) => {
    setPendingDeleteId(feedbackId);
  };

  const handleDeleteExecute = () => {
    deleteFeedback(pendingDeleteId);
    setPendingDeleteId(null);
  };

  const handleDeleteCancel = () => {
    setPendingDeleteId(null);
  };

  return (
    <div className="page page--active" id="page-feedback">
      {/* Stats */}
      {!statsLoading && stats && (
        <div className="stats-strip">
          <div className="stats-card">
            <i className="bx bx-message-square-detail stats-card__icon stats-card__icon--blue" />
            <div className="stats-card__body">
              <span className="stats-card__label">Tổng feedback</span>
              <span className="stats-card__value">
                {stats.totalFeedbacks.toLocaleString()}
              </span>
            </div>
          </div>
          <div className="stats-card">
            <i className="bx bxs-star stats-card__icon stats-card__icon--amber" />
            <div className="stats-card__body">
              <span className="stats-card__label">Điểm trung bình</span>
              <span className="stats-card__value stats-card__value--amber">
                {stats.averageRating.toFixed(1)}
              </span>
            </div>
          </div>
          <div className="stats-card">
            <i className="bx bx-edit-alt stats-card__icon stats-card__icon--green" />
            <div className="stats-card__body">
              <span className="stats-card__label">Có chỉnh sửa</span>
              <span className="stats-card__value">
                {stats.totalWithCorrection.toLocaleString()}
              </span>
            </div>
          </div>
          <div className="stats-card stats-card--dist">
            <i className="bx bx-bar-chart-alt-2 stats-card__icon stats-card__icon--purple" />
            <div className="stats-card__body">
              <span className="stats-card__label">Phân phối sao</span>
              <div className="stats-card__dist">
                {[5, 4, 3, 2, 1].map((star) => {
                  const key = `${star}_star`;
                  const count = stats.distribution[key] ?? 0;
                  const maxCount = Math.max(
                    ...Object.values(stats.distribution),
                    1
                  );
                  return (
                    <div className="dist-row" key={star}>
                      <span className="dist-row__star">
                        {star}
                        <i
                          className="bx bxs-star"
                          style={{ color: "#f9c74f" }}
                        />
                      </span>
                      <div className="dist-row__track">
                        <div
                          className="dist-row__fill"
                          style={{ width: `${(count / maxCount) * 100}%` }}
                        />
                      </div>
                      <span className="dist-row__count">{count}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filter bar */}
      <div className="filter-bar">
        <div className="filter-bar__actions">
          <select
            className="filter-select"
            value={filters.rating}
            onChange={(e) =>
              setFilters((f) => ({ ...f, rating: e.target.value, page: 1 }))
            }
          >
            <option value="">Tất cả sao</option>
            {STAR_OPTIONS.map((s) => (
              <option key={s} value={s}>
                {s} sao
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="page-error">
          <i className="bx bx-error-circle" /> {error}
        </div>
      )}

      {/* Table */}
      <div className="data-table">
        <table>
          <colgroup>
            <col />
            <col />
            <col />
            <col />
            <col />
            <col />
            <col />
          </colgroup>
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
                    <div className="cell-truncate" title={fb.correctedContent}>
                      {fb.correctedContent || (
                        <span className="cell-empty">Không có</span>
                      )}
                    </div>
                  </td>
                  <td>
                    <div className="cell-truncate" title={fb.feedbackNote}>
                      {fb.feedbackNote || (
                        <span className="cell-empty">Không có</span>
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
                    <button
                      className="table-action"
                      onClick={() => openDetail(fb.id)}
                      title="Xem chi tiết"
                    >
                      <i className="bx bx-show" />
                    </button>
                    <button
                      className="table-action table-action--delete"
                      style={{ marginLeft: 4 }}
                      onClick={() => handleDeleteConfirm(fb.id)}
                      title="Xóa"
                    >
                      <i className="bx bx-trash" />
                    </button>
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

      {/* Detail Modal */}
      {(selectedFeedback || detailLoading || detailError) && (
        <div className="modal-overlay" onClick={closeDetail}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal__header">
              <h2 className="modal__title">Chi tiết Feedback</h2>
              <button className="modal__close" onClick={closeDetail}>
                <i className="bx bx-x" />
              </button>
            </div>
            {detailLoading ? (
              <div className="modal__state">
                <i className="bx bx-loader-alt bx-spin" /> Đang tải...
              </div>
            ) : detailError ? (
              <div className="modal__state modal__state--error">
                <i className="bx bx-error-circle" /> {detailError}
              </div>
            ) : (
              selectedFeedback && (
                <div className="modal__body">
                  <div className="modal__user-row">
                    <UserCell
                      initials={selectedFeedback.initials}
                      name={selectedFeedback.name}
                      sub={selectedFeedback.email}
                      avatarBg={selectedFeedback.avatarBg}
                      avatarColor={selectedFeedback.avatarColor}
                      size={36}
                    />
                    <div className="modal__badges">
                      <StarRating value={selectedFeedback.rating} />
                      <Badge variant={selectedFeedback.type}>
                        {selectedFeedback.typeLabel}
                      </Badge>
                      <Badge variant="neutral">{selectedFeedback.tier}</Badge>
                    </div>
                  </div>
                  <div className="modal__section">
                    <span className="modal__label">Ghi chú</span>
                    <p className="modal__content">
                      {selectedFeedback.feedbackNote || "Không có ghi chú"}
                    </p>
                  </div>
                  {selectedFeedback.correctedContent && (
                    <div className="modal__section">
                      <span className="modal__label">Nội dung chỉnh sửa</span>
                      <p className="modal__content">
                        {selectedFeedback.correctedContent}
                      </p>
                    </div>
                  )}
                  {selectedFeedback.translation && (
                    <div className="modal__section">
                      <span className="modal__label">Bản dịch gốc</span>
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
                  <div className="modal__meta">
                    <span className="modal__label">Thời gian</span>
                    <span className="cell-date">
                      {selectedFeedback.createdAt}
                    </span>
                  </div>
                  <div className="modal__footer">
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

      {/* Confirm Delete Modal */}
      {pendingDeleteId && (
        <ConfirmModal
          onConfirm={handleDeleteExecute}
          onCancel={handleDeleteCancel}
        />
      )}
    </div>
  );
}
