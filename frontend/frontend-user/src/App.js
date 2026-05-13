import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import Header from "./components/Header/Header";
import Footer from "./components/Footer/Footer";

import HomePage from "./pages/Home/HomePage";
import TransFilesPage from "./pages/TransFiles/TransFilesPage";
import AboutUsPage from "./pages/AboutUs/AboutUsPage";
import LoginPage from "./pages/Auth/Login/LoginPage";
import RegisterPage from "./pages/Auth/Register/RegisterPage";
import ForgotPasswordPage from "./pages/Auth/ForgotPassword/ForgotPassword";
import ProfilePage from "./pages/Profile/Profile";
import NotFound from "./pages/nf/NotFound";

import useAuth from "./hooks/useAuth";

import "./assets/styles/base.scss";
import "./assets/styles/layout.scss";
import "./assets/styles/components.scss";

function PrivateRoute({ user, children }) {
  if (user === undefined) return null;

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function MainLayout({ user, logout }) {
  return (
    <div className="app-wrapper">
      <Header user={user} logout={logout} />

      <main className="app-main">
        <Routes>
          {/* Public */}
          <Route path="/" element={<HomePage />} />
          <Route path="/about-us" element={<AboutUsPage />} />

          {/* Protected */}
          <Route
            path="/trans-files"
            element={
              <PrivateRoute user={user}>
                <TransFilesPage />
              </PrivateRoute>
            }
          />

          <Route
            path="/profile"
            element={
              <PrivateRoute user={user}>
                <ProfilePage />
              </PrivateRoute>
            }
          />

          {/* Not Found */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>

      <Footer />
    </div>
  );
}

export default function App() {
  const { user, login, logout, register, loading, error } = useAuth();

  return (
    <Router>
      <Routes>
        {/* Auth */}
        <Route
          path="/login"
          element={
            user ? (
              <Navigate to="/" replace />
            ) : (
              <LoginPage login={login} loading={loading} error={error} />
            )
          }
        />

        <Route
          path="/register"
          element={
            user ? (
              <Navigate to="/" replace />
            ) : (
              <RegisterPage
                register={register}
                loading={loading}
                error={error}
              />
            )
          }
        />

        <Route path="/forgot-password" element={<ForgotPasswordPage />} />

        {/* Main Layout */}
        <Route path="/*" element={<MainLayout user={user} logout={logout} />} />
      </Routes>
    </Router>
  );
}
