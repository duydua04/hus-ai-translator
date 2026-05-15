import React from "react";
import UserCell from "../../components/common/UserCell";
import Badge from "../../components/common/Badge";

const PLAN_MAP = {
  pro: { variant: "pro", label: "Pro" },
  free: { variant: "free", label: "Miễn phí" },
  enterprise: { variant: "enterprise", label: "Doanh nghiệp" },
};

const STATUS_MAP = {
  active: { variant: "active", dot: true, label: "Hoạt động" },
  locked: { variant: "inactive", dot: true, label: "Bị khóa" },
};

export default function UserRow({ user, onDetail, onLock, onUnlock }) {
  const plan = PLAN_MAP[user.plan] || {};
  const status = STATUS_MAP[user.status] || {};

  return (
    <tr>
      <td>
        <UserCell
          initials={user.initials}
          name={user.name}
          email={user.email}
          avatarBg={user.avatarBg}
          avatarColor={user.avatarColor}
        />
      </td>
      <td>
        <Badge variant={plan.variant}>{plan.label}</Badge>
      </td>
      <td>
        <Badge variant={status.variant} dot={status.dot}>
          {status.label}
        </Badge>
      </td>
      <td>
        <span className="cell-date">{user.joinDate}</span>
      </td>
      <td>
        <button
          className="table-action"
          onClick={() => onDetail(user.id)}
          title="Xem chi tiết"
        >
          <i className="bx bx-show" />
        </button>
        {user.status === "locked" ? (
          <button
            className="table-action table-action--unlock"
            style={{ marginLeft: 4 }}
            onClick={() => onUnlock(user.id)}
            title="Mở khóa"
          >
            <i className="bx bx-lock-open" />
          </button>
        ) : (
          <button
            className="table-action table-action--lock"
            style={{ marginLeft: 4 }}
            onClick={() => onLock(user.id)}
            title="Khóa"
          >
            <i className="bx bx-lock" />
          </button>
        )}
      </td>
    </tr>
  );
}
