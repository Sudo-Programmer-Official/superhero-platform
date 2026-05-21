export type GuardState = {
  ready: boolean;
  token: string | null;
  me: { role: string } | null;
};

export function evaluateRouteGuard(
  to: { name?: string | symbol | null; meta: Record<string, unknown> },
  state: GuardState
) {
  if (!state.ready) return true;
  if (to.meta.requiresAuth && !state.token) return { name: "auth" };
  if (to.name === "auth" && state.token) return { name: "home" };

  const allowedRoles = to.meta.roles as string[] | undefined;
  if (allowedRoles && state.me && !allowedRoles.includes(state.me.role)) {
    return { name: "home" };
  }
  return true;
}
