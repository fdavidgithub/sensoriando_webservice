import { beforeEach, describe, expect, it, vi } from "vitest";

import { readChartType, readPeriod, writeChartType, writePeriod } from "./prefs";

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

describe("readPeriod", () => {
  it("defaults to second when nothing is stored", () => {
    expect(readPeriod()).toBe("second");
  });

  it("returns what was written", () => {
    writePeriod("month");
    expect(readPeriod()).toBe("month");
  });

  it("falls back to the default when the stored value is not a period", () => {
    localStorage.setItem("chartview", "fortnight");
    expect(readPeriod()).toBe("second");
  });
});

describe("readChartType", () => {
  it("defaults to line when nothing is stored", () => {
    expect(readChartType(7)).toBe("line");
  });

  it("keeps one value per sensor", () => {
    writeChartType(7, "bar");
    writeChartType(9, "table");

    expect(readChartType(7)).toBe("bar");
    expect(readChartType(9)).toBe("table");
    expect(readChartType(11)).toBe("line");
  });

  it("uses the same key Django used, so a returning user keeps the setting", () => {
    writeChartType(7, "bar");
    expect(localStorage.getItem("chart7")).toBe("bar");
  });

  it("falls back to the default when the stored value is not a chart type", () => {
    localStorage.setItem("chart7", "pie");
    expect(readChartType(7)).toBe("line");
  });
});
