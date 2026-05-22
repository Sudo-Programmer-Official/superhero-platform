import { describe, expect, it } from "vitest";

import { evaluateRouteGuard } from "./guard";

describe("route guard", () => {
  it("redirects unauthenticated users from protected routes", () => {
    const result = evaluateRouteGuard(
      { name: "dashboard", meta: { requiresAuth: true } },
      { ready: true, token: null, me: null }
    );
    expect(result).toEqual({ name: "signin" });
  });

  it("redirects authenticated users away from auth page", () => {
    const result = evaluateRouteGuard(
      { name: "signin", meta: {} },
      { ready: true, token: "token", me: { role: "customer", practitioner_id: "p1" } }
    );
    expect(result).toEqual({ name: "dashboard" });
  });

  it("redirects authenticated users without practitioner profile to onboarding", () => {
    const result = evaluateRouteGuard(
      { name: "deals", meta: { requiresAuth: true } },
      { ready: true, token: "token", me: { role: "practitioner", practitioner_id: null } }
    );
    expect(result).toEqual({ name: "onboarding" });
  });

  it("blocks role-restricted route access", () => {
    const result = evaluateRouteGuard(
      { name: "profile", meta: { requiresAuth: true, roles: ["practitioner", "admin", "super_admin"] } },
      { ready: true, token: "token", me: { role: "customer", practitioner_id: "p1" } }
    );
    expect(result).toEqual({ name: "dashboard" });
  });
});
