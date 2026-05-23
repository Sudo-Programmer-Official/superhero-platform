export type AdminRole = "super_admin" | "operator" | "finance_admin" | "support_admin" | "moderator";

export const adminNav = [
  { id: "overview", section: "Control", label: "Overview", route: "admin-overview", roles: ["super_admin", "operator", "finance_admin", "support_admin", "moderator"] },
  { id: "analytics", section: "Control", label: "Analytics", route: "admin-analytics", roles: ["super_admin", "operator", "finance_admin"] },
  { id: "health", section: "Control", label: "System Health", route: "admin-health", roles: ["super_admin", "operator"] },
  { id: "practitioners", section: "Operations", label: "Practitioners", route: "admin-practitioners", roles: ["super_admin", "operator", "support_admin"] },
  { id: "deals", section: "Operations", label: "Deals", route: "admin-deals", roles: ["super_admin", "operator", "moderator"] },
  { id: "wallet-passes", section: "Operations", label: "Wallet Passes", route: "admin-wallet-passes", roles: ["super_admin", "operator", "support_admin"] },
  { id: "redemptions", section: "Operations", label: "Redemptions", route: "admin-redemptions", roles: ["super_admin", "operator", "support_admin", "moderator"] },
  { id: "bookings", section: "Operations", label: "Bookings", route: "admin-bookings", roles: ["super_admin", "operator", "finance_admin", "support_admin"] },
  { id: "payouts", section: "Finance", label: "Payouts", route: "admin-payouts", roles: ["super_admin", "finance_admin"] },
  { id: "subscriptions", section: "Finance", label: "Subscriptions", route: "admin-subscriptions", roles: ["super_admin", "finance_admin", "support_admin"] },
  { id: "merchandise", section: "Finance", label: "Merchandise", route: "admin-merchandise", roles: ["super_admin", "operator"] },
  { id: "support", section: "Trust", label: "Support", route: "admin-support", roles: ["super_admin", "support_admin", "operator"] },
  { id: "moderation", section: "Trust", label: "Moderation", route: "admin-moderation", roles: ["super_admin", "moderator", "operator"] },
  { id: "automations", section: "Platform", label: "Automations", route: "admin-automations", roles: ["super_admin", "operator"] },
  { id: "integrations", section: "Platform", label: "Integrations", route: "admin-integrations", roles: ["super_admin", "operator", "finance_admin"] },
  { id: "settings", section: "Platform", label: "Settings", route: "admin-settings", roles: ["super_admin"] }
] as const;

export function canAccessAdminRole(role: string): role is AdminRole {
  return ["super_admin", "operator", "finance_admin", "support_admin", "moderator", "admin"].includes(role);
}

export function normalizeAdminRole(role: string): AdminRole {
  if (role === "admin") return "operator";
  if (role === "finance_admin" || role === "support_admin" || role === "moderator" || role === "super_admin" || role === "operator") return role;
  return "operator";
}
