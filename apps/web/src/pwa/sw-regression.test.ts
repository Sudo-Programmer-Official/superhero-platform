import fs from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

describe("service worker regression checks", () => {
  const swPath = path.resolve(__dirname, "../../public/sw.js");
  const swSource = fs.readFileSync(swPath, "utf-8");

  it("does not precache root document in static install list", () => {
    expect(swSource).toContain('const STATIC_ASSETS = ["/manifest.webmanifest", "/pwa-icon.svg"]');
  });

  it("has explicit navigate network-first handling", () => {
    expect(swSource).toContain('event.request.mode === "navigate"');
    expect(swSource).toContain("fetch(event.request)");
  });
});
