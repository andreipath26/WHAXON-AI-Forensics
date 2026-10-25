import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./ui/App";

let root: Root;
let host: HTMLDivElement;

function response(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

beforeEach(() => {
  host = document.createElement("div");
  document.body.appendChild(host);
  root = createRoot(host);
  vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url === "/api/health") return response({ ok: true });
    if (url === "/api/tools") return response([]);
    if (url === "/api/scope") return response({ enabled: true, in_scope: ["127.0.0.0/8"] });
    if (url === "/api/scope/check") return response({ allowed: false, reason: "not in scope" });
    return response({ error: "not found" }, 404);
  }));
});

afterEach(async () => {
  await act(async () => root.unmount());
  host.remove();
  vi.unstubAllGlobals();
});

describe("Obsidian Kinetic React shell", () => {
  it("shows backend state without invented findings or telemetry", async () => {
    await act(async () => {
      root.render(<App />);
    });
    expect(host.textContent).toContain("WHAXON security operations");
    expect(host.textContent).toContain("Backend connected");
    expect(host.textContent).toContain("No sample findings or simulated telemetry");
    expect(host.textContent).not.toContain("CVE-2025-0000");
    expect(host.textContent).not.toContain("Demo target");
  });

  it("navigates to scope and displays the server's real decision", async () => {
    await act(async () => root.render(<App />));
    const nav = Array.from(host.querySelectorAll("button")).find((button) => button.textContent === "Scope & targets");
    expect(nav).toBeDefined();
    await act(async () => nav?.click());
    const input = host.querySelector<HTMLInputElement>("#target-scope");
    expect(input).not.toBeNull();
    await act(async () => {
      if (!input) throw new Error("Scope input missing");
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
      setter?.call(input, "example.invalid");
      input.dispatchEvent(new Event("input", { bubbles: true }));
      input.dispatchEvent(new Event("change", { bubbles: true }));
    });
    const form = input?.closest("form");
    expect(form).not.toBeNull();
    await act(async () => form?.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true })));
    expect(host.textContent).toContain("not in scope");
  });
});
