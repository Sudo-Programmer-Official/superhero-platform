import { describe, expect, it } from "vitest";

import { evaluateRouteGuard } from "./guard";

describe("route guard", () => {
  it("redirects unauthenticated users from protected routes", () => {
    const result = evaluateRouteGuard(
      { name: "home", meta: { requiresAuth: true } },
      { ready: true, token: null, me: null }
    );
    expect(result).toEqual({ name: "auth" });
  });

  it("redirects authenticated users away from auth page", () => {
    const result = evaluateRouteGuard(
      { name: "auth", meta: {} },
      { ready: true, token: "token", me: { role: "customer" } }
    );
    expect(result).toEqual({ name: "home" });
  });

  it("blocks role-restricted route access", () => {
    const result = evaluateRouteGuard(
      { name: "profile", meta: { requiresAuth: true, roles: ["practitioner", "admin", "super_admin"] } },
      { ready: true, token: "token", me: { role: "customer" } }
    );
    expect(result).toEqual({ name: "home" });
  });
});
