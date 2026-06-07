import fs from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

describe("pwa regression checks", () => {
  const manifestPath = path.resolve(__dirname, "../../public/manifest.webmanifest");
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf-8")) as {
    name: string;
    start_url: string;
    display: string;
    icons: Array<{ src: string; sizes: string; purpose?: string }>;
  };
  const viteConfigPath = path.resolve(__dirname, "../../vite.config.ts");
  const viteConfig = fs.readFileSync(viteConfigPath, "utf-8");

  it("uses OpenMat manifest defaults", () => {
    expect(manifest.name).toBe("OpenMat");
    expect(manifest.start_url).toBe("/app");
    expect(manifest.display).toBe("standalone");
  });

  it("includes required install icons", () => {
    expect(manifest.icons.some((icon) => icon.sizes === "192x192")).toBe(true);
    expect(manifest.icons.some((icon) => icon.sizes === "512x512")).toBe(true);
    expect(manifest.icons.some((icon) => (icon.purpose || "").includes("maskable"))).toBe(true);
  });

  it("configures vite-plugin-pwa", () => {
    expect(viteConfig).toContain("VitePWA");
    expect(viteConfig).toContain("registerType: \"autoUpdate\"");
    expect(viteConfig).toContain("navigateFallback: \"/index.html\"");
  });
});
