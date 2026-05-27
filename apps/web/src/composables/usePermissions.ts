import { computed } from "vue";
import { OPERATOR_MODE_ENABLED } from "../config/features";
import { normalizeAdminRole } from "../admin/domain/permissions";
import { sessionState } from "../stores/session";

export type PlatformRole =
  | "practitioner"
  | "super_admin"
  | "operator"
  | "finance_admin"
  | "support_admin"
  | "moderator"
  | "admin"
  | "customer";

export function getPostLoginRoute(role?: string | null): { name: string } {
  const current = (role || "customer") as PlatformRole;
  if (current === "practitioner" && OPERATOR_MODE_ENABLED) return { name: "app-deals" };
  if (current === "super_admin") return { name: "admin-overview" };
  if (current === "finance_admin") return { name: "admin-payouts" };
  if (current === "support_admin") return { name: "admin-support" };
  if (current === "moderator") return { name: "admin-moderation" };
  if (current === "operator" || current === "admin") return { name: "admin-overview" };
  return { name: "dashboard" };
}

export function usePermissions() {
  const role = computed(() => (sessionState.me?.role || "customer") as PlatformRole);
  const isAdmin = computed(() => {
    const normalized = normalizeAdminRole(role.value);
    return ["super_admin", "operator", "finance_admin", "support_admin", "moderator"].includes(normalized);
  });
  const homeRoute = computed(() => getPostLoginRoute(role.value));

  return {
    role,
    isAdmin,
    homeRoute
  };
}
