import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  clearIdToken,
  clearSession,
  getIdToken,
  readRefreshToken,
  readSession,
  setIdToken,
  writeSession,
} from "./session";

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

beforeEach(() => {
  vi.stubGlobal("localStorage", memoryStorage());
  clearIdToken();
});

describe("session", () => {
  it("starts with no session", () => {
    expect(readSession()).toBeNull();
  });

  it("returns the session that was written", () => {
    writeSession("fulano", "refresh-token");
    expect(readSession()).toEqual({ username: "fulano" });
    expect(readRefreshToken()).toBe("refresh-token");
  });

  it("clears both the session and the token in memory", () => {
    writeSession("fulano", "refresh-token");
    setIdToken("id-token", 3600);

    clearSession();

    expect(readSession()).toBeNull();
    expect(getIdToken()).toBeNull();
  });

  it("treats a corrupted entry as no session instead of crashing", () => {
    localStorage.setItem("sensoriando.session", "{not json");
    expect(readSession()).toBeNull();
  });

  it("rejects a session left by the old convenience gate", () => {
    // It carried a username and no refresh token: it never authenticated
    // anyone, so it must not be honoured as a session now.
    localStorage.setItem("sensoriando.session", JSON.stringify({ username: "visitante" }));
    expect(readSession()).toBeNull();
  });
});

describe("the id token", () => {
  it("never reaches localStorage", () => {
    writeSession("fulano", "refresh-token");
    setIdToken("id-token", 3600);

    const stored = localStorage.getItem("sensoriando.session") ?? "";
    expect(stored).not.toContain("id-token");
    expect(getIdToken()).toBe("id-token");
  });

  it("is treated as absent once it is close to expiring", () => {
    setIdToken("id-token", 30);
    expect(getIdToken()).toBeNull();
  });

  it("is dropped by clearIdToken", () => {
    setIdToken("id-token", 3600);
    clearIdToken();
    expect(getIdToken()).toBeNull();
  });
});
