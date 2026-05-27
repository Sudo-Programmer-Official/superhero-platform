import { getPostLoginRoute } from "../composables/usePermissions";
import { OPERATOR_MODE_ENABLED } from "../config/features";
import { waitForSessionResolution } from "../stores/session";

export type GuardState = {
  ready: boolean;
  loading?: boolean;
  token: string | null;
  me: { role: string; practitioner_id?: string | null } | null;
  meLoaded?: boolean;
  authState?: "loading" | "authenticated" | "unauthenticated";
};

export async function evaluateRouteGuard(
  to: { name?: string | symbol | null; meta: Record<string, unknown>; fullPath: string; path: string },
  state: GuardState
) {
  const requiresAuth = Boolean(to.meta.requiresAuth);
  const isOperatorRoute = to.path === "/operator" || to.path.startsWith("/operator/");
  if ((requiresAuth || isOperatorRoute) && (!state.ready || state.loading || state.authState === "loading")) {
    await waitForSessionResolution();
  }

  const role = state.me?.role || "";
  const isPlatformRole = role === "super_admin" || role === "admin" || role === "operator" || role === "finance_admin" || role === "support_admin" || role === "moderator";
  const isAdminRoute = String(to.name || "").startsWith("admin-");

  if (!state.ready) return true;
  if (requiresAuth && !state.token) return { path: "/sign-in", query: { next: to.fullPath } };
  if (requiresAuth && state.token && !state.meLoaded) return { path: "/sign-in", query: { next: to.fullPath } };
  if (
    requiresAuth &&
    state.token &&
    !state.me?.practitioner_id &&
    to.name !== "onboarding" &&
    !isPlatformRole &&
    !isAdminRoute
  ) {
    return { name: "onboarding" };
  }
  if ((to.name === "signin" || to.name === "signup") && state.token) {
    const nextParam = new URLSearchParams(to.fullPath.split("?")[1] || "").get("next");
    if (nextParam && nextParam.startsWith("/")) return nextParam;
    return getPostLoginRoute(state.me?.role);
  }
  if (to.name === "onboarding" && state.token && state.me?.practitioner_id) {
    return getPostLoginRoute(state.me?.role);
  }
  if (
    OPERATOR_MODE_ENABLED &&
    state.me?.role === "practitioner" &&
    state.me?.practitioner_id &&
    (to.name === "dashboard" || to.name === "deals" || to.name === "bookings" || to.path === "/app")
  ) {
    return { name: "app-deals" };
  }

  const allowedRoles = to.meta.roles as string[] | undefined;
  if (allowedRoles && state.me && !allowedRoles.includes(state.me.role)) {
    return getPostLoginRoute(state.me.role);
  }
  return true;
}
