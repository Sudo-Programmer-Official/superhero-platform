export type GuardState = {
  ready: boolean;
  token: string | null;
  me: { role: string; practitioner_id?: string | null } | null;
};

export function evaluateRouteGuard(
  to: { name?: string | symbol | null; meta: Record<string, unknown> },
  state: GuardState
) {
  if (!state.ready) return true;
  if (to.meta.requiresAuth && !state.token) return { name: "signin" };
  if (to.meta.requiresAuth && state.token && !state.me?.practitioner_id && to.name !== "onboarding") {
    return { name: "onboarding" };
  }
  if ((to.name === "signin" || to.name === "signup") && state.token) return { name: "dashboard" };
  if (to.name === "onboarding" && state.token && state.me?.practitioner_id) return { name: "dashboard" };

  const allowedRoles = to.meta.roles as string[] | undefined;
  if (allowedRoles && state.me && !allowedRoles.includes(state.me.role)) {
    return { name: "dashboard" };
  }
  return true;
}
