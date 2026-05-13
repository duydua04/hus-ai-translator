import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import { Outlet, useLocation } from "react-router-dom";

export default function Layout({ admin, onLogout }) {
  const location = useLocation();

  return (
    <>
      <Sidebar
        currentPath={location.pathname}
        admin={admin}
        onLogout={onLogout}
      />
      <div className="main">
        <Topbar currentPath={location.pathname} />
        <div className="content">
          <Outlet />
        </div>
      </div>
    </>
  );
}
