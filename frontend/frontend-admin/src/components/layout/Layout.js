import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import { Outlet, useLocation } from "react-router-dom";

export default function Layout() {
  const location = useLocation();

  return (
    <>
      <Sidebar currentPath={location.pathname} />
      <div className="main">
        <Topbar currentPath={location.pathname} />
        <div className="content">
          <Outlet />
        </div>
      </div>
    </>
  );
}
