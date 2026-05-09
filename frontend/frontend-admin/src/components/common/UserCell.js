import React from "react";

export default function UserCell({
  initials,
  name,
  email,
  avatarBg,
  avatarColor,
  size = 30,
}) {
  return (
    <div className="user-cell">
      <div
        className="user-cell__avatar"
        style={{
          background: avatarBg,
          color: avatarColor,
          width: size,
          height: size,
          fontSize: size < 30 ? 10 : 11,
        }}
      >
        {initials}
      </div>
      <div>
        <div className="user-cell__name">{name}</div>
        {email && <div className="user-cell__email">{email}</div>}
      </div>
    </div>
  );
}
