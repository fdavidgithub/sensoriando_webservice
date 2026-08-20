import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ApiError, SESSION_EXPIRED, apiGet, apiPost, authGet, authPost } from "./client";
import { clearIdToken, readSession, setIdToken, writeSession } from "../auth/session";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("apiGet", () => {
  it("returns the parsed body on success", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse([{ id: 1, name: "temp" }]));
    vi.stubGlobal("fetch", fetchMock);

    await expect(apiGet("/sensors")).resolves.toEqual([{ id: 1, name: "temp" }]);
    expect(fetchMock).toHaveBeenCalledWith(
      "/sensors",
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("joins the base URL without doubling the slash", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse([]));
    vi.stubGlobal("fetch", fetchMock);

    await apiGet("/sensors", "https://api.example.com/development/");

    expect(fetchMock).toHaveBeenCalledWith(
      "https://api.example.com/development/sensors",
      expect.anything(),
    );
  });

  it("raises ApiError carrying the HTTP status", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse({}, 404)));

    await expect(apiGet("/missing")).rejects.toMatchObject({
      name: "ApiError",
      status: 404,
    });
  });

  it("reports a network failure as status 0", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("failed to fetch")));

    await expect(apiGet("/sensors")).rejects.toMatchObject({
      name: "ApiError",
      status: 0,
    });
  });

  it("reports a malformed body as status 0 rather than crashing", async () => {
    const broken = new Response("not json", {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(broken));

    await expect(apiGet("/sensors")).rejects.toBeInstanceOf(ApiError);
  });

  it("treats an empty body as a valid success instead of a parse failure", async () => {
    // The Fetch spec forbids a body on 204, so it is constructed with null --
    // exactly what fetch() itself hands back for a real 204 response.
    const noContent = new Response(null, { status: 204 });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(noContent));

    await expect(apiGet("/accounts/private")).resolves.toBeUndefined();
  });
});

describe("apiPost", () => {
  it("sends the body as JSON", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse([]));
    vi.stubGlobal("fetch", fetchMock);

    await apiPost("/things", { sensor: "temperatura" });

    expect(fetchMock).toHaveBeenCalledWith(
      "/things",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ sensor: "temperatura" }),
        headers: { "Content-Type": "application/json" },
      }),
    );
  });

  it("omits the body when there is none", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse([]));
    vi.stubGlobal("fetch", fetchMock);

    await apiPost("/things");

    const [, init] = fetchMock.mock.calls[0];
    expect(init.body).toBeUndefined();
  });

  it("uses the message field of the error body", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse({ message: "código inválido" }, 400)),
    );

    await expect(apiPost("/auth/verify", {})).rejects.toMatchObject({
      status: 400,
      message: "código inválido",
    });
  });

  it("uses the detail field of the error body", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse({ detail: "algo" }, 400)));

    await expect(apiPost("/accounts", {})).rejects.toMatchObject({
      status: 400,
      message: "algo",
    });
  });

  it("falls back to the status line when the error body is not JSON", async () => {
    const plain = new Response("not found", { status: 404 });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(plain));

    await expect(apiPost("/missing")).rejects.toMatchObject({
      status: 404,
      message: "A API respondeu 404",
    });
  });
});

function memoryStorage(): Storage {
  const entries = new Map<string, string>();
  return {
    get length() {
      return entries.size;
    },
    clear: () => entries.clear(),
    getItem: (key: string) => entries.get(key) ?? null,
    key: (index: number) => Array.from(entries.keys())[index] ?? null,
    removeItem: (key: string) => void entries.delete(key),
    setItem: (key: string, value: string) => void entries.set(key, value),
  } as Storage;
}

describe("authenticated requests", () => {
  beforeEach(() => {
    vi.stubGlobal("localStorage", memoryStorage());
    clearIdToken();
    writeSession("fulano", "refresh-token");
  });

  it("sends the id token as a bearer credential", async () => {
    setIdToken("id-token", 3600);
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ username: "fulano" }));
    vi.stubGlobal("fetch", fetchMock);

    await authGet("/accounts/private");

    const [, init] = fetchMock.mock.calls[0];
    expect(init.headers.Authorization).toBe("Bearer id-token");
  });

  it("does not send a token on a public request", async () => {
    setIdToken("id-token", 3600);
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse([]));
    vi.stubGlobal("fetch", fetchMock);

    await apiGet("/sensors");

    const [, init] = fetchMock.mock.calls[0];
    expect(init.headers?.Authorization).toBeUndefined();
  });

  it("renews before the first call when only the refresh token survives", async () => {
    // The state right after a page reload: the id token died with the tab.
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ id_token: "novo", expires_in: 3600 }))
      .mockResolvedValueOnce(jsonResponse({ username: "fulano" }));
    vi.stubGlobal("fetch", fetchMock);

    await authGet("/accounts/private");

    expect(fetchMock.mock.calls[0][0]).toBe("/auth/refresh");
    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual({
      refresh_token: "refresh-token",
      username: "fulano",
    });
    expect(fetchMock.mock.calls[1][1].headers.Authorization).toBe("Bearer novo");
  });

  it("renews once and retries when a call comes back 401", async () => {
    setIdToken("velho", 3600);
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({}, 401))
      .mockResolvedValueOnce(jsonResponse({ id_token: "novo", expires_in: 3600 }))
      .mockResolvedValueOnce(jsonResponse({ username: "fulano" }));
    vi.stubGlobal("fetch", fetchMock);

    await expect(authGet("/accounts/private")).resolves.toEqual({ username: "fulano" });
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });

  it("clears the session and reports SESSION_EXPIRED when the retry is also 401", async () => {
    setIdToken("velho", 3600);
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({}, 401))
      .mockResolvedValueOnce(jsonResponse({ id_token: "novo", expires_in: 3600 }))
      .mockResolvedValueOnce(jsonResponse({}, 401));
    vi.stubGlobal("fetch", fetchMock);

    await expect(authGet("/accounts/private")).rejects.toMatchObject({
      status: 401,
      message: SESSION_EXPIRED,
    });
    // A fresh token was refused too: the session is gone, not just the token.
    expect(readSession()).toBeNull();
  });

  it("gives up and clears the session when the refresh itself is rejected", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({}, 401));
    vi.stubGlobal("fetch", fetchMock);

    await expect(authGet("/accounts/private")).rejects.toMatchObject({
      status: 401,
      message: SESSION_EXPIRED,
    });
    // 30 days elapsed: there is nothing left to renew with.
    expect(readSession()).toBeNull();
  });

  it("renews only once for concurrent callers", async () => {
    // Several views mount at the same time. Without a shared promise this
    // would fire one refresh per view.
    const fetchMock = vi.fn().mockImplementation((url: string) => {
      if (url === "/auth/refresh") {
        return Promise.resolve(jsonResponse({ id_token: "novo", expires_in: 3600 }));
      }
      return Promise.resolve(jsonResponse([]));
    });
    vi.stubGlobal("fetch", fetchMock);

    await Promise.all([
      authGet("/accounts/private"),
      authPost("/things/private", {}),
      authGet("/data/stats/private"),
    ]);

    const refreshes = fetchMock.mock.calls.filter(([url]) => url === "/auth/refresh");
    expect(refreshes).toHaveLength(1);
  });
});
