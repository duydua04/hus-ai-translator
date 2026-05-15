import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import "./Sidebar.scss";

const NAV_ITEMS = [
  {
    section: "Dashboard",
    items: [{ path: "dash", icon: "bx-grid-alt", label: "Thống kê" }],
  },
  {
    section: "Người dùng",
    items: [{ path: "/users", icon: "bx-group", label: "Quản lý người dùng" }],
  },
  {
    section: "Feedback",
    items: [
      {
        path: "/feedback/list",
        icon: "bx-list-ul",
        label: "Danh sách feedback",
      },
    ],
  },
  {
    section: "Ngôn ngữ",
    items: [
      { path: "/languages", icon: "bx-world", label: "Quản lý ngôn ngữ" },
    ],
  },
];

function getInitials(name) {
  if (!name) return "AD";
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0][0].toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

export default function Sidebar({ admin, onLogout }) {
  const [confirmLogout, setConfirmLogout] = useState(false);

  const displayName = admin?.name || admin?.email || "Administrator";
  const role = admin?.role || "Toàn quyền truy cập";
  const initials = getInitials(admin?.name);

  const handleAvatarClick = () => {
    if (confirmLogout) {
      onLogout();
    } else {
      setConfirmLogout(true);
      setTimeout(() => setConfirmLogout(false), 3000);
    }
  };

  return (
    <>
      <aside className="sidebar sidebar--desktop">
        <div className="sidebar__logo">
          <div className="sidebar__logo-icon">
            <i className="bx bx-store" />
          </div>
          <div>
            <div className="sidebar__logo-text">TRANSDE</div>
            <div className="sidebar__logo-ver">admin</div>
          </div>
        </div>

        {NAV_ITEMS.map(({ section, items }) => (
          <div className="sidebar__section" key={section}>
            <div className="sidebar__section-label">{section}</div>
            {items.map(({ path, icon, label }) => (
              <NavLink
                key={path}
                to={path}
                className={({ isActive }) =>
                  `nav-item${isActive ? " nav-item--active" : ""}`
                }
              >
                <i className={`bx ${icon} nav-item__icon`} />
                <span className="nav-item__text">{label}</span>
              </NavLink>
            ))}
          </div>
        ))}

        <div className="sidebar__footer">
          <div className="admin-card">
            <div className="admin-card__avatar">{initials}</div>
            <div className="admin-card__info">
              <div className="admin-card__name">{displayName}</div>
              <div className="admin-card__role">{role}</div>
            </div>
            <button
              className="admin-card__logout"
              onClick={onLogout}
              title="Đăng xuất"
              aria-label="Đăng xuất"
            >
              <i className="bx bx-log-out" />
            </button>
          </div>
        </div>
      </aside>

      <nav className="mobile-bar">
        {NAV_ITEMS.flatMap(({ items }) => items).map(
          ({ path, icon, label }) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) =>
                `mobile-bar__item${isActive ? " mobile-bar__item--active" : ""}`
              }
            >
              <i className={`bx ${icon}`} />
            </NavLink>
          )
        )}

        <button
          className={`mobile-bar__item mobile-bar__avatar${
            confirmLogout ? " mobile-bar__avatar--confirm" : ""
          }`}
          onClick={handleAvatarClick}
          title={confirmLogout ? "Bấm lần nữa để đăng xuất" : "Đăng xuất"}
        >
          {confirmLogout ? (
            <i className="bx bx-log-out" />
          ) : (
            <span className="mobile-bar__initials">{initials}</span>
          )}
          {confirmLogout && (
            <span className="mobile-bar__tooltip">
              Bấm lần nữa để đăng xuất
            </span>
          )}
        </button>
      </nav>
    </>
  );
}
