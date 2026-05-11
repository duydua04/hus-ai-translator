import React from "react";
import UserCell from "../../../components/common/UserCell";
import Badge from "../../../components/common/Badge";
import "./UserDetail.scss";

const PLAN_MAP = {
  pro: { variant: "pro", label: "Pro" },
  free: { variant: "free", label: "Miễn phí" },
  enterprise: { variant: "enterprise", label: "Doanh nghiệp" },
};

export default function UserDetailModal({
  user, // normalized user object | null
  loading,
  error,
  onClose,
  onLock,
  onUnlock,
  onDelete,
}) {
  if (!user && !loading && !error) return null;

  const plan = PLAN_MAP[user?.plan] || {};
  const isLocked = user?.status === "locked";

  const handleToggleStatus = () => {
    if (isLocked) onUnlock(user.id);
    else onLock(user.id);
  };

  const handleDelete = () => {
    if (
      window.confirm(
        `Xóa tài khoản "${user.name}"? Hành động này không thể hoàn tác.`
      )
    ) {
      onDelete(user.id);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal__header">
          <h3 className="modal__title">Chi tiết người dùng</h3>
          <button className="modal__close" onClick={onClose}>
            <i className="bx bx-x" />
          </button>
        </div>

        {/* Body */}
        <div className="modal__body">
          {loading && <p className="modal__state">Đang tải...</p>}
          {error && <p className="modal__state modal__state--error">{error}</p>}

          {user && (
            <>
              {/* Avatar + tên */}
              <div className="modal__user-header">
                <UserCell
                  initials={user.initials}
                  name={user.name}
                  email={user.email}
                  avatarBg={user.avatarBg}
                  avatarColor={user.avatarColor}
                  size={40}
                />
                <Badge
                  variant={user.status === "locked" ? "inactive" : "active"}
                  dot
                >
                  {isLocked ? "Bị khóa" : "Hoạt động"}
                </Badge>
              </div>

              {/* Thông tin */}
              <dl className="modal__info">
                <div className="modal__info-row">
                  <dt>Gói dịch vụ</dt>
                  <dd>
                    <Badge variant={plan.variant}>
                      {plan.label || user.plan}
                    </Badge>
                  </dd>
                </div>
                <div className="modal__info-row">
                  <dt>Ngày đăng ký</dt>
                  <dd>{user.joinDate}</dd>
                </div>
                <div className="modal__info-row">
                  <dt>Cập nhật lần cuối</dt>
                  <dd>{user.updatedAt}</dd>
                </div>
                <div className="modal__info-row">
                  <dt>Tổng bản dịch</dt>
                  <dd>{user.translations}</dd>
                </div>
                <div className="modal__info-row">
                  <dt>Tổng phản hồi</dt>
                  <dd>{user.feedbacks}</dd>
                </div>
              </dl>
            </>
          )}
        </div>

        {/* Footer actions */}
        {user && (
          <div className="modal__footer">
            <button
              className={`btn ${isLocked ? "btn--primary" : "btn--warning"}`}
              onClick={handleToggleStatus}
            >
              {isLocked ? "Mở khóa" : "Khóa tài khoản"}
            </button>
            <button className="btn btn--danger" onClick={handleDelete}>
              Xóa người dùng
            </button>
            <button className="btn btn--ghost" onClick={onClose}>
              Đóng
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
