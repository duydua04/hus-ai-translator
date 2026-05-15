import React from "react";

const AVATAR_COLORS = [
  "#4f86f7",
  "#f76e4f",
  "#4fcf70",
  "#f7c74f",
  "#a78bfa",
  "#f472b6",
  "#34d399",
  "#fb923c",
];
const avatarColor = (name = "") => {
  const code = [...name].reduce((s, c) => s + c.charCodeAt(0), 0);
  return AVATAR_COLORS[code % AVATAR_COLORS.length];
};
const initials = (name = "") =>
  name
    .split(" ")
    .slice(-2)
    .map((w) => w[0])
    .join("")
    .toUpperCase();

export default function RecentUsersCard({ users }) {
  return (
    <div className="chart-card">
      <div className="chart-card__header">
        <div className="chart-card__title">Người dùng hoạt động gần đây</div>
      </div>
      <div className="user-list">
        {(users ?? []).map((u) => (
          <div className="user-row" key={u.id}>
            <div
              className="user-avatar"
              style={{ background: avatarColor(u.full_name) }}
            >
              {initials(u.full_name)}
            </div>
            <div className="user-info">
              <div className="user-info__name">{u.full_name}</div>
              <div className="user-info__meta">
                {u.translation_count} lượt dịch
                {u.last_active ? ` · ${u.last_active}` : ""}
              </div>
            </div>
            <span className={`badge badge--${u.is_active ? u.tier : "banned"}`}>
              {u.is_active ? (u.tier === "pro" ? "Pro" : "Free") : "Banned"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
