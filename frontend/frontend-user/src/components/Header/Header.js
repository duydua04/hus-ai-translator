import React, { useState, useRef, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import "./Header.scss";

const NAV_LINKS = [
  { to: "/", label: "Trang chủ", protected: false },
  { to: "/trans-files", label: "Dịch tệp", protected: true },
  { to: "/about-us", label: "Về chúng tôi", protected: false },
];

function Header({ user, logout }) {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleProtectedLink = (e, link) => {
    if (link.protected && !user) {
      e.preventDefault();
      navigate("/login");
    }
  };

  const handleLogout = async () => {
    setDropdownOpen(false);
    await logout();
    navigate("/");
  };

  // Get initials from user's name or email
  const getInitials = () => {
    if (!user) return "";
    const name = user.full_name || user.name || user.email || "";
    return name
      .split(" ")
      .map((w) => w[0])
      .slice(0, 2)
      .join("")
      .toUpperCase();
  };

  return (
    <header className="header">
      <Link to="/" className="header__brand">
        <i className="bx bx-store header__brand-icon"></i>
        <span className="header__brand-text">Site name</span>
      </Link>

      <nav className="header__nav">
        {NAV_LINKS.map(({ to, label, protected: isProtected }) => (
          <Link
            key={to}
            to={to}
            className={`header__link${
              pathname === to ? " header__link--active" : ""
            }${isProtected && !user ? " header__link--locked" : ""}`}
            onClick={(e) =>
              handleProtectedLink(e, { to, protected: isProtected })
            }
          >
            {isProtected && !user && (
              <i className="bx bx-lock-alt header__link-lock"></i>
            )}
            {label}
          </Link>
        ))}
      </nav>

      {user ? (
        <div className="header__user" ref={dropdownRef}>
          <button
            className="header__avatar"
            onClick={() => setDropdownOpen((prev) => !prev)}
            aria-label="Tài khoản"
          >
            {user.avatar ? (
              <img
                src={user.avatar}
                alt={user.full_name || user.email}
                className="header__avatar-img"
              />
            ) : (
              <span className="header__avatar-initials">{getInitials()}</span>
            )}
            <i
              className={`bx bx-chevron-down header__avatar-chevron${
                dropdownOpen ? " header__avatar-chevron--open" : ""
              }`}
            ></i>
          </button>

          {dropdownOpen && (
            <div className="header__dropdown">
              <div className="header__dropdown-info">
                <span className="header__dropdown-name">
                  {user.full_name || user.name || user.email}
                </span>
                <span className="header__dropdown-email">{user.email}</span>
              </div>
              <div className="header__dropdown-divider"></div>
              <Link
                to="/profile"
                className="header__dropdown-item"
                onClick={() => setDropdownOpen(false)}
              >
                <i className="bx bx-user"></i>
                Trang cá nhân
              </Link>
              <button
                className="header__dropdown-item header__dropdown-item--logout"
                onClick={handleLogout}
              >
                <i className="bx bx-log-out"></i>
                Đăng xuất
              </button>
            </div>
          )}
        </div>
      ) : (
        <Link to="/login" className="btn btn--primary">
          Đăng nhập
        </Link>
      )}
    </header>
  );
}

export default Header;
