"use client";

import React, { ReactNode } from "react";

// RBAC matrix role rankings definition
const ROLE_HIERARCHY: Record<string, number> = {
  superadmin: 4,
  admin: 3,
  editor: 2,
  viewer: 1,
};

export interface PermissionGateProps {
  children: ReactNode;
  fallback?: ReactNode;
  requiredRole?: "superadmin" | "admin" | "editor" | "viewer";
  currentUserRole?: string; // e.g. fetched from global auth state
}

export function PermissionGate({
  children,
  fallback = null,
  requiredRole = "viewer",
  currentUserRole = "admin", // default mock role for Phase 5 demo panels
}: PermissionGateProps) {
  const currentLevel = ROLE_HIERARCHY[currentUserRole.toLowerCase()] || 0;
  const requiredLevel = ROLE_HIERARCHY[requiredRole.toLowerCase()] || 1;

  // Render children only if current user has authorized permission score
  if (currentLevel >= requiredLevel) {
    return <>{children}</>;
  }

  return <>{fallback}</>;
}
export default PermissionGate;
