import React from "react";
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

export default function Sidebar() {
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
        <div className="admin-card">
          <div className="admin-card__avatar">AD</div>
          <div className="admin-card__info">
            <div className="admin-card__name">Administrator</div>
            <div className="admin-card__role">Toàn quyền truy cập</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
