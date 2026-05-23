import { getPostLoginRoute } from "../composables/usePermissions";

export type GuardState = {
  ready: boolean;
  token: string | null;
  me: { role: string; practitioner_id?: string | null } | null;
};

export function evaluateRouteGuard(
  to: { name?: string | symbol | null; meta: Record<string, unknown> },
  state: GuardState
) {
  const role = state.me?.role || "";
  const isPlatformRole = role === "super_admin" || role === "admin" || role === "operator" || role === "finance_admin" || role === "support_admin" || role === "moderator";
  const isAdminRoute = String(to.name || "").startsWith("admin-");

  if (!state.ready) return true;
  if (to.meta.requiresAuth && !state.token) return { name: "signin" };
  if (
    to.meta.requiresAuth &&
    state.token &&
    !state.me?.practitioner_id &&
    to.name !== "onboarding" &&
    !isPlatformRole &&
    !isAdminRoute
  ) {
    return { name: "onboarding" };
  }
  if ((to.name === "signin" || to.name === "signup") && state.token) {
    return getPostLoginRoute(state.me?.role);
  }
  if (to.name === "onboarding" && state.token && state.me?.practitioner_id) {
    return getPostLoginRoute(state.me?.role);
  }

  const allowedRoles = to.meta.roles as string[] | undefined;
  if (allowedRoles && state.me && !allowedRoles.includes(state.me.role)) {
    return getPostLoginRoute(state.me.role);
  }
  return true;
}
