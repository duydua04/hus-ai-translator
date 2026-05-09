import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import "./Sidebar.scss";

const NAV_ITEMS = [
  {
    section: "Người dùng",
    items: [{ path: "/users", icon: "bx-group", label: "Quản lý người dùng" }],
  },
  {
    section: "Feedback",
    items: [
      { path: "/feedback/dash", icon: "bx-grid-alt", label: "Dashboard" },
      {
        path: "/feedback/list",
        icon: "bx-list-ul",
        label: "Danh sách feedback",
      },
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
  const [hovered, setHovered] = useState(false);

  const displayName = admin?.name || admin?.email || "Administrator";
  const role = admin?.role || "Toàn quyền truy cập";
  const initials = getInitials(admin?.name);

  return (
    <aside className="sidebar">
      <div className="sidebar__logo">
        <div className="sidebar__logo-icon">
          <i className="bx bx-store" />
        </div>
        <div>
          <div className="sidebar__logo-text">Admin</div>
          <div className="sidebar__logo-ver">v2.0</div>
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
        <div
          className={`admin-card${hovered ? " admin-card--hovered" : ""}`}
          onMouseEnter={() => setHovered(true)}
          onMouseLeave={() => setHovered(false)}
        >
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
  );
}
