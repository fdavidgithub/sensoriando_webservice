import { beforeEach, describe, expect, it, vi } from "vitest";

import { clearSession, readSession, writeSession } from "./session";

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
});

describe("session", () => {
  it("starts with no session", () => {
    expect(readSession()).toBeNull();
  });

  it("returns the session that was written", () => {
    writeSession("visitante");
    expect(readSession()).toEqual({ username: "visitante" });
  });

  it("clears the session", () => {
    writeSession("visitante");
    clearSession();
    expect(readSession()).toBeNull();
  });

  it("treats a corrupted entry as no session instead of crashing", () => {
    localStorage.setItem("sensoriando.session", "{not json");
    expect(readSession()).toBeNull();
  });

  it("treats an entry without a username as no session", () => {
    localStorage.setItem("sensoriando.session", JSON.stringify({ other: 1 }));
    expect(readSession()).toBeNull();
  });
});
