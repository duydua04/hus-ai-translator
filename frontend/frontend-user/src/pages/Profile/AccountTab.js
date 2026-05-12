import React from "react";

const TIER_LABELS = {
  free: "Miễn phí",
  basic: "Cơ bản",
  pro: "Pro",
  premium: "Premium",
  enterprise: "Enterprise",
};

const getTierLabel = (tier) =>
  TIER_LABELS[tier?.toLowerCase()] ?? (tier || "—");

const formatDate = (isoString) => {
  if (!isoString) return "—";
  return new Date(isoString).toLocaleDateString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
};

export default function AccountTab({ profile }) {
  const rows = [
    { icon: "bx-id-card", label: "id", value: profile?.id || "—", mono: true },
    { icon: "bx-envelope", label: "email", value: profile?.email || "—" },
    {
      icon: "bx-crown",
      label: "Gói tài khoản",
      value: getTierLabel(profile?.tier),
      badge: true,
      tier: profile?.tier,
    },
    {
      icon: "bx-check-shield",
      label: "Trạng thái",
      value: profile?.is_active ? "Đang hoạt động" : "Đã khoá",
      status: profile?.is_active ? "active" : "inactive",
    },
    {
      icon: "bx-calendar",
      label: "Ngày tham gia",
      value: formatDate(profile?.created_at),
    },
  ];

  return (
    <div className="profile-page__card">
      <h2 className="profile-page__card-title">Thông tin tài khoản</h2>
      <ul className="profile-page__account-list">
        {rows.map((row) => (
          <li key={row.label} className="profile-page__account-row">
            <span className="profile-page__account-icon">
              <i className={`bx ${row.icon}`}></i>
            </span>
            <span className="profile-page__account-label">{row.label}</span>
            <span
              className={[
                "profile-page__account-value",
                row.mono ? "profile-page__account-value--mono" : "",
                row.badge
                  ? `profile-page__account-value--tier profile-page__account-value--tier-${row.tier?.toLowerCase()}`
                  : "",
                row.status
                  ? `profile-page__account-value--status profile-page__account-value--status-${row.status}`
                  : "",
              ]
                .filter(Boolean)
                .join(" ")}
            >
              {row.status && <span className="profile-page__status-dot"></span>}
              {row.value}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
