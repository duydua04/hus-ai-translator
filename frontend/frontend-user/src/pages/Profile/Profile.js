import React, { useState, useCallback } from "react";
import "./Profile.scss";
import useProfile from "../../hooks/useProfile";
import InfoTab from "./InfoTab";
import PasswordTab from "./PasswordTab";
import AccountTab from "./AccountTab";
import FeedbackPage from "../Feedback/FeedbackPage";

// Helpers
const getInitials = (profile) => {
  if (!profile) return "";
  const name = profile.full_name || profile.email || "";
  return name
    .split(" ")
    .map((w) => w[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
};

// Skeleton
function ProfileSkeleton() {
  return (
    <div className="profile-page__header">
      <div className="profile-page__skeleton profile-page__skeleton--avatar"></div>
      <div>
        <div className="profile-page__skeleton profile-page__skeleton--title"></div>
        <div className="profile-page__skeleton profile-page__skeleton--text"></div>
      </div>
    </div>
  );
}

const TABS = [
  { key: "account", label: "Tài khoản" },
  { key: "info", label: "Cập nhật" },
  { key: "password", label: "Đổi mật khẩu" },
  { key: "feedback", label: "Đánh giá" },
];

export default function Profile() {
  const [activeTab, setActiveTab] = useState("account");
  const {
    profile,
    loading,
    error,
    success,
    updateProfile,
    changePassword,
    clearMessages,
  } = useProfile();

  const handleTabChange = useCallback(
    (key) => {
      setActiveTab(key);
      clearMessages();
    },
    [clearMessages]
  );

  return (
    <div className="profile-page">
      <div className="profile-page__inner">
        {/* Header */}
        {!profile ? (
          <ProfileSkeleton />
        ) : (
          <div className="profile-page__header">
            <div className="profile-page__avatar-wrap">
              {profile.avatar ? (
                <img
                  src={profile.avatar}
                  alt={profile.full_name || profile.email}
                  className="profile-page__avatar"
                />
              ) : (
                <div className="profile-page__avatar-initials">
                  {getInitials(profile)}
                </div>
              )}
            </div>
            <div className="profile-page__header-meta">
              <div className="profile-page__heading-row">
                <h1 className="profile-page__heading">
                  {profile.full_name || "Người dùng"}
                </h1>
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="profile-page__tabs" role="tablist">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              role="tab"
              aria-selected={activeTab === tab.key}
              className={`profile-page__tab${
                activeTab === tab.key ? " profile-page__tab--active" : ""
              }`}
              onClick={() => handleTabChange(tab.key)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab content */}
        {activeTab === "account" && <AccountTab profile={profile} />}
        {activeTab === "info" && (
          <InfoTab
            profile={profile}
            loading={loading}
            error={error}
            success={success}
            onUpdate={updateProfile}
            onClearMessages={clearMessages}
          />
        )}
        {activeTab === "password" && (
          <PasswordTab
            loading={loading}
            error={error}
            success={success}
            onChangePassword={changePassword}
            onClearMessages={clearMessages}
          />
        )}
        {activeTab === "feedback" && <FeedbackPage />}
      </div>
    </div>
  );
}
