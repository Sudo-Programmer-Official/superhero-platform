import { beforeEach, describe, expect, it, vi } from "vitest";

import { fetchMe } from "./api";

describe("api service", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("throws a readable error when /me fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500
      })
    );

    await expect(fetchMe("token")).rejects.toThrow("Failed /me: 500");
  });
});
