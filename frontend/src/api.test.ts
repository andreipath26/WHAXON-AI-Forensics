import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, api } from "./api";

afterEach(() => vi.unstubAllGlobals());

describe("typed API client", () => {
  it("sends same-origin JSON requests and returns JSON", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }));
    vi.stubGlobal("fetch", fetchMock);
    await expect(api<{ ok: boolean }>("/api/health")).resolves.toEqual({ ok: true });
    expect(fetchMock).toHaveBeenCalledWith("/api/health", expect.objectContaining({
      credentials: "same-origin",
      headers: expect.objectContaining({ Accept: "application/json" }),
    }));
  });

  it("surfaces backend errors instead of presenting a false success", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ error: "scope denied" }), {
      status: 403,
      headers: { "Content-Type": "application/json" },
    })));
    await expect(api("/api/run", { method: "POST", body: "{}" }))
      .rejects.toMatchObject<ApiError>({ message: "scope denied", status: 403 });
  });
});
