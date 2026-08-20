import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  readChartType,
  readPeriod,
  readPreferredUnit,
  writeChartType,
  writePeriod,
  writePreferredUnit,
} from "./prefs";

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

describe("preferred unit", () => {
  it("has none until one is chosen", () => {
    expect(readPreferredUnit(3)).toBeNull();
  });

  it("returns the unit that was chosen for that sensor", () => {
    writePreferredUnit(3, 7);
    writePreferredUnit(4, 9);

    expect(readPreferredUnit(3)).toBe(7);
    expect(readPreferredUnit(4)).toBe(9);
  });

  it("treats a corrupted entry as no preference", () => {
    localStorage.setItem("unit3", "nem numero");
    expect(readPreferredUnit(3)).toBeNull();
  });
});
