import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import Layout from "./components/layout/Layout";

import UsersPage from "./pages/users/UsersPage";
import FeedbackDashPage from "./pages/feedback/FeedbackDashPage";
import FeedbackListPage from "./pages/feedback/FeedbackListPage";

import "./assets/styles/base.scss";
import "./assets/styles/layout.scss";
import "./assets/styles/components.scss";

export default function App() {
  return (
    <Router>
      <Routes>
        {/* redirect mặc định */}
        <Route path="/" element={<Navigate to="/users" />} />

        {/* layout chung */}
        <Route path="/" element={<Layout />}>
          <Route path="users" element={<UsersPage />} />
          <Route path="feedback/dash" element={<FeedbackDashPage />} />
          <Route path="feedback/list" element={<FeedbackListPage />} />
        </Route>

        {/* 404 */}
        <Route path="*" element={<div>404 Not Found</div>} />
      </Routes>
    </Router>
  );
}
