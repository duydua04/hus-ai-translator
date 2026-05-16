import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import Header from "./components/Header/Header";
import Footer from "./components/Footer/Footer";

import TransFilesPage from "./pages/Home/HomePage";
import AboutUsPage from "./pages/AboutUs/AboutUsPage";
import LoginPage from "./pages/Auth/Login/LoginPage";
import RegisterPage from "./pages/Auth/Register/RegisterPage";
import ProfilePage from "./pages/Profile/Profile";
import NotFound from "./pages/nf/NotFound";

import useAuth from "./hooks/useAuth";

import "./assets/styles/base.scss";
import "./assets/styles/layout.scss";
import "./assets/styles/components.scss";

function MainLayout({ user, logout }) {
  return (
    <div className="app-wrapper">
      <Header user={user} logout={logout} />

      <main className="app-main">
        <Routes>
          <Route path="/" element={<Navigate to="/home/text" replace />} />
          <Route path="/home" element={<Navigate to="/home/text" replace />} />
          <Route path="/home/:mode" element={<TransFilesPage user={user} />} />
          <Route
            path="/trans-files"
            element={<Navigate to="/home/text" replace />}
          />
          <Route path="/about-us" element={<AboutUsPage />} />
          <Route
            path="/profile"
            element={user ? <ProfilePage /> : <Navigate to="/login" replace />}
          />
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
        <Route
          path="/login"
          element={
            user ? (
              <Navigate to="/home/text" replace />
            ) : (
              <LoginPage login={login} loading={loading} error={error} />
            )
          }
        />
        <Route
          path="/register"
          element={
            user ? (
              <Navigate to="/home/text" replace />
            ) : (
              <RegisterPage
                register={register}
                loading={loading}
                error={error}
              />
            )
          }
        />
        <Route path="/*" element={<MainLayout user={user} logout={logout} />} />
      </Routes>
    </Router>
  );
}
