import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import Layout from "./components/layout/Layout";

import Login from "./pages/auth/Login";
import UsersPage from "./pages/users/UsersPage";
import DashPage from "./pages/dashboard/DashPage";
import FeedbackListPage from "./pages/feedback/FeedbackListPage";
import NotFound from "./pages/nf/NotFound";
import LanguagesPage from "./pages/language/Language";

import useAuth from "./hooks/useAuth";

import "./assets/styles/base.scss";
import "./assets/styles/layout.scss";
import "./assets/styles/components.scss";

function PrivateRoute({ admin, children }) {
  if (admin === undefined) return null;
  if (admin === null) return <Navigate to="/login" />;
  return children;
}

export default function App() {
  const { admin, login, logout, loading, error } = useAuth();

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />

        <Route
          path="/login"
          element={
            admin ? (
              <Navigate to="/users" />
            ) : (
              <Login login={login} loading={loading} error={error} />
            )
          }
        />

        <Route
          path="/"
          element={
            <PrivateRoute admin={admin}>
              <Layout admin={admin} onLogout={logout} />
            </PrivateRoute>
          }
        >
          <Route index element={<Navigate to="/users" />} />
          <Route path="users" element={<UsersPage />} />
          <Route path="dash" element={<DashPage />} />
          <Route path="feedback/list" element={<FeedbackListPage />} />
          <Route path="languages" element={<LanguagesPage />} />
        </Route>

        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
}
