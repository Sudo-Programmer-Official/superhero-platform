import { describe, expect, it } from "vitest";

import { evaluateRouteGuard } from "./guard";

describe("route guard", () => {
  it("redirects unauthenticated users from protected routes", async () => {
    const result = await evaluateRouteGuard(
      { name: "dashboard", meta: { requiresAuth: true }, fullPath: "/dashboard", path: "/dashboard" },
      { ready: true, token: null, me: null, meLoaded: false }
    );
    expect(result).toEqual({ path: "/sign-in", query: { next: "/dashboard" } });
  });

  it("redirects authenticated users away from auth page", async () => {
    const result = await evaluateRouteGuard(
      { name: "signin", meta: {}, fullPath: "/sign-in", path: "/sign-in" },
      { ready: true, token: "token", me: { role: "customer", practitioner_id: "p1" }, meLoaded: true }
    );
    expect(result).toEqual({ name: "dashboard" });
  });

  it("redirects authenticated users without practitioner profile to onboarding", async () => {
    const result = await evaluateRouteGuard(
      { name: "deals", meta: { requiresAuth: true }, fullPath: "/dashboard/deals", path: "/dashboard/deals" },
      { ready: true, token: "token", me: { role: "practitioner", practitioner_id: null }, meLoaded: true }
    );
    expect(result).toEqual({ name: "onboarding" });
  });

  it("blocks role-restricted route access", async () => {
    const result = await evaluateRouteGuard(
      {
        name: "profile",
        meta: { requiresAuth: true, roles: ["practitioner", "admin", "super_admin"] },
        fullPath: "/app/profile",
        path: "/app/profile"
      },
      { ready: true, token: "token", me: { role: "customer", practitioner_id: "p1" }, meLoaded: true }
    );
    expect(result).toEqual({ name: "dashboard" });
  });

  it("requires sign-in if /me is unresolved after auth for protected routes", async () => {
    const result = await evaluateRouteGuard(
      { name: "dashboard", meta: { requiresAuth: true }, fullPath: "/dashboard", path: "/dashboard" },
      { ready: true, token: "token", me: null, meLoaded: false }
    );
    expect(result).toEqual({ path: "/sign-in", query: { next: "/dashboard" } });
  });
});
