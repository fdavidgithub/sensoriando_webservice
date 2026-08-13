import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "./client";
import { PENDING_MESSAGE, listSensors, listSensorUnits, readPrivateAccount } from "./endpoints";

afterEach(() => {
  vi.unstubAllGlobals();
});

function respond(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("existing endpoints", () => {
  it("listSensors calls GET /sensors", async () => {
    const fetchMock = vi.fn().mockResolvedValue(respond([{ id: 1, name: "temp" }]));
    vi.stubGlobal("fetch", fetchMock);

    await expect(listSensors()).resolves.toEqual([{ id: 1, name: "temp" }]);
    expect(fetchMock.mock.calls[0][0]).toBe("/sensors");
  });
});

describe("pending endpoints", () => {
  it("turns a 404 into the pending message", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(respond({}, 404)));

    await expect(listSensorUnits()).rejects.toMatchObject({
      status: 404,
      message: PENDING_MESSAGE,
    });
  });

  it("leaves other failures untouched", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(respond({}, 500)));

    const error = await readPrivateAccount().catch((caught: unknown) => caught);

    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).status).toBe(500);
    expect((error as ApiError).message).not.toBe(PENDING_MESSAGE);
  });

  it("passes a successful response straight through once the route exists", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(respond([{ id: 1, id_sensor: 1, name: "Celsius", initial: "C", precision: 2, isdefault: true }])),
    );

    await expect(listSensorUnits()).resolves.toHaveLength(1);
  });
});
