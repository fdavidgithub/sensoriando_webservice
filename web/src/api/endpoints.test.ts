import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { setIdToken, writeSession } from "../auth/session";
import {
  confirmSignUp,
  listSensors,
  listSensorUnits,
  login,
  savePrivateAccount,
  signUp,
  verifyOtp,
} from "./endpoints";

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

  it("passes a successful response straight through once the route exists", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(respond([{ id: 1, id_sensor: 1, name: "Celsius", initial: "C", precision: 2, isdefault: true }])),
    );

    await expect(listSensorUnits()).resolves.toHaveLength(1);
  });
});

describe("identity endpoints", () => {
  it("posts the registration without a password", async () => {
    const fetchMock = vi.fn().mockResolvedValue(respond({ destination: "f***@e***.com" }));
    vi.stubGlobal("fetch", fetchMock);

    await signUp({
      username: "fulano",
      name: "Fulano de Tal",
      email: "fulano@example.com",
      city: "Ribeirão Preto",
      state: "SP",
      country: "BR",
    });

    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("/accounts");
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body)).not.toHaveProperty("password");
  });

  it("confirms the registration by username and code", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      respond({ username: "fulano", id_token: "id", refresh_token: "r", expires_in: 3600 }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(confirmSignUp({ username: "fulano", code: "123456" })).resolves.toMatchObject({
      id_token: "id",
    });
    expect(fetchMock.mock.calls[0][0]).toBe("/accounts/confirm");
  });

  it("starts a sign-in with the e-mail alone", async () => {
    const fetchMock = vi.fn().mockResolvedValue(respond({ session: "s", destination: "d" }));
    vi.stubGlobal("fetch", fetchMock);

    await login({ email: "fulano@example.com" });

    expect(fetchMock.mock.calls[0][0]).toBe("/auth/login");
    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual({
      email: "fulano@example.com",
    });
  });

  it("answers the challenge with the code and the session", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      respond({ username: "fulano", id_token: "id", refresh_token: "r", expires_in: 3600 }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await verifyOtp({ email: "fulano@example.com", code: "123456", session: "s" });

    expect(fetchMock.mock.calls[0][0]).toBe("/auth/verify");
  });

  it("normalizes the phone to E.164 before signing up", async () => {
    // A phone with no country code is what Cognito rejected with
    // "Invalid phone number format." -- this is the field the form leaves
    // unformatted, so it is normalized here rather than trusted as typed.
    const fetchMock = vi.fn().mockResolvedValue(respond({ destination: "d" }));
    vi.stubGlobal("fetch", fetchMock);

    await signUp({
      username: "fulano",
      name: "Fulano de Tal",
      email: "fulano@example.com",
      phone: "(16) 99999-1234",
      city: "Ribeirão Preto",
      state: "SP",
      country: "BR",
    });

    expect(JSON.parse(fetchMock.mock.calls[0][1].body).phone).toBe("+5516999991234");
  });
});

describe("saving the profile", () => {
  beforeEach(() => {
    vi.stubGlobal("localStorage", memoryStorage());
    writeSession("fulano", "refresh-token");
    setIdToken("id-token", 3600);
  });

  it("normalizes the phone to E.164 before saving", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
    vi.stubGlobal("fetch", fetchMock);

    await savePrivateAccount({
      name: "Fulano de Tal",
      phone: "16999991234",
      city: "Ribeirão Preto",
      state: "SP",
      country: "BR",
    });

    expect(JSON.parse(fetchMock.mock.calls[0][1].body).phone).toBe("+5516999991234");
  });

  it("leaves no phone as no phone", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
    vi.stubGlobal("fetch", fetchMock);

    await savePrivateAccount({
      name: "Fulano de Tal",
      phone: "",
      city: "Ribeirão Preto",
      state: "SP",
      country: "BR",
    });

    expect(JSON.parse(fetchMock.mock.calls[0][1].body).phone).toBe("");
  });
});
