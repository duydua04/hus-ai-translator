import React from "react";

const VARIANT_MAP = {
  active: "badge--active",
  inactive: "badge--inactive",
  pending: "badge--pending",
  pro: "badge--pro",
  free: "badge--free",
  enterprise: "badge--ent",
  positive: "badge--positive",
  negative: "badge--negative",
  resolved: "badge--resolved",
  "pending-review": "badge--pending-review",
};

export default function Badge({ variant, dot = false, children }) {
  return (
    <span className={`badge ${VARIANT_MAP[variant] || ""}`}>
      {dot && <span className="badge__dot" />}
      {children}
    </span>
  );
}
