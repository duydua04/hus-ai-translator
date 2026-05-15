import React from "react";
import { useLocation } from "react-router-dom";
import "./Topbar.scss";

export default function Topbar() {
  const location = useLocation();

  const path = location.pathname;

  let title = "Admin";

  if (path.startsWith("/users")) {
    title = "Quản lý người dùng";
  } else if (path.startsWith("/feedback")) {
    title = "Quản lý Feedback";
  } else if (path.startsWith("/languages")) {
    title = "Quản lý ngôn ngữ";
  } else if (path.startsWith("/dash")) {
    title = "Dashboard";
  }

  return (
    <header className="topbar">
      <div>
        <span className="topbar__title">{title}</span>
      </div>

      <div className="topbar__actions">
        <button className="topbar__btn topbar__btn--notif">
          <i className="bx bx-bell" />
        </button>
      </div>
    </header>
  );
}
