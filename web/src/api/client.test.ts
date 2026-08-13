import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, apiGet, apiPost } from "./client";

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
});
